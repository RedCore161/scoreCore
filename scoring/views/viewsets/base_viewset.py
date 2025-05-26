import os

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView

from scoring.basics import parse_file_name, parse_int
from scoring.helper import dlog, save_check_dir, get_path_projects, is_video, is_image, get_path_videos, elog, okaylog
from scoring.serializers import RedcoreTokenObtainPairSerializer
from server.settings import DEFAULT_DIRS, MEDIA_ROOT
from server.views import RequestFailed, RequestSuccess


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "size"
    max_page_size = 500

    def get_paginated_response(self, data):

        return RequestSuccess({
            "count": self.page.paginator.count,
            "pages": self.page.paginator.num_pages,
            "per_page": self.page.paginator.per_page,
            "elements": data
        })


class ExtendedTokenObtainPairView(TokenObtainPairView):
    serializer_class = RedcoreTokenObtainPairSerializer

    def post(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        user = User.objects.get(username=request.data.get("username"))
        login(request, user)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class EmptyViewSet(viewsets.ModelViewSet):
    queryset = None

    @action(detail=False, url_path="empty", methods=["GET"])
    def empty(self, request=None):
        return RequestFailed()


class BasisViewSet:

    @staticmethod
    def base_upload_file(request, *args, **kwargs) -> dict:

        project_name = request.data.get("projectName")
        pos = parse_int(request.data.get("pos", 0))
        okaylog(pos, project_name, len(request.FILES))

        response = {}
        fs = FileSystemStorage(location=DEFAULT_DIRS.get("projects"))

        without_infofiles = False
        folder_counter = pos + 1
        files_count = 0

        for file in request.FILES:
            _file = request.FILES.get(file)
            if not _file:
                elog(f"Error with file {_file}")

            incr_count = False
            files_count += 1
            name = parse_file_name(str(_file))
            if not name:
                return {"reason": f"No valid file-name: {name}"}

            if is_video(name):
                some_dir = get_path_videos(project_name)
            elif is_image(name):
                some_dir = get_path_projects(project_name)
            elif name == "infofile.txt":
                some_dir = get_path_projects(project_name)
                incr_count = True
            else:
                elog(f"Unknown file-type: {name}", tag="[UPLOAD]")
                continue

            if not without_infofiles:
                some_dir = os.path.join(some_dir, str(folder_counter))

            save_check_dir(some_dir)
            _path = os.path.join(some_dir, name)
            if _path.startswith(MEDIA_ROOT):
                _path = _path[len(get_path_projects())+1:].replace("\\", "/")

            _new_file = fs.save(_path, _file)

            if incr_count:
                folder_counter += 1

            dlog(f"{_new_file=}", tag="[UPLOAD]")

            # response.update({name: {"created": 1, "cached": 0, "name": name,
            #                         "error": None, "path": _new_path[len(DEFAULT_DIRS.get("projects")) + 1:]}})

        response.update({"files": files_count, "pos": pos})
        return response
