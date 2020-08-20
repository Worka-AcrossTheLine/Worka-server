from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LinkModelViewSet, FeedViewSet

router = DefaultRouter()
router.register("feed", FeedViewSet)
router.register(
    "links", LinkModelViewSet, basename="links",
)

urlpatterns = [
    path("", include(router.urls)),
]
