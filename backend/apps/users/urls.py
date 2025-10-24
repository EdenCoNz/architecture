"""
URL configuration for authentication endpoints.
"""

from django.urls import path

from .views import (
    ChangePasswordView,
    CurrentUserView,
    CustomTokenRefreshView,
    UserLoginView,
    UserLogoutView,
    UserRegistrationView,
)

app_name = "auth"

urlpatterns = [
    # Authentication endpoints
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    # User profile endpoints
    path("me/", CurrentUserView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
]
