"""
users/serializers/reset_password_serializer.py

Validates password reset payload.
"""

from rest_framework import serializers
from users.utils.validators import validate_password_strength
from users.utils.constants import ERR_PASSWORDS_DONT_MATCH


class ResetPasswordSerializer(serializers.Serializer):
    """
    Validates token and new password for the reset flow.
    """

    token = serializers.CharField(
        error_messages={
            "blank": "Reset token is required.",
            "required": "Reset token is required.",
        }
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        error_messages={
            "min_length": "Password must be at least 8 characters.",
            "blank": "New password is required.",
            "required": "New password is required.",
        },
    )

    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        error_messages={
            "blank": "Please confirm your new password.",
            "required": "Please confirm your new password.",
        },
    )

    def validate_new_password(self, value: str) -> str:
        validate_password_strength(value)
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs.get("new_password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({"confirm_password": ERR_PASSWORDS_DONT_MATCH})
        return attrs
