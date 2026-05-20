"""
users/serializers/user_serializer.py

Read-only serializer for safe user data in API responses.
"""

from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Safe, read-only representation of a User instance.
    Never exposes: password, is_staff, is_superuser, internal flags.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "is_active",
            "is_email_verified",
            "auth_provider",
            "terms_accepted",
            "created_at",
        ]
        read_only_fields = fields
