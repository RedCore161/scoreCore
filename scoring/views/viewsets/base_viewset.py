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

from scoring.basics import parse_file_name
from scoring.helper import save_check_dir, get_path_projects, dlog, is_video, is_image, get_path_videos, elog
from scoring.serializers import RedcoreTokenObtainPairSerializer
from server.settings import DEFAULT_DIRS
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
    def base_upload_file(request, project_name, *args, **kwargs) -> dict:

        response = {}
        fs = FileSystemStorage(location=DEFAULT_DIRS.get("projects"))

        for file in request.FILES:
            _file = request.FILES.get(file)
            if _file:
                name = parse_file_name(str(_file))
                if not name:
                    return {"reason": f"No valid file-name: {name}"}

                if is_video(name):
                    some_dir = get_path_videos(project_name)
                elif is_image(name):
                    some_dir = get_path_projects(project_name)
                else:
                    elog(f"Unknown file-type: {name}", tag="[UPLOAD]")
                    continue

                save_check_dir(some_dir)
                _path = os.path.join(some_dir, name)
                _new_file = fs.save(_path, _file)

                dlog(f"{_new_file=}", tag="[UPLOAD]")

                # response.update({name: {"created": 1, "cached": 0, "name": name,
                #                         "error": None, "path": _new_path[len(DEFAULT_DIRS.get("projects")) + 1:]}})

        return response
