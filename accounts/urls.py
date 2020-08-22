from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from post.views import ProfileFeed
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
router.register(
    r"profile/(?P<accounts_pk>\d+)/feed", ProfileFeed, basename="profile-cards",
)

urlpatterns = [
    path("profile/<int:pk>/", views.ProfilePage.as_view()),
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
    path("accounts/tmp-password/", views.tmp_password, name="tmp-password"),
    path("accounts/delete/", views.DeleteUserView.as_view(), name="delete-user"),
    path(
        "accounts/forgot-username/", views.forgot_username_view, name="forgot-username"
    ),
    path(
        "accounts/comment/",
        views.UpdateDecsription.as_view(),
        name="update-description",
    ),
    path("accounts/password/", views.ChangePassword.as_view(), name="update-password",),
    path("accounts/username/", views.ChangeUsername.as_view(), name="update-username",),
    path("accounts/image/", views.UpdateUserImage.as_view(), name="update-image",),
]
