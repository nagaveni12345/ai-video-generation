"""
users/serializers/logout_serializer.py

Handles refresh token blacklisting on logout.
"""

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


class LogoutSerializer(serializers.Serializer):
    """
    Accepts refresh token and blacklists it.
    """

    refresh = serializers.CharField(
        error_messages={
            "blank": "Refresh token is required.",
            "required": "Refresh token is required.",
        }
    )

    def validate(self, attrs: dict) -> dict:
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs) -> None:
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError as exc:
            raise serializers.ValidationError({"refresh": str(exc)})
