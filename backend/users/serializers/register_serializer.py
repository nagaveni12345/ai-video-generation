"""
users/serializers/register_serializer.py

Validates registration payload for VidAI Studio.
Supports: full_name, email, password, confirm_password, terms_accepted.
"""

from rest_framework import serializers
from users.utils.validators import validate_password_strength, validate_full_name
from users.utils.constants import ERR_TERMS_NOT_ACCEPTED, ERR_PASSWORDS_DONT_MATCH


class RegisterSerializer(serializers.Serializer):
    """
    Validates user registration payload.

    Business logic (DB writes, token generation) lives in AuthService.
    This serializer is validation-only.
    """

    full_name = serializers.CharField(
        min_length=2,
        max_length=255,
        trim_whitespace=True,
        error_messages={
            "min_length": "Full name must be at least 2 characters.",
            "blank": "Full name is required.",
            "required": "Full name is required.",
        },
    )

    email = serializers.EmailField(
        error_messages={
            "invalid": "Enter a valid email address.",
            "blank": "Email is required.",
            "required": "Email is required.",
        }
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        error_messages={
            "min_length": "Password must be at least 8 characters.",
            "blank": "Password is required.",
            "required": "Password is required.",
        },
    )

    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        error_messages={
            "blank": "Please confirm your password.",
            "required": "Please confirm your password.",
        },
    )

    terms_accepted = serializers.BooleanField(
        error_messages={
            "required": ERR_TERMS_NOT_ACCEPTED,
        }
    )

    def validate_email(self, value: str) -> str:
        return value.lower().strip()

    def validate_full_name(self, value: str) -> str:
        return validate_full_name(value)

    def validate_password(self, value: str) -> str:
        validate_password_strength(value)
        return value

    def validate_terms_accepted(self, value: bool) -> bool:
        if not value:
            raise serializers.ValidationError(ERR_TERMS_NOT_ACCEPTED)
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({"confirm_password": ERR_PASSWORDS_DONT_MATCH})
        return attrs
