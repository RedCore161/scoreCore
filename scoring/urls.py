from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from scoring.views.viewsets.docker_viewset import DockerViewSet
from scoring.views.viewsets.project_viewset import ProjectViewSet
from scoring.views.viewsets.imagescore_viewset import ImageScoreViewSet
from scoring.views.viewsets.backup_viewset import BackupViewSet
from scoring.views.viewsets.user_viewset import UserViewSet

router = DefaultRouter()
router.register(r'project', ProjectViewSet, basename='project')
router.register(r'imagescore', ImageScoreViewSet, basename='scoreimage')
router.register(r'backup', BackupViewSet, basename='backup')
router.register(r'docker', DockerViewSet, basename='docker')
router.register(r'user', UserViewSet, basename='user')

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^api-auth/', include('rest_framework.urls')),
]
