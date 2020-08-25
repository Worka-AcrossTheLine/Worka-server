from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import FeedViewSet

router = DefaultRouter()
router.register("", FeedViewSet, basename="feed")

urlpatterns = [
    path("", include(router.urls)),
]
