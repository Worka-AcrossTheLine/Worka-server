from django.urls import path
from rest_framework_jwt.views import (
    obtain_jwt_token,
    refresh_jwt_token,
    verify_jwt_token,
)
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("tendency/", views.tendency_view, name="tendency"),
    path("delete/", views.DeleteUserView.as_view(), name="delete_user"),
    path("username/", views.forgot_username_view, name="forgot_username"),
    # path("token/refresh/", refresh_jwt_token),
    # path("token/verify/", verify_jwt_token),
]
