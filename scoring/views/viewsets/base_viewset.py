from django.contrib.auth import login
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

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
    serializer_class = TokenObtainPairSerializer

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
