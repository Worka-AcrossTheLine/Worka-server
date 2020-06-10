from django.urls import path, include
from rest_framework.routers import DefaultRouter

from post import views


router = DefaultRouter()
router.register("", views.PostViewSet)

app_name = "post"

urlpatterns = [
    path("", include(router.urls)),
    path("feeds/", views.Feed.as_view(), name="feed"),
    path("comment/<uuid:post_id>/", views.AddComment.as_view(), name="add-comment"),
    path(
        "comment/<int:comment_id>/",
        views.ManageComment.as_view(),
        name="manage-comment",
    ),
    path("like/<uuid:post_id>/", views.Like.as_view(), name="like"),
    path("<uuid:post_id>/likers/", views.Likers.as_view(), name="get-likers"),
]
