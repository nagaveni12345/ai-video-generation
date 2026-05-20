"""
users/utils/jwt_helper.py

Low-level JWT utility functions for VidAI Studio.
"""

import logging
from typing import Optional, Dict, Any

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

logger = logging.getLogger(__name__)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate an access token without triggering DRF auth middleware.

    Returns:
        Token payload dict, or None if invalid.
    """
    try:
        validated_token = AccessToken(token)
        return dict(validated_token.payload)
    except (TokenError, InvalidToken) as exc:
        logger.debug("Token decoding failed: %s", str(exc))
        return None


def get_user_id_from_token(token: str) -> Optional[str]:
    """Extract the user UUID from an access token's payload."""
    payload = decode_access_token(token)
    return str(payload.get("user_id")) if payload else None


def is_token_valid(token: str, token_class=AccessToken) -> bool:
    """Check whether a token is structurally valid and not expired."""
    try:
        token_class(token)
        return True
    except (TokenError, InvalidToken):
        return False


def extract_token_from_header(auth_header: str) -> Optional[str]:
    """
    Extract raw token from 'Bearer <token>' Authorization header.

    Returns:
        Token string or None.
    """
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]
