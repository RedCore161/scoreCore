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


def get_scores_from_request(request, fields) -> list:
    scores = []
    for feature in fields:
        name = request.data.get(feature)
        if name is not None:
            scores.append(name)
    return scores


class ImageScoreViewSet(viewsets.ModelViewSet):
    serializer_class = ImageScoreSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return ImageScore.objects.all()

    @action(detail=True, url_path="confirm", methods=["POST"])
    def confirm_image(self, request, pk):

        project = request.data.get("project")
        _project = Project.objects.get(pk=project)
        comment = request.data.get("comment", "")

        if not _project.is_finished():
            scoring_fields = _project.features.all().values_list("name", flat=True)
            scores = get_scores_from_request(request, scoring_fields)

            ViewSetCreateModel().create_or_update_imagescore(pk, request.user, scoring_fields, scores, comment)
            return ProjectViewSet().get_next_image(request, project)
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
