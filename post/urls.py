from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LinkModelViewSet, FeedViewSet, Like, Likers

router = DefaultRouter()
router.register("feed", FeedViewSet)
router.register(
    "links", LinkModelViewSet, basename="links",
)

urlpatterns = [
    path("", include(router.urls)),
    path("like/<int:post_id>/", Like.as_view(), name="like"),
    path("<int:post_id>/likers/", Likers.as_view(), name="likers"),
]
