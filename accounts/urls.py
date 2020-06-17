from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from . import views
from question.views import ProfilePageViewSet, QuestionViewSet, CommentViewSet

router = DefaultRouter()

router.register(
    r"profile/(?P<accounts_pk>\d+)/pages", ProfilePageViewSet, basename="profile-pages",
)
router.register(
    r"profile/(?P<accounts_pk>\d+)/pages/(?P<page_pk>\d+)/questions",
    QuestionViewSet,
    basename="profile-questions",
)
router.register(
    r"profile/(?P<accounts_pk>\d+)/pages/(?P<page_pk>\d+)/questions/(?P<question_pk>\d+)/comments",
    CommentViewSet,
    basename="profile-comment",
)

urlpatterns = [
    path("profile/<int:pk>/", views.Profile.as_view()),
    re_path(
        r"profile/(?P<accounts_pk>\d+)/mento/", views.mento_user, name="user-mento"
    ),
    re_path(
        r"profile/(?P<accounts_pk>\d+)/mentiee/",
        views.mentiee_user,
        name="user-mentiee",
    ),
    path("", include(router.urls)),
    path("accounts/signup/", views.signup_view, name="signup"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/tendency/", views.tendency_view, name="tendency"),
    path("accounts/delete/", views.DeleteUserView.as_view(), name="delete-user"),
    path("accounts/username/", views.forgot_username_view, name="forgot-username"),
    path("accounts/password/", views.ChangePassword.as_view(), name="update-password",),
    path("accounts/username/", views.ChangeUsername.as_view(), name="update-username",),
]
