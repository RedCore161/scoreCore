import os
import random
import re

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action, permission_classes

from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from scoring.helper import get_media_path, build_abs_path
from scoring.models import Project, ImageScore, ImageFile
from scoring.serializers import ProjectSerializer, ImageScoreSerializer, ImageFileSerializer
from server.settings import BASE_DIR
from server.views import RequestSuccess, RequestFailed




class StandardResultsSetPagination(PageNumberPagination):
    page_size = 500
    page_size_query_param = "page_size"
    max_page_size = 500

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "pages": self.page.paginator.num_pages,
            "elements": data
        })


# ######################################################################################################################

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    @action(detail=False, url_path="list", methods=["GET"])
    @permission_classes([IsAuthenticated])
    def list_projects(self, request):
        serializer = ProjectSerializer(Project.objects.filter(users=request.user), context={"user": request.user.pk},
                                       many=True)
        return Response(serializer.data)

    @action(detail=True, url_path="images", methods=["GET"])
    @permission_classes([IsAuthenticated])
    def get_images(self, request, pk):

        images = ImageFile.objects.filter(project=pk)\
                                  .exclude(useless=True) \
                                  .exclude(hidden=True) \
                                  .exclude(scores__user=request.user).order_by("order")
        serializer = ImageFileSerializer(images, many=True)
        return Response(serializer.data)

    @action(detail=True, url_path="get-useless", methods=["GET"])
    @permission_classes([IsAdminUser])
    def get_useless_image_files(self, request, pk):
        images = ImageFile.objects.filter(project=pk, useless=True, hidden=False).order_by("order")
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
    @action(detail=True, url_path="evaluate", methods=["POST"])
    def evaluate(self, request, pk):
        files = ImageFile.objects.filter(project=pk).exclude(useless=True)
        serializer = ImageFileSerializer(files, many=True)

        project = Project.objects.get(pk=pk)

        project_serializer = ProjectSerializer(project)
        project.evaluate_data({"imagefiles": serializer.data,
                               "project": project_serializer.data})

        return RequestSuccess(project.get_existing_evaluations())


class ImageScoreViewSet(viewsets.ModelViewSet):
    serializer_class = ImageScoreSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def replaceNoneValue(self, str):
        if str == "X":
            return None
        return str

    def get_queryset(self):
        return ImageScore.objects.all()

    @action(detail=True, url_path="confirm", methods=["POST"])
    def confirm_image(self, request, pk):

        eye = self.replaceNoneValue(request.data.get("eye"))
        nose = self.replaceNoneValue(request.data.get("nose"))
        cheek = self.replaceNoneValue(request.data.get("cheek"))
        ear = self.replaceNoneValue(request.data.get("ear"))
        whiskas = self.replaceNoneValue(request.data.get("whiskas"))

        image_file = ImageFile.objects.get(pk=pk)

        score = ImageScore.objects.create(user=request.user,
                                          project=image_file.project,
                                          file=image_file,
                                          s_eye=eye,
                                          s_nose=nose,
                                          s_cheek=cheek,
                                          s_ear=ear,
                                          s_whiskas=whiskas,
                                          date=timezone.now())
        score.save()

        image_file.calc_kappa()

        return RequestSuccess()

    @action(detail=True, url_path="useless", methods=["POST"])
    def mark_as_useless(self, request, pk):

        image_file_old = ImageFile.objects.get(pk=pk)
        image_file_old.useless = True
        image_file_old.save()

        project = int(request.data.get("project"))
        _project = Project.objects.get(pk=project)

        # Load new Imagefile
        result = _project.parse_info_file(build_abs_path([image_file_old.path]))
        return RequestSuccess()
        # if result:
        #     return RequestSuccess()
        # return RequestFailed()

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


# ######################################################################################################################

# ######################################################################################################################
# ##########  H E L P E R  #############################################################################################
# ######################################################################################################################


class EmptyViewSet(viewsets.ModelViewSet):
    queryset = None

    @action(detail=False, url_path="empty", methods=["GET"])
    def empty(self, request=None):
        return RequestFailed()
