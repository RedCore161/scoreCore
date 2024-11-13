from django.urls import include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from scoring.views.viewsets.base_viewset import ExtendedTokenObtainPairView
from scoring.views.viewsets.docker_viewset import DockerViewSet
from scoring.views.viewsets.imagefile_viewset import ImageFileViewSet
from scoring.views.viewsets.project_viewset import ProjectViewSet
from scoring.views.viewsets.imagescore_viewset import ImageScoreViewSet
from scoring.views.viewsets.backup_viewset import BackupViewSet
from scoring.views.viewsets.user_viewset import UserViewSet

router = DefaultRouter()
router.register(r"project", ProjectViewSet, basename="project")
router.register(r"imagescore", ImageScoreViewSet, basename="scoreimage")
router.register(r"imagefile", ImageFileViewSet, basename="imagefile")
router.register(r"backup", BackupViewSet, basename="backup")
router.register(r"docker", DockerViewSet, basename="docker")
router.register(r"user", UserViewSet, basename="user")

urlpatterns = [
    re_path(r"^api/token/refresh/$", TokenRefreshView.as_view(), name="token_refresh"),
    re_path(r"^api/token/$", ExtendedTokenObtainPairView.as_view(), name="token_obtain_pair"),
    re_path(r"^api/", include(router.urls)),
]
