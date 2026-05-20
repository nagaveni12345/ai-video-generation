"""
users/services/token_service.py

JWT token lifecycle: generation, refresh, custom claims.
If the JWT library is ever swapped, only this file needs to change.
"""

import logging
from datetime import timedelta
from typing import Dict

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from users.models import User

logger = logging.getLogger(__name__)

# Extended token lifetime for "remember me"
REMEMBER_ME_REFRESH_TTL = timedelta(days=30)
DEFAULT_REFRESH_TTL     = timedelta(days=7)


class TokenService:
    """Stateless service for JWT token operations."""

    @staticmethod
    def generate_tokens(user: User, remember_me: bool = False) -> Dict[str, str]:
        """
        Generate access + refresh token pair for the given user.

        Args:
            user: Authenticated User instance.
            remember_me: If True, extends the refresh token lifetime.

        Returns:
            Dict with 'access' and 'refresh' JWT strings.
        """
        refresh = RefreshToken.for_user(user)

        # Extend lifetime if remember_me is set
        if remember_me:
            refresh.set_exp(lifetime=REMEMBER_ME_REFRESH_TTL)

        # Embed non-sensitive custom claims
        refresh["email"] = user.email
        refresh["full_name"] = user.full_name
        refresh["is_email_verified"] = user.is_email_verified

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict[str, str]:
        """
        Generate a new access token from a valid refresh token.

        Args:
            refresh_token: A raw refresh JWT string.

        Returns:
            Dict with new 'access' token.

        Raises:
            TokenError: If the refresh token is invalid or expired.
        """
        try:
            token = RefreshToken(refresh_token)
            return {"access": str(token.access_token)}
        except TokenError as exc:
            logger.warning("Invalid refresh token used: %s", str(exc))
            raise
