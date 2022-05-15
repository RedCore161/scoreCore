from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from scoring.views.viewsets import ProjectViewSet, ImageScoreViewSet, BackupViewSet

router = DefaultRouter()
router.register(r'project', ProjectViewSet, basename='project')
router.register(r'imagescore', ImageScoreViewSet, basename='scoreimage')
router.register(r'backup', BackupViewSet, basename='backup')

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^api-auth/', include('rest_framework.urls')),
    # url(r'', EmptyViewSet.as_view({'get': 'empty'})),
]
