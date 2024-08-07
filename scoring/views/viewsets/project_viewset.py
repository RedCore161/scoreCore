import os

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from scoring.basics import parse_int
from scoring.excel import data_to_image
from scoring.helper import build_abs_path, get_path_projects, count_images_in_folder, get_rel_path, get_fields_from_bit, \
    dlog, get_project_evaluation_dir, delete_file
from scoring.models import Project, ImageFile, ImageScore, ScoreFeature
from scoring.serializers import ProjectSerializer, ImageFileSerializer, ImageScoreSerializer, ScoreFeaturesSerializer
from scoring.views.viewsets.base_viewset import StandardResultsSetPagination, BasisViewSet
from scoring.views.viewsets.viewset_creator import ViewSetCreateModel
from server.views import RequestSuccess, RequestFailed
import numpy as np

DUMPING_MAX_SCORE = .9


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    @action(detail=False, url_path="list", methods=["GET"])
    def list_projects(self, request):
        ser = ProjectSerializer(Project.objects.filter(users=request.user), context={"user": request.user.pk}, many=True)
        return Response(ser.data)

    @action(detail=True, url_path="cross-stddev-all", methods=["GET"], permission_classes=[IsAdminUser])
    def cross_std_dev_all(self, request, pk):
        images = ImageFile.objects.filter(project=pk, useless=False, hidden=False)
        project = Project.objects.get(pk=pk)
        _user = request.user
        users = project.get_scoring_users(_exclude=_user)
        cx = len(images)
        cy = len(users)

        matrix = np.zeros((cx, cy))
        for y, image in enumerate(images):
            for x, a in enumerate(users):
                if _user.pk == a.pk:
                    continue
                matrix[y, x] = image.calc_std_dev(False, users=[a, _user])

        column_sums = np.sum(matrix, axis=0)

        # Add the sums as a new row to the matrix
        matrix = np.vstack([matrix, column_sums])

        y_axis = [img.filename for img in images] + ["Sum"]
        x_axis = [usr.username[:3] for usr in users]

        score, fts = project.get_max_score()
        max_score = score / (fts * DUMPING_MAX_SCORE)

        buf = data_to_image(matrix, f'Heatmap for "{project.name}" and "{_user}"',
                            max_score=max_score, x_axis=x_axis, y_axis=y_axis, y_label="Images")

        return HttpResponse(buf, content_type="image/png")

    @action(detail=True, url_path="cross-stddev", methods=["GET"], permission_classes=[IsAdminUser])
    def cross_stddev(self, request, pk):
        file_id = request.GET.get("file_id")
        if file_id:
            images = ImageFile.objects.filter(pk=file_id)
        else:
            images = ImageFile.objects.filter(project=pk, useless=False, hidden=False)

        project = Project.objects.get(pk=pk)
        users = project.get_scoring_users()
        count = len(users)

        matrix = np.zeros((count, count))
        file_name = "Error"
        for image in images:
            file_name = image.filename
            for x, a in enumerate(users):
                for y, b in enumerate(users):
                    if b.pk >= a.pk:
                        continue
                    matrix[x, y] = matrix[y, x] = image.calc_std_dev(False, users=[a, b])
            break

        score, fts = project.get_max_score()
        max_score = score / (fts * DUMPING_MAX_SCORE)

        axis = [usr.username[:3] for usr in users]
        title = f'Heatmap for Scores on image "{file_name}"'
        buf = data_to_image(matrix, title, max_score=max_score, x_axis=axis, y_axis=axis)

        return HttpResponse(buf, content_type="image/png")

    @action(detail=True, url_path="recalculate-stddev", methods=["GET"], permission_classes=[IsAdminUser])
    def recalculate_stddev(self, request, pk):
        images = ImageFile.objects.filter(project=pk, useless=False, hidden=False)
        for image in images:
            image.calc_std_dev()
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
        response = BasisViewSet.base_upload_file(request, *args, **kwargs)
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
            .order_by("-stddev")

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

    @action(detail=True, url_path="export/clear", methods=["POST"], permission_classes=[IsAdminUser])
    def clear_xlsx_files(self, request, pk):
        project = Project.objects.get(pk=pk)
        _path = get_project_evaluation_dir(str(project.pk))

        for _file in os.listdir(_path):
            delete_file(os.path.join(_path, _file), True)

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
