from rest_framework import viewsets
from rest_framework.decorators import permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from scoring.models import Project, ImageFile, ImageScore
from scoring.serializers import ProjectSerializer, ImageFileSerializer, ImageScoreSerializer
from scoring.views.viewsets.base_viewset import StandardResultsSetPagination
from scoring.views.viewsets.viewset_creator import ViewSetCreateModel
from server.views import RequestSuccess, RequestFailed


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    pagination_class = StandardResultsSetPagination

    @action(detail=False, url_path="list", methods=["GET"])
    @permission_classes([IsAuthenticated])
    def list_projects(self, request):
        serializer = ProjectSerializer(Project.objects.filter(users=request.user), context={"user": request.user.pk},
                                       many=True)
        return Response(serializer.data)

    @action(detail=True, url_path="recalculate-varianz", methods=["GET"])
    @permission_classes([IsAuthenticated])
    def recalculate_varianz(self, request, pk):
        images = ImageFile.objects.filter(project=pk, useless=False, hidden=False)
        for image in images:
            image.calc_varianz()
        return RequestSuccess()

    @action(detail=True, url_path="image", methods=["GET"])
    @permission_classes([IsAuthenticated])
    def get_next_image(self, request, pk):
        return ViewSetCreateModel.get_next_image(pk, request.user)

    @action(detail=True, url_path="images/all", methods=["GET"])
    @permission_classes([IsAuthenticated])
    def get_images_all(self, request, pk):
        project = Project.objects.get(pk=pk)

        images = ImageFile.objects.filter(project=pk) \
            .exclude(hidden=True) \
            .exclude(useless=True) \
            .order_by("-varianz")

        page = self.paginate_queryset(images)
        if page is not None:
            serializer = ImageFileSerializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.update_data({"project": project.name})
            return response

        return RequestFailed()

    @action(detail=True, url_path="get-useless", methods=["GET"])
    @permission_classes([IsAdminUser])
    def get_useless_image_files(self, request, pk):
        images = ImageFile.objects.filter(project=pk, useless=True, hidden=False)
        serializer = ImageFileSerializer(images, many=True)
        return Response(serializer.data)

    @action(detail=True, url_path="read-images", methods=["GET"])
    @permission_classes([IsAdminUser])
    def read_images(self, request, pk):
        project = Project.objects.get(pk=pk)
        if not project.image_dir:
            return RequestFailed({"reason": f"No 'image-dir' on project '{project}'!"})

        project.read_images()

        return RequestSuccess()

    @action(detail=True, url_path="scores", methods=["GET"])
    @permission_classes([IsAdminUser])
    def get_scores(self, request, pk):
        images = ImageScore.objects.filter(project=pk).exclude(file__useless=True)
        serializer = ImageScoreSerializer(images, many=True)
        return Response(serializer.data)

    @permission_classes([IsAdminUser])
    @action(detail=True, url_path="evaluations", methods=["POST"])
    def evaluate(self, request, pk):
        files = ImageFile.objects.filter(project=pk).exclude(useless=True).exclude(scores__isnull=True)
        serializer = ImageFileSerializer(files, many=True)

        project = Project.objects.get(pk=pk)

        project_serializer = ProjectSerializer(project)
        project.evaluate_data({"imagefiles": serializer.data,
                               "project": project_serializer.data})

        return RequestSuccess(project.get_existing_evaluations())

    @permission_classes([IsAdminUser])
    @action(detail=True, url_path="export/xlsx", methods=["POST"])
    def export_as_xlsx(self, request, pk):
        files = ImageFile.objects.filter(project=pk).exclude(useless=True).exclude(scores__isnull=True)
        serializer = ImageFileSerializer(files, many=True)

        project = Project.objects.get(pk=pk)

        project_serializer = ProjectSerializer(project)
        project.evaluate_data_as_xlsx({"imagefiles": serializer.data,
                                       "project": project_serializer.data})

        return RequestSuccess(project.get_existing_evaluations())
