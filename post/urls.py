from django.urls import path, include
from rest_framework.routers import DefaultRouter

from post import views


router = DefaultRouter()
router.register("", views.FeedViewSet)

urlpatterns = [
    path("feed/", include(router.urls)),
    path("all/", views.All.as_view(), name="all"),
    path("comment/<uuid:post_id>/", views.AddComment.as_view(), name="add-comment"),
    path(
        "comment/<int:comment_id>/",
        views.ManageComment.as_view(),
        name="manage-comment",
    ),
    path("like/<uuid:post_id>/", views.Like.as_view(), name="like"),
    path("<uuid:post_id>/likers/", views.Likers.as_view(), name="likers"),
]
