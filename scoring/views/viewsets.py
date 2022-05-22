import os
import random

from django.db.models import Count
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action, permission_classes

from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from scoring.helper import build_abs_path, get_backup_path
from scoring.models import Project, ImageScore, ImageFile, Backup
from scoring.serializers import ProjectSerializer, ImageScoreSerializer, ImageFileSerializer, BackupSerializer
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
        project = Project.objects.get(pk=pk)

        base_request = ImageFile.objects.filter(project=pk) \
            .exclude(hidden=True) \
            .exclude(useless=True) \
            .exclude(scores__user=request.user) \
            .annotate(scores_min=Count('scores'))

        min_count = base_request.order_by("scores_min")[0].scores_min

        images = base_request.filter(scores_min=min_count)

        scored = ImageFile.objects.filter(project=pk, scores__user=request.user) \
            .exclude(hidden=True) \
            .exclude(useless=True).count()

        serializer = ImageFileSerializer(images, many=True)
        count = project.wanted_scores_per_user - scored

        if count == 0:
            return RequestSuccess({"files_left": count})

        if len(images):
            rnd = random.randint(0, len(images)-1)
            return RequestSuccess({"files_left": count, "image": serializer.data[rnd], "random": rnd})

        return RequestSuccess({"files_left": count})


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
        whiskers = self.replaceNoneValue(request.data.get("whiskers"))
        comment = request.data.get("comment", "")

        image_file = ImageFile.objects.get(pk=pk)

        score = ImageScore.objects.create(user=request.user,
                                          project=image_file.project,
                                          file=image_file,
                                          s_eye=eye,
                                          s_nose=nose,
                                          s_cheek=cheek,
                                          s_ear=ear,
                                          s_whiskers=whiskers,
                                          comment=comment,
                                          date=timezone.now())
        score.save()

        image_file.calc_similarity()

        return ProjectViewSet().get_images(request, image_file.project.pk)

    @action(detail=True, url_path="useless", methods=["POST"])
    def mark_as_useless(self, request, pk):
        image_file_old = ImageFile.objects.get(pk=pk)
        image_file_old.useless = True
        image_file_old.save()

        project = int(request.data.get("project"))
        _project = Project.objects.get(pk=project)

        # Load new Imagefile
        result = _project.parse_info_file(build_abs_path([image_file_old.path]))

        return ProjectViewSet().get_images(request, project)
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


class BackupViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    serializer_class = BackupSerializer
    queryset = Backup.objects.all()
    permission_classes = [IsAdminUser]

    @action(detail=False, url_path="readin", methods=["POST"])
    def read_backups(self, request):
        _files = os.listdir(get_backup_path())
        for _f in _files:
            try:
                Backup.objects.get(name=_f)
            except Backup.DoesNotExist:
                backup = Backup.objects.create(name=_f)
                backup.save()

        return RequestSuccess()

    # @action(detail=False, url_path="list", methods=["GET"])
    # @permission_classes([IsAdminUser])
    # def list_backups(self, request):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     page = self.paginate_queryset(queryset)
    #
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)


# ######################################################################################################################

# ######################################################################################################################
# ##########  H E L P E R  #############################################################################################
# ######################################################################################################################


class EmptyViewSet(viewsets.ModelViewSet):
    queryset = None

    @action(detail=False, url_path="empty", methods=["GET"])
    def empty(self, request=None):
        return RequestFailed()
