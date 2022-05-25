from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from scoring.views.viewsets.base_viewset import EmptyViewSet
from scoring.views.viewsets.docker_viewset import DockerViewSet
from scoring.views.viewsets.project_viewset import ProjectViewSet
from scoring.views.viewsets.imagescore_viewset import ImageScoreViewSet
from scoring.views.viewsets.backup_viewset import BackupViewSet

router = DefaultRouter()
router.register(r'project', ProjectViewSet, basename='project')
router.register(r'imagescore', ImageScoreViewSet, basename='scoreimage')
router.register(r'backup', BackupViewSet, basename='backup')
router.register(r'docker', DockerViewSet, basename='docker')

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^api-auth/', include('rest_framework.urls')),
    # url(r'', EmptyViewSet.as_view({'get': 'empty'})),
]
