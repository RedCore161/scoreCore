from rest_framework import viewsets
from rest_framework.decorators import permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from scoring.helper import build_abs_path
from scoring.models import Project, ImageFile, ImageScore
from scoring.serializers import ProjectSerializer, ImageFileSerializer, ImageScoreSerializer
from scoring.views.viewsets.base_viewset import StandardResultsSetPagination
from scoring.views.viewsets.viewset_creator import ViewSetCreateModel
from server.views import RequestSuccess, RequestFailed


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    @action(detail=False, url_path="list", methods=["GET"])
    def list_projects(self, request):
        serializer = ProjectSerializer(Project.objects.filter(users=request.user), context={"user": request.user.pk},
                                       many=True)
        return Response(serializer.data)

    @action(detail=True, url_path="recalculate-varianz", methods=["GET"])
    def recalculate_varianz(self, request, pk):
        images = ImageFile.objects.filter(project=pk, useless=False, hidden=False)
        for image in images:
            image.calc_varianz()
        return RequestSuccess()

    @action(detail=True, url_path="image", methods=["GET"])
    def get_next_image(self, request, pk):
        _project = Project.objects.get(pk=pk)
        qs = ImageScore.objects.filter(project=pk, user=request.user).order_by("-pk")
        serializer = ImageScoreSerializer(qs, many=True, read_only=True)
        if not _project.is_finished():
            data = ViewSetCreateModel.get_next_image(pk, request.user, request.GET.get("file"))
            data.update({"history": serializer.data})
        return RequestSuccess({"is_finished": True, "files_left": 0, "history": serializer.data})

    @action(detail=True, url_path="images/all", methods=["GET"])
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
            response.update_data({"project": project.name,
                                  "usersCount": len(project.users.all()),
                                  "scoresCount": project.get_score_count()})
            return response

        return RequestFailed()

    @action(detail=True, url_path="get-useless", methods=["GET"], permission_classes=[IsAdminUser])
    def get_useless_image_files(self, request, pk):
        images = ImageFile.objects.filter(project=pk, useless=True, hidden=False)
        serializer = ImageFileSerializer(images, many=True)
        return Response(serializer.data)

    @action(detail=True, url_path="read-images", methods=["GET"], permission_classes=[IsAdminUser])
    def read_images(self, request, pk):
        project = Project.objects.get(pk=pk)
        if not project.image_dir:
            return RequestFailed({"reason": f"No 'image-dir' on project '{project}'!"})

        project.read_images()

        return RequestSuccess()

    @action(detail=True, url_path="scores", methods=["GET"], permission_classes=[IsAdminUser])
    def get_scores(self, request, pk):
        images = ImageScore.objects.filter(project=pk).exclude(file__useless=True)
        serializer = ImageScoreSerializer(images, many=True)
        return Response(serializer.data)

    @action(detail=True, url_path="evaluations", methods=["POST"], permission_classes=[IsAdminUser])
    def evaluate(self, request, pk):
        files = ImageFile.objects.filter(project=pk).exclude(useless=True).exclude(scores__isnull=True)
        serializer = ImageFileSerializer(files, many=True)

        project = Project.objects.get(pk=pk)

        project_serializer = ProjectSerializer(project)
        project.evaluate_data({"imagefiles": serializer.data,
                               "project": project_serializer.data})

        return RequestSuccess(project.get_existing_evaluations())

    @action(detail=True, url_path="export/xlsx", methods=["POST"], permission_classes=[IsAdminUser])
    def export_as_xlsx(self, request, pk):
        files = ImageFile.objects.filter(project=pk).exclude(useless=True).exclude(scores__isnull=True)
        serializer = ImageFileSerializer(files, many=True)

        project = Project.objects.get(pk=pk)

        project_serializer = ProjectSerializer(project)
        project.evaluate_data_as_xlsx({"project": project_serializer.data,
                                       "imagefiles": serializer.data
                                       })

        return RequestSuccess(project.get_existing_evaluations())

    @action(detail=True, url_path="investigate", methods=["GET"], permission_classes=[IsAdminUser])
    def investigate(self, request, pk):

        project = Project.objects.get(pk=pk)
        project_serializer = ProjectSerializer(project)

        files = project.get_all_files_save()

        scores_count = {}
        for _file in files:
            value = len(_file.get_scores_save(_file.project))

            if value in scores_count:
                element = scores_count.get(value)
            else:
                element = []

            element.append({"id": _file.id,
                            "path": _file.get_rel_path(),
                            "filename": _file.filename,
                            "users": _file.get_scored_users(),
                            })

            scores_count.update({value: element})

        scores_per_user = {}
        for user in project.users.all():
            scores_per_user.update({user.username: ImageScore.objects.filter(project=pk, user=user.id)
                                                                     .exclude(file__useless=True).count()
                                    })

        return RequestSuccess({"project": project_serializer.data,
                               "imageFilesCount": files.count(),
                               "scoresCount": scores_count,
                               "scoresPerUser": scores_per_user,
                               })

    @action(detail=True, url_path="fix/useless", methods=["GET"], permission_classes=[IsAdminUser])
    def fix_useless_images(self, request, pk):
        project = Project.objects.get(pk=pk)
        images = ImageFile.objects.filter(project=pk, useless=True, hidden=False)

        for image in images:
            index = image.path.index("media") + 6
            _path = image.path[index:]
            project.parse_info_file(build_abs_path([_path]))
        return RequestSuccess()
