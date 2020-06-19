from django.urls import path, include
from rest_framework.routers import DefaultRouter

from post import views
from post.views import TagView

router = DefaultRouter()
router.register("feed", views.FeedViewSet)
router.register(
    r"(?P<post_pk>\d+)/comments", views.CommentView, basename="comments",
)
router.register(
    "links", views.LinkModelViewSet, basename="links",
)

urlpatterns = [
    path("", include(router.urls)),
    path("all/", views.All.as_view(), name="all"),
    path("tags/<slug>", views.TagView.as_view(), name="tag"),
    path("like/<uuid:post_id>/", views.Like.as_view(), name="like"),
    path("<uuid:post_id>/likers/", views.Likers.as_view(), name="likers"),
]
