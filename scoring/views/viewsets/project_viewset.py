import os

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from scoring.basics import parse_int, parse_boolean
from scoring.helper import build_abs_path, get_path_projects, count_images_in_folder, get_rel_path, get_fields_from_bit, \
    dlog
from scoring.models import Project, ImageFile, ImageScore, ScoreFeature
from scoring.serializers import ProjectSerializer, ImageFileSerializer, ImageScoreSerializer, ScoreFeaturesSerializer
from scoring.views.viewsets.base_viewset import StandardResultsSetPagination, BasisViewSet
from scoring.views.viewsets.viewset_creator import ViewSetCreateModel
from server.views import RequestSuccess, RequestFailed


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    @action(detail=False, url_path="list", methods=["GET"])
    def list_projects(self, request):
        serializer = ProjectSerializer(Project.objects.filter(users=request.user),
                                                              context={"user": request.user.pk}, many=True)
        return Response(serializer.data)

    @action(detail=True, url_path="recalculate-variance", methods=["GET"])
    def recalculate_variance(self, request, pk):
        images = ImageFile.objects.filter(project=pk, useless=False, hidden=False)
        for image in images:
            image.calc_variance()
        return RequestSuccess()

    @action(detail=False, url_path="available", methods=["GET"])
    def get_available_folders(self, request):
        project_dir = get_path_projects()
        folders = os.listdir(project_dir)
        data = []

        for d in folders:
            _path = os.path.join(project_dir, d)
            _rel_path = get_rel_path(_path).replace("\\", "/")
            _in_use = Project.objects.filter(users=request.user, image_dir=_rel_path).count()
            count = count_images_in_folder(_path)
            data.append({"name": d,
                         "images": count,
                         "in_use": _in_use > 0})

        return RequestSuccess({"data": data})

    @action(detail=False, url_path="create", methods=["POST"], permission_classes=[IsAdminUser])
    def create_new_project(self, request):

        name = request.data.get("name")
        icon = request.data.get("icon")
        folder = request.data.get("folder")
        features = request.data.get("features", "").split(",")

        project, created = Project.objects.get_or_create(name=name)

        if not created:
            return RequestFailed({"reason": "Project with this name already exists..."})

        if folder:
            project.image_dir = folder
        project.icon = icon
        project.users.add(request.user)
        project.save()

        bit = 1
        for _feature in features:
            feature, created = ScoreFeature.objects.get_or_create(project=project, name=_feature.strip())
            feature.bit = bit
            feature.save()
            bit *= 2

        project.read_images(False)
        serializer = self.get_serializer(project, read_only=True)

        return RequestSuccess({"model": serializer.data})

    @action(detail=False, url_path="upload", methods=["POST"], permission_classes=[IsAdminUser])
    def upload_images(self, request, *args, **kwargs):
        project_name = request.data.get("projectName")
        response = BasisViewSet.base_upload_file(request, project_name, *args, **kwargs)
        return RequestSuccess(response)

    @action(detail=True, url_path="image", methods=["GET"])
    def get_next_image(self, request, pk):
        _project = Project.objects.get(pk=pk)
        _fields = parse_int(request.GET.get("fields", 0))

        bits = get_fields_from_bit(_fields)
        scoring_fields = _project.features.all()
        _index = 0
        _filter = {}
        for bit in bits:
            if bit:
                # print(f"{_index=} => {scoring_fields[_index]=}")
                _filter.update({f"{scoring_fields[_index]}__isnull": False})
            _index += 1
        dlog(f"{_filter=}, {bits=}")

        qs = ImageScore.objects.filter(project=pk, user=request.user, **_filter).order_by("-pk")
        serializer_scores = ImageScoreSerializer(qs, many=True, read_only=True)
        serializer_features = ScoreFeaturesSerializer(_project.features.all(), many=True, read_only=True)

        if not _project.is_finished():
            data = ViewSetCreateModel.get_next_image(request, pk)
            data.update({"features": serializer_features.data,
                         "history": serializer_scores.data})
            return RequestSuccess(data)
        return RequestSuccess({"is_finished": True, "files_left": 0,
                               "history": serializer_scores.data})

    @action(detail=True, url_path="images/all", methods=["GET"])
    def get_images_all(self, request, pk):
        project = Project.objects.get(pk=pk)

        images = ImageFile.objects.filter(project=pk) \
            .exclude(hidden=True) \
            .exclude(useless=True) \
            .order_by("-variance")

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
