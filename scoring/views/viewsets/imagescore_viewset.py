import os

from loguru import logger
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from scoring.helper import build_abs_path, set_logging_file
from scoring.models import Project, ImageFile, ImageScore
from scoring.serializers import ImageScoreSerializer
from scoring.views.viewsets.base_viewset import StandardResultsSetPagination
from scoring.views.viewsets.project_viewset import ProjectViewSet
from scoring.views.viewsets.viewset_creator import ViewSetCreateModel
from server.views import RequestSuccess, RequestFailed


class ImageScoreViewSet(viewsets.ModelViewSet):
    serializer_class = ImageScoreSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return ImageScore.objects.all()

    @action(detail=True, url_path="confirm", methods=["POST"])
    def confirm_image(self, request, pk):
        eye = request.data.get("eye")
        nose = request.data.get("nose")
        cheek = request.data.get("cheek")
        ear = request.data.get("ear")
        whiskers = request.data.get("whiskers")
        comment = request.data.get("comment", "")
        project = request.data.get("project")

        _project = Project.objects.get(pk=project)

        if not _project.is_finished():
            success = ViewSetCreateModel().create_or_update_imagescore(pk, request.user, [eye, nose, cheek, ear, whiskers], comment)
            if success:
                return ProjectViewSet().get_next_image(request, project)
            return RequestFailed({"already_scored": True})
        return RequestFailed({"is_finished": True})

    @action(detail=True, url_path="useless", methods=["POST"])
    def mark_as_useless(self, request, pk):

        project = int(request.data.get("project"))
        _project = Project.objects.get(pk=project)

        if not _project.is_finished():
            set_logging_file()
            image_file_old = ImageFile.objects.get(pk=pk)
            image_file_old.useless = True
            image_file_old.save()
            logger.info(f"Marked useless ImageFile: {os.path.join(image_file_old.path, image_file_old.filename)}")

            # Load new Imagefile
            index = image_file_old.path.index("media") + 6
            _path = image_file_old.path[index:]
            _project.parse_info_file(build_abs_path([_path]))

            return ProjectViewSet().get_next_image(request, project)
        return RequestFailed({"is_finished": True})

    @action(detail=True, url_path="hide", methods=["POST"])
    def hide_useless(self, request, pk):
        image_file = ImageFile.objects.get(pk=pk)
        image_file.hidden = True
        image_file.save()

        return RequestSuccess()

    @action(detail=True, url_path="restore", methods=["POST"])
    def restore(self, request, pk):
        image_file = ImageFile.objects.get(pk=pk)
        image_file.useless = False
        image_file.save()

        return RequestSuccess()
