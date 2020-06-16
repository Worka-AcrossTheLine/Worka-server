from django.urls import path, include
from rest_framework.routers import DefaultRouter

from post import views


router = DefaultRouter()
router.register("", views.FeedViewSet)
router.register(
    r"(?P<post_pk>\d+)/comments", views.CommentView, basename="comments",
)

urlpatterns = [
    path("feed/", include(router.urls)),
    path("all/", views.All.as_view(), name="all"),
    path("like/<uuid:post_id>/", views.Like.as_view(), name="like"),
    path("<uuid:post_id>/likers/", views.Likers.as_view(), name="likers"),
]
