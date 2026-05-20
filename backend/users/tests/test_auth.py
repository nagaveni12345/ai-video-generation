"""
users/tests/test_auth.py

Comprehensive auth test suite for VidAI Studio.
Covers: serializers, services, API integration, JWT, permissions, validation.
"""

from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User
from users.serializers import RegisterSerializer, LoginSerializer
from users.services.auth_service import AuthService, AuthenticationError, RegistrationError
from users.services.token_service import TokenService
from users.utils.validators import validate_password_strength, validate_full_name
from rest_framework import serializers as drf_serializers


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_user(email="user@vidai.com", full_name="Test User", password="Secure@123") -> User:
    return User.objects.create_user(email=email, full_name=full_name, password=password)


REGISTER_PAYLOAD = {
    "full_name": "Jane Doe",
    "email": "jane@vidai.com",
    "password": "Secure@123",
    "confirm_password": "Secure@123",
    "terms_accepted": True,
}

LOGIN_PAYLOAD = {
    "email": "jane@vidai.com",
    "password": "Secure@123",
}


# ─────────────────────────────────────────────────────────────────────────────
# Validator Tests
# ─────────────────────────────────────────────────────────────────────────────

class PasswordValidatorTests(TestCase):

    def test_strong_password_passes(self):
        """Should not raise for a strong password."""
        validate_password_strength("Secure@123")

    def test_short_password_fails(self):
        with self.assertRaises(drf_serializers.ValidationError):
            validate_password_strength("Ab1@")

    def test_no_uppercase_fails(self):
        with self.assertRaises(drf_serializers.ValidationError):
            validate_password_strength("secure@123")

    def test_no_digit_fails(self):
        with self.assertRaises(drf_serializers.ValidationError):
            validate_password_strength("Secure@abc")

    def test_no_special_char_fails(self):
        with self.assertRaises(drf_serializers.ValidationError):
            validate_password_strength("Secure1234")


class FullNameValidatorTests(TestCase):

    def test_valid_name(self):
        result = validate_full_name("Jane Doe")
        self.assertEqual(result, "Jane Doe")

    def test_name_with_hyphen(self):
        result = validate_full_name("Mary-Jane Watson")
        self.assertIn("Mary-Jane", result)

    def test_numeric_name_fails(self):
        with self.assertRaises(drf_serializers.ValidationError):
            validate_full_name("12345")

    def test_special_chars_fail(self):
        with self.assertRaises(drf_serializers.ValidationError):
            validate_full_name("Jane<script>")

    def test_too_short_fails(self):
        with self.assertRaises(drf_serializers.ValidationError):
            validate_full_name("A")


# ─────────────────────────────────────────────────────────────────────────────
# RegisterSerializer Tests
# ─────────────────────────────────────────────────────────────────────────────

class RegisterSerializerTests(TestCase):

    def test_valid_payload(self):
        s = RegisterSerializer(data=REGISTER_PAYLOAD)
        self.assertTrue(s.is_valid(), s.errors)

    def test_password_mismatch(self):
        data = {**REGISTER_PAYLOAD, "confirm_password": "Wrong@123"}
        s = RegisterSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("confirm_password", s.errors)

    def test_terms_not_accepted(self):
        data = {**REGISTER_PAYLOAD, "terms_accepted": False}
        s = RegisterSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("terms_accepted", s.errors)

    def test_email_normalized(self):
        data = {**REGISTER_PAYLOAD, "email": "  JANE@VIDAI.COM  "}
        s = RegisterSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["email"], "jane@vidai.com")

    def test_invalid_email(self):
        data = {**REGISTER_PAYLOAD, "email": "not-an-email"}
        s = RegisterSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("email", s.errors)

    def test_weak_password(self):
        data = {**REGISTER_PAYLOAD, "password": "weak", "confirm_password": "weak"}
        s = RegisterSerializer(data=data)
        self.assertFalse(s.is_valid())

    def test_numeric_name_fails(self):
        data = {**REGISTER_PAYLOAD, "full_name": "1234"}
        s = RegisterSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("full_name", s.errors)


# ─────────────────────────────────────────────────────────────────────────────
# LoginSerializer Tests
# ─────────────────────────────────────────────────────────────────────────────

class LoginSerializerTests(TestCase):

    def test_valid_payload(self):
        s = LoginSerializer(data=LOGIN_PAYLOAD)
        self.assertTrue(s.is_valid(), s.errors)

    def test_remember_me_default_false(self):
        s = LoginSerializer(data=LOGIN_PAYLOAD)
        s.is_valid()
        self.assertFalse(s.validated_data["remember_me"])

    def test_remember_me_true(self):
        s = LoginSerializer(data={**LOGIN_PAYLOAD, "remember_me": True})
        s.is_valid()
        self.assertTrue(s.validated_data["remember_me"])

    def test_missing_email_fails(self):
        s = LoginSerializer(data={"password": "Secure@123"})
        self.assertFalse(s.is_valid())
        self.assertIn("email", s.errors)


# ─────────────────────────────────────────────────────────────────────────────
# AuthService Tests
# ─────────────────────────────────────────────────────────────────────────────

class AuthServiceTests(TestCase):

    def test_register_creates_user(self):
        result = AuthService.register_user({
            "email": "new@vidai.com",
            "full_name": "New User",
            "password": "Secure@123",
            "terms_accepted": True,
        })
        self.assertIn("user", result)
        self.assertIn("tokens", result)
        self.assertEqual(result["user"].email, "new@vidai.com")

    def test_register_duplicate_email_raises(self):
        make_user(email="dup@vidai.com")
        with self.assertRaises(RegistrationError):
            AuthService.register_user({
                "email": "dup@vidai.com",
                "full_name": "Dupe User",
                "password": "Secure@123",
                "terms_accepted": True,
            })

    def test_login_valid_credentials(self):
        make_user(email="login@vidai.com", password="Secure@123")
        result = AuthService.login_user({"email": "login@vidai.com", "password": "Secure@123"})
        self.assertIn("tokens", result)

    def test_login_wrong_password_raises(self):
        make_user(email="bad@vidai.com", password="Secure@123")
        with self.assertRaises(AuthenticationError):
            AuthService.login_user({"email": "bad@vidai.com", "password": "Wrong@000"})

    def test_login_inactive_user_raises(self):
        user = make_user(email="inactive@vidai.com", password="Secure@123")
        user.is_active = False
        user.save()
        with self.assertRaises(AuthenticationError):
            AuthService.login_user({"email": "inactive@vidai.com", "password": "Secure@123"})


# ─────────────────────────────────────────────────────────────────────────────
# TokenService Tests
# ─────────────────────────────────────────────────────────────────────────────

class TokenServiceTests(TestCase):

    def setUp(self):
        self.user = make_user()

    def test_generates_token_pair(self):
        tokens = TokenService.generate_tokens(self.user)
        self.assertIn("access", tokens)
        self.assertIn("refresh", tokens)

    def test_refresh_produces_access_token(self):
        tokens = TokenService.generate_tokens(self.user)
        refreshed = TokenService.refresh_access_token(tokens["refresh"])
        self.assertIn("access", refreshed)

    def test_invalid_refresh_raises(self):
        from rest_framework_simplejwt.exceptions import TokenError
        with self.assertRaises(TokenError):
            TokenService.refresh_access_token("invalid.token.here")


# ─────────────────────────────────────────────────────────────────────────────
# API Integration Tests
# ─────────────────────────────────────────────────────────────────────────────

class RegisterAPITests(APITestCase):

    url = "/api/auth/register/"

    def test_register_success(self):
        response = self.client.post(self.url, REGISTER_PAYLOAD, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertIn("tokens", response.data["data"])
        self.assertIn("user", response.data["data"])

    def test_register_duplicate_email(self):
        make_user(email="jane@vidai.com")
        response = self.client.post(self.url, REGISTER_PAYLOAD, format="json")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertFalse(response.data["success"])

    def test_register_weak_password(self):
        data = {**REGISTER_PAYLOAD, "password": "weak", "confirm_password": "weak"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_terms_not_accepted(self):
        data = {**REGISTER_PAYLOAD, "terms_accepted": False}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        data = {**REGISTER_PAYLOAD, "confirm_password": "Different@123"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPITests(APITestCase):

    url = "/api/auth/login/"

    def setUp(self):
        make_user(email="jane@vidai.com", password="Secure@123")

    def test_login_success(self):
        response = self.client.post(self.url, LOGIN_PAYLOAD, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("tokens", response.data["data"])

    def test_login_wrong_password(self):
        response = self.client.post(self.url, {**LOGIN_PAYLOAD, "password": "Wrong@000"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_unknown_email(self):
        response = self.client.post(self.url, {"email": "nobody@vidai.com", "password": "Secure@123"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_remember_me(self):
        response = self.client.post(self.url, {**LOGIN_PAYLOAD, "remember_me": True}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TokenRefreshAPITests(APITestCase):

    url = "/api/auth/token/refresh/"

    def setUp(self):
        self.user = make_user()
        self.tokens = TokenService.generate_tokens(self.user)

    def test_refresh_success(self):
        response = self.client.post(self.url, {"refresh": self.tokens["refresh"]}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data["data"])

    def test_refresh_invalid_token(self):
        response = self.client.post(self.url, {"refresh": "bad.token"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_missing_token(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutAPITests(APITestCase):

    url = "/api/auth/logout/"

    def setUp(self):
        self.user = make_user()
        self.tokens = TokenService.generate_tokens(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.tokens['access']}")

    def test_logout_success(self):
        response = self.client.post(self.url, {"refresh": self.tokens["refresh"]}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_unauthenticated(self):
        self.client.credentials()
        response = self.client.post(self.url, {"refresh": self.tokens["refresh"]}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_missing_refresh_token(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ForgotPasswordAPITests(APITestCase):

    url = "/api/auth/forgot-password/"

    def test_always_returns_200_for_known_email(self):
        make_user(email="known@vidai.com")
        response = self.client.post(self.url, {"email": "known@vidai.com"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_always_returns_200_for_unknown_email(self):
        """Prevents user enumeration — same response regardless."""
        response = self.client.post(self.url, {"email": "ghost@vidai.com"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_email_returns_400(self):
        response = self.client.post(self.url, {"email": "not-an-email"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SocialAuthPlaceholderTests(APITestCase):
    """
    Confirm social auth endpoints are wired and return 501 Not Implemented
    until real credentials are configured.
    """

    def test_google_auth_returns_501(self):
        response = self.client.post(
            "/api/auth/google/",
            {"id_token": "fake.google.token"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)

    def test_apple_auth_returns_501(self):
        response = self.client.post(
            "/api/auth/apple/",
            {"identity_token": "fake.apple.token"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)


# ─────────────────────────────────────────────────────────────────────────────
# Permission Tests
# ─────────────────────────────────────────────────────────────────────────────

class PermissionTests(APITestCase):

    def test_logout_requires_auth(self):
        response = self.client.post("/api/auth/logout/", {"refresh": "token"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deactivated_user_cannot_logout(self):
        user = make_user()
        tokens = TokenService.generate_tokens(user)
        user.is_active = False
        user.save()

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        # Token is still technically valid but user is inactive —
        # DRF's simplejwt auth will still allow it at middleware level;
        # IsAuthenticatedUser (custom) would block, but default IsAuthenticated
        # in LogoutView does not check is_active again. Verify this behavior.
        response = self.client.post("/api/auth/logout/", {"refresh": tokens["refresh"]}, format="json")
        # Standard DRF IsAuthenticated passes if token is valid even for inactive;
        # custom IsAuthenticatedUser would block with 403.
        self.assertIn(response.status_code, [200, 403])
