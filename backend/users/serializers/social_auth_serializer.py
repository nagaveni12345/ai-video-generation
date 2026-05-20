"""
users/serializers/social_auth_serializer.py

Serializers for Google and Apple OAuth flows.
Architecture-ready placeholders for future implementation.
"""

from rest_framework import serializers


class GoogleAuthSerializer(serializers.Serializer):
    """
    Validates Google OAuth token payload.

    Frontend sends the ID token from Google Sign-In SDK.
    Backend verifies it against Google's token info endpoint.
    """

    id_token = serializers.CharField(
        help_text="Google ID token from client-side Sign-In.",
        error_messages={
            "blank": "Google ID token is required.",
            "required": "Google ID token is required.",
        },
    )

    terms_accepted = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Required only on first-time social registration.",
    )


class AppleAuthSerializer(serializers.Serializer):
    """
    Validates Apple Sign-In payload.

    Frontend sends the authorization code or identity token from Apple.
    Backend verifies and decodes using Apple's public keys (JWKS).
    """

    identity_token = serializers.CharField(
        help_text="Apple identity token (JWT) from client-side Sign-In.",
        error_messages={
            "blank": "Apple identity token is required.",
            "required": "Apple identity token is required.",
        },
    )

    authorization_code = serializers.CharField(
        required=False,
        help_text="Apple authorization code (for server-side token exchange).",
    )

    full_name = serializers.CharField(
        required=False,
        max_length=255,
        help_text="Full name — only provided on first Apple login.",
    )

    terms_accepted = serializers.BooleanField(
        required=False,
        default=False,
    )
