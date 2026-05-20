"""
users/urls.py

Auth module URL routing for VidAI Studio.
All endpoints prefixed with /api/auth/ at the root urlconf level.
"""

from django.urls import path
from users.views import (
    RegisterView,
    LoginView,
    TokenRefreshView,
    LogoutView,
    ForgotPasswordView,
    ResetPasswordView,
    GoogleAuthView,
    AppleAuthView,
)

app_name = "users"

urlpatterns = [
    # Core auth
    path("register/",          RegisterView.as_view(),      name="register"),
    path("login/",             LoginView.as_view(),         name="login"),
    path("logout/",            LogoutView.as_view(),        name="logout"),
    path("token/refresh/",     TokenRefreshView.as_view(),  name="token-refresh"),

    # Password reset
    path("forgot-password/",   ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password/",    ResetPasswordView.as_view(),  name="reset-password"),

    # Social auth (placeholders)
    path("google/",            GoogleAuthView.as_view(),    name="google-auth"),
    path("apple/",             AppleAuthView.as_view(),     name="apple-auth"),
]
