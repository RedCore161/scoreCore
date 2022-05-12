from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter
from django.views.static import serve

from scoring.views.viewsets import ProjectViewSet, ImageScoreViewSet
from server.settings import MEDIA_ROOT

router = DefaultRouter()
router.register(r'project', ProjectViewSet, basename='project')
router.register(r'imagescore', ImageScoreViewSet, basename='scoreimage')

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^test-data/(?P<path>.*)$', serve, {'document_root': MEDIA_ROOT}),
]
