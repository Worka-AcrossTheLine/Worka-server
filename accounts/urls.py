from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("tendency/", views.tendency_view, name="tendency"),
    path("delete/", views.DeleteUserView.as_view(), name="delete-user"),
    path("username/", views.forgot_username_view, name="forgot-username"),
    path("update/password/", views.ChangePassword.as_view(), name="change-password"),
    path("update/username/", views.ChangeUsername.as_view(), name="change-username"),
]
