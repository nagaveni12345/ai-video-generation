"""
users/serializers/login_serializer.py

Validates login credentials for VidAI Studio.
Supports: email, password, remember_me.
"""

from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """
    Validates login payload.
    Authentication logic lives in AuthService — not here.
    """

    email = serializers.EmailField(
        error_messages={
            "invalid": "Enter a valid email address.",
            "blank": "Email is required.",
            "required": "Email is required.",
        }
    )

    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        error_messages={
            "blank": "Password is required.",
            "required": "Password is required.",
        },
    )

    remember_me = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Extends refresh token lifetime when True.",
    )

    def validate_email(self, value: str) -> str:
        return value.lower().strip()
