"""
users/services/social_auth_service.py

Architecture-ready social authentication service for VidAI Studio.

Google: Verifies ID tokens via Google's tokeninfo endpoint.
Apple:  Verifies identity tokens via Apple's JWKS endpoint.

PLACEHOLDER — real credentials / SDK calls are NOT implemented.
This file establishes the service structure for future implementation.

To activate:
  1. Add credentials to .env (see comments below).
  2. Install: pip install google-auth PyJWT cryptography
  3. Replace the NotImplementedError blocks with real verification calls.
"""

import logging
from typing import Dict, Any, Optional
from datetime import timezone, datetime

from django.db import IntegrityError

from users.models import User
from users.services.token_service import TokenService
from users.utils.constants import GOOGLE_TOKEN_INFO_URL, APPLE_KEYS_URL

logger = logging.getLogger(__name__)


class SocialAuthError(Exception):
    """Raised when social token verification or user creation fails."""
    pass


class GoogleAuthService:
    """
    Handles Google OAuth ID token verification and user login/registration.

    Required .env vars:
        GOOGLE_CLIENT_ID = "your-google-client-id.apps.googleusercontent.com"

    Implementation steps:
        pip install google-auth
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
    """

    @staticmethod
    def authenticate(id_token: str, terms_accepted: bool = False) -> Dict[str, Any]:
        """
        Verify Google ID token and return (or create) a VidAI user.

        Args:
            id_token: Google ID token from client.
            terms_accepted: Required on first-time registration.

        Returns:
            Dict with 'user', 'tokens', 'created' (bool).

        Raises:
            SocialAuthError: If token verification fails.
        """
        # ── Step 1: Verify token with Google ──────────────────────────────────
        # import google.auth.transport.requests
        # from google.oauth2 import id_token as google_id_token
        # from django.conf import settings
        #
        # try:
        #     idinfo = google_id_token.verify_oauth2_token(
        #         id_token,
        #         google.auth.transport.requests.Request(),
        #         settings.GOOGLE_CLIENT_ID,
        #     )
        # except ValueError as exc:
        #     raise SocialAuthError(f"Invalid Google token: {exc}")

        # ── Step 2: Extract claims ─────────────────────────────────────────────
        # email     = idinfo["email"]
        # full_name = idinfo.get("name", "")
        # verified  = idinfo.get("email_verified", False)

        # ── Step 3: Get or create user ─────────────────────────────────────────
        # user, created = GoogleAuthService._get_or_create_user(
        #     email=email,
        #     full_name=full_name,
        #     email_verified=verified,
        #     terms_accepted=terms_accepted,
        # )

        raise NotImplementedError(
            "GoogleAuthService.authenticate() is not yet implemented. "
            "Add GOOGLE_CLIENT_ID to .env and install google-auth."
        )

    @staticmethod
    def _get_or_create_user(
        email: str,
        full_name: str,
        email_verified: bool,
        terms_accepted: bool,
    ) -> tuple[User, bool]:
        """Find existing user or create a new one from Google claims."""
        user = User.objects.filter(email=email).first()

        if user:
            # Update provider in case they previously registered via email
            if user.auth_provider != User.AuthProvider.GOOGLE:
                user.auth_provider = User.AuthProvider.GOOGLE
                user.save(update_fields=["auth_provider"])
            return user, False

        user = User.objects.create_user(
            email=email,
            full_name=full_name or "Google User",
            password=None,
            auth_provider=User.AuthProvider.GOOGLE,
            is_email_verified=email_verified,
            terms_accepted=terms_accepted,
            terms_accepted_at=datetime.now(tz=timezone.utc) if terms_accepted else None,
        )
        logger.info("New user via Google OAuth: %s", email)
        return user, True


class AppleAuthService:
    """
    Handles Apple Sign-In identity token verification.

    Required .env vars:
        APPLE_APP_BUNDLE_ID = "com.vidai.studio"
        APPLE_TEAM_ID       = "YOUR_TEAM_ID"
        APPLE_CLIENT_ID     = "com.vidai.studio.service"

    Implementation steps:
        pip install PyJWT cryptography
        Fetch Apple's JWKS from APPLE_KEYS_URL.
        Decode and verify identity_token using matching public key.
    """

    @staticmethod
    def authenticate(
        identity_token: str,
        full_name: Optional[str] = None,
        terms_accepted: bool = False,
    ) -> Dict[str, Any]:
        """
        Verify Apple identity token and return (or create) a VidAI user.

        Args:
            identity_token: JWT from Apple Sign-In.
            full_name: Only provided on first login (Apple sends it once).
            terms_accepted: Required on first registration.

        Returns:
            Dict with 'user', 'tokens', 'created' (bool).

        Raises:
            SocialAuthError: If token is invalid.
        """
        # ── Step 1: Fetch Apple JWKS ───────────────────────────────────────────
        # import requests, jwt
        # from jwt.algorithms import RSAAlgorithm
        #
        # jwks = requests.get(APPLE_KEYS_URL).json()
        # header = jwt.get_unverified_header(identity_token)
        # key = next(k for k in jwks["keys"] if k["kid"] == header["kid"])
        # public_key = RSAAlgorithm.from_jwk(key)

        # ── Step 2: Decode and verify ──────────────────────────────────────────
        # claims = jwt.decode(
        #     identity_token,
        #     public_key,
        #     algorithms=["RS256"],
        #     audience=settings.APPLE_CLIENT_ID,
        # )
        # email = claims["email"]

        raise NotImplementedError(
            "AppleAuthService.authenticate() is not yet implemented. "
            "Add Apple credentials to .env and install PyJWT + cryptography."
        )
