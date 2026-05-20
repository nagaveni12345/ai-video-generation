"""
users/serializers/forgot_password_serializer.py

Validates the forgot-password request.
Does NOT confirm whether email exists (prevents user enumeration).
"""

from rest_framework import serializers


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Accepts user email and triggers password reset email.
    """

    email = serializers.EmailField(
        error_messages={
            "invalid": "Enter a valid email address.",
            "blank": "Email is required.",
            "required": "Email is required.",
        }
    )

    def validate_email(self, value: str) -> str:
        return value.lower().strip()
