from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from scoring.helper import build_abs_path
from scoring.models import Project, ImageFile, ImageScore
from scoring.serializers import ImageScoreSerializer
from scoring.views.viewsets.base_viewset import StandardResultsSetPagination
from scoring.views.viewsets.project_viewset import ProjectViewSet
from scoring.views.viewsets.viewset_creator import ViewSetCreateModel
from server.views import RequestSuccess


class ImageScoreViewSet(viewsets.ModelViewSet):
    serializer_class = ImageScoreSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return ImageScore.objects.all()

    @action(detail=True, url_path="confirm", methods=["POST"])
    def confirm_image(self, request, pk):

        def replace_none(_str):
            if _str == "X":
                return None
            return _str

        eye = replace_none(request.data.get("eye"))
        nose = replace_none(request.data.get("nose"))
        cheek = replace_none(request.data.get("cheek"))
        ear = replace_none(request.data.get("ear"))
        whiskers = replace_none(request.data.get("whiskers"))
        comment = request.data.get("comment", "")
        project = request.data.get("project")

        ViewSetCreateModel().create_imagescore(pk, request.user, eye, nose, cheek, ear, whiskers, comment)

        return ProjectViewSet().get_next_image(request, project)

    @action(detail=True, url_path="useless", methods=["POST"])
    def mark_as_useless(self, request, pk):
        image_file_old = ImageFile.objects.get(pk=pk)
        image_file_old.useless = True
        image_file_old.save()

        project = int(request.data.get("project"))
        _project = Project.objects.get(pk=project)

        # Load new Imagefile
        _project.parse_info_file(build_abs_path([image_file_old.path]))

        return ProjectViewSet().get_next_image(request, project)

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