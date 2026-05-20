"""
users/views.py

Thin view layer for VidAI Studio auth module.
Views validate input via serializers, delegate business logic to services,
and return standardized JSON responses.

All responses follow the shape:
  { "success": bool, "message": str, "data": {} | "errors": {} }
"""

import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError

from users.serializers import (
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    UserSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    GoogleAuthSerializer,
    AppleAuthSerializer,
)
from users.services.auth_service import AuthService, AuthenticationError, RegistrationError
from users.services.token_service import TokenService
from users.services.password_reset_service import PasswordResetService, PasswordResetError
from users.services.social_auth_service import GoogleAuthService, AppleAuthService, SocialAuthError

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def success_response(message: str, data: dict = None, status_code: int = 200) -> Response:
    return Response(
        {"success": True, "message": message, "data": data or {}},
        status=status_code,
    )


def error_response(message: str, errors: dict = None, status_code: int = 400) -> Response:
    payload = {"success": False, "message": message}
    if errors:
        payload["errors"] = errors
    return Response(payload, status=status_code)


def validation_error(serializer) -> Response:
    return error_response(
        message="Validation failed.",
        errors=serializer.errors,
        status_code=status.HTTP_400_BAD_REQUEST,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Register
# ─────────────────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    """
    POST /api/auth/register/

    Create a new VidAI Studio account.
    Returns user data + JWT tokens on success.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return validation_error(serializer)

        try:
            result = AuthService.register_user(serializer.validated_data)
        except RegistrationError as exc:
            return error_response(str(exc), status_code=status.HTTP_409_CONFLICT)

        return success_response(
            message="Account created successfully.",
            data={
                "user": UserSerializer(result["user"]).data,
                "tokens": result["tokens"],
            },
            status_code=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Login
# ─────────────────────────────────────────────────────────────────────────────

class LoginView(APIView):
    """
    POST /api/auth/login/

    Authenticate with email + password.
    Supports remember_me to extend token lifetime.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return validation_error(serializer)

        try:
            result = AuthService.login_user(serializer.validated_data)
        except AuthenticationError as exc:
            return error_response(str(exc), status_code=status.HTTP_401_UNAUTHORIZED)

        return success_response(
            message="Login successful.",
            data={
                "user": UserSerializer(result["user"]).data,
                "tokens": result["tokens"],
            },
        )


# ─────────────────────────────────────────────────────────────────────────────
# Token Refresh
# ─────────────────────────────────────────────────────────────────────────────

class TokenRefreshView(APIView):
    """
    POST /api/auth/token/refresh/

    Exchange a valid refresh token for a new access token.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return error_response(
                "Refresh token is required.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            tokens = TokenService.refresh_access_token(refresh_token)
        except TokenError:
            return error_response(
                "Invalid or expired refresh token.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        return success_response(
            message="Token refreshed successfully.",
            data={"tokens": tokens},
        )


# ─────────────────────────────────────────────────────────────────────────────
# Logout
# ─────────────────────────────────────────────────────────────────────────────

class LogoutView(APIView):
    """
    POST /api/auth/logout/

    Blacklist the provided refresh token.
    Requires authentication.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = LogoutSerializer(data=request.data)

        if not serializer.is_valid():
            return validation_error(serializer)

        try:
            serializer.save()
        except TokenError:
            return error_response(
                "Invalid or expired token.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            logger.error("Logout error: %s", exc)
            return error_response(
                "Logout failed.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return success_response(
            message="Logout successful.",
            data={"detail": "Refresh token has been blacklisted."},
        )


# ─────────────────────────────────────────────────────────────────────────────
# Forgot Password
# ─────────────────────────────────────────────────────────────────────────────

class ForgotPasswordView(APIView):
    """
    POST /api/auth/forgot-password/

    Initiate password reset. Always returns 200 to prevent email enumeration.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = ForgotPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return validation_error(serializer)

        PasswordResetService.initiate_reset(serializer.validated_data["email"])

        # Always return the same response regardless of whether email exists
        return success_response(
            message="If this email is registered, you'll receive a reset link shortly.",
        )


# ─────────────────────────────────────────────────────────────────────────────
# Reset Password
# ─────────────────────────────────────────────────────────────────────────────

class ResetPasswordView(APIView):
    """
    POST /api/auth/reset-password/

    Validate reset token and set new password.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = ResetPasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return validation_error(serializer)

        try:
            PasswordResetService.confirm_reset(
                raw_token=serializer.validated_data["token"],
                new_password=serializer.validated_data["new_password"],
            )
        except PasswordResetError as exc:
            return error_response(str(exc), status_code=status.HTTP_400_BAD_REQUEST)

        return success_response(message="Password reset successfully. You can now log in.")


# ─────────────────────────────────────────────────────────────────────────────
# Google OAuth (Placeholder)
# ─────────────────────────────────────────────────────────────────────────────

class GoogleAuthView(APIView):
    """
    POST /api/auth/google/

    Authenticate or register via Google OAuth ID token.
    Returns user data + JWT tokens.

    PLACEHOLDER — requires GOOGLE_CLIENT_ID in .env and google-auth library.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = GoogleAuthSerializer(data=request.data)

        if not serializer.is_valid():
            return validation_error(serializer)

        try:
            result = GoogleAuthService.authenticate(
                id_token=serializer.validated_data["id_token"],
                terms_accepted=serializer.validated_data.get("terms_accepted", False),
            )
        except NotImplementedError as exc:
            return error_response(str(exc), status_code=status.HTTP_501_NOT_IMPLEMENTED)
        except SocialAuthError as exc:
            return error_response(str(exc), status_code=status.HTTP_401_UNAUTHORIZED)

        status_code = status.HTTP_201_CREATED if result.get("created") else status.HTTP_200_OK
        message = "Google registration successful." if result.get("created") else "Google login successful."

        return success_response(
            message=message,
            data={
                "user": UserSerializer(result["user"]).data,
                "tokens": result["tokens"],
            },
            status_code=status_code,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Apple OAuth (Placeholder)
# ─────────────────────────────────────────────────────────────────────────────

class AppleAuthView(APIView):
    """
    POST /api/auth/apple/

    Authenticate or register via Apple Sign-In identity token.

    PLACEHOLDER — requires Apple credentials in .env and PyJWT + cryptography.
    """

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = AppleAuthSerializer(data=request.data)

        if not serializer.is_valid():
            return validation_error(serializer)

        try:
            result = AppleAuthService.authenticate(
                identity_token=serializer.validated_data["identity_token"],
                full_name=serializer.validated_data.get("full_name"),
                terms_accepted=serializer.validated_data.get("terms_accepted", False),
            )
        except NotImplementedError as exc:
            return error_response(str(exc), status_code=status.HTTP_501_NOT_IMPLEMENTED)
        except SocialAuthError as exc:
            return error_response(str(exc), status_code=status.HTTP_401_UNAUTHORIZED)

        status_code = status.HTTP_201_CREATED if result.get("created") else status.HTTP_200_OK
        message = "Apple registration successful." if result.get("created") else "Apple login successful."

        return success_response(
            message=message,
            data={
                "user": UserSerializer(result["user"]).data,
                "tokens": result["tokens"],
            },
            status_code=status_code,
        )
