from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response

from scoring.serializers import UserSerializer, PasswordSerializer
from server.views import RequestSuccess, RequestFailed
from django.contrib.auth import login
from rest_framework_simplejwt.tokens import AccessToken


def authenticate(request, user_id=None):
    try:
        user = User.objects.get(pk=user_id)
        return user
    except User.DoesNotExist:
        return None


class IsAdminOrIsSelf(object):
    pass


class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @permission_classes([IsAdminOrIsSelf])
    @action(detail=True, url_path="set-password", methods=["POST"])
    def set_password(self, request, pk):
        user = self.get_object()
        serializer = PasswordSerializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get("old_password")):
                return RequestFailed({"old_password": ["Wrong password."]})
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return RequestSuccess({"status": "Changed Password!"})
        else:
            return RequestFailed(serializer.errors)

    @action(detail=False, url_path="recent", methods=["GET"])
    def recent_users(self, request):
        recent_users = User.objects.all().order_by("-last_login")

        page = self.paginate_queryset(recent_users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(recent_users, many=True)
        return Response(serializer.data)

    @action(detail=False, url_path="login", methods=["POST"])
    def login_user(self, request):
        token = request.data.get("token")
        if not token:
            return RequestFailed({"error": "Token is required"})

        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            user = authenticate(request, user_id=user_id)

            if user is not None:
                login(request, user)
                return RequestSuccess({"message": "Session created"})
            else:
                return RequestFailed({"error": "Invalid credentials"})

        except Exception as e:
            return RequestFailed({"error": str(e)})
