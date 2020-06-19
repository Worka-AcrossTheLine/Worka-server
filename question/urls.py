from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(
    "", views.PageViewSet, basename="pages",
)
router.register(
    r"(?P<page_pk>\d+)/questions", views.QuestionViewSet, basename="questions",
)
router.register(
    r"(?P<page_pk>\d+)/questions/(?P<question_pk>\d+)/comments",
    views.CommentViewSet,
    basename="comments",
)


urlpatterns = [
    path("", include(router.urls)),
]
