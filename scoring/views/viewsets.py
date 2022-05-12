import os
import random
import re

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action

from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
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

def parse_info_file(project, _path, get_or_create_amount=2):

    regex = re.compile("^\d{5}\.png")
    _path = os.path.join(_path, "infofile.txt")
    if os.path.exists(_path):
        with open(_path, 'r') as f:
            lines = f.readlines()
            images = lines[3:]

            for img in images:

                if not regex.match(img):
                    break

                if get_or_create_amount == 0:
                    return True

                _file = img.rstrip("\n")

                image_file, created = ImageFile.objects.get_or_create(project=project,
                                                                      filename=_file,
                                                                      path=_path)

                if created:
                    print("Created IMAGEFILE", _file, get_or_create_amount, _path)
                    image_file.order = random.randint(0, 5000000)
                    image_file.date = timezone.now()
                    image_file.save()
                    get_or_create_amount -= 1

                else:
                    if not image_file.useless and not image_file.hidden:
                        print("Existing IMAGEFILE", _file, get_or_create_amount, _path)
                        get_or_create_amount -= 1
    return False


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]

    @action(detail=False, url_path="list", methods=["GET"])
    def list_projects(self, request):
        serializer = ProjectSerializer(Project.objects.filter(users=request.user), context={"user": request.user.pk},
                                       many=True)
        return Response(serializer.data)

    @action(detail=True, url_path="images", methods=["GET"])
    def get_images(self, request, pk):

        images = ImageFile.objects.filter(project=pk)\
                                  .exclude(useless=True) \
                                  .exclude(hidden=True) \
                                  .exclude(scores__user=request.user).order_by("order")
        serializer = ImageFileSerializer(images, many=True)
        return Response(serializer.data)

    @action(detail=True, url_path="get-useless", methods=["GET"])
    def get_useless_image_files(self, request, pk):
        images = ImageFile.objects.filter(project=pk, useless=True, hidden=False).order_by("order")
        serializer = ImageFileSerializer(images, many=True)
        return Response(serializer.data)

    @action(detail=True, url_path="read-images", methods=["GET"])
    def read_images(self, request, pk):

        project = Project.objects.get(pk=pk)
        if not project.image_dir:
            return RequestFailed({"reason": f"No 'image-dir' on project '{project}'!"})

        _path = os.path.join(get_media_path(), project.image_dir)

        for root, _, files in os.walk(_path):
            if len(files):
                for _file in files:
                    if _file[-4:] == ".txt":    # TODO check file-type
                        parse_info_file(project, os.path.join(BASE_DIR, root))

        return RequestSuccess()

    @action(detail=True, url_path="scores", methods=["GET"])
    def get_scores(self, request, pk):
        images = ImageScore.objects.filter(project=pk).exclude(file__useless=True)
        serializer = ImageScoreSerializer(images, many=True)
        return Response(serializer.data)

    @action(detail=True, url_path="evaluate", methods=["GET"])
    def evaluate(self, request, pk):
        files = ImageFile.objects.filter(project=pk).exclude(useless=True)
        serializer = ImageFileSerializer(files, many=True)
        return Response(serializer.data)


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

        return RequestSuccess()

    @action(detail=True, url_path="useless", methods=["POST"])
    def mark_as_useless(self, request, pk):

        image_file_old = ImageFile.objects.get(pk=pk)
        image_file_old.useless = True
        image_file_old.save()

        project = int(request.data.get("project"))
        _project = Project.objects.get(pk=project)

        # Load new Imagefile
        result = parse_info_file(_project, build_abs_path([image_file_old.path]))
        if result:
            return RequestSuccess()
        return RequestFailed()

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
