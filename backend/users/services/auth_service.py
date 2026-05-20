"""
users/services/auth_service.py

Core authentication business logic for VidAI Studio.
Views are thin — they delegate entirely to this service.
"""

import logging
from datetime import timezone, datetime
from typing import Dict, Any

from django.contrib.auth import authenticate
from django.db import IntegrityError

from users.models import User
from users.services.token_service import TokenService
from users.utils.constants import (
    ERR_DUPLICATE_EMAIL,
    ERR_INVALID_CREDENTIALS,
    ERR_ACCOUNT_INACTIVE,
)

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when credentials are invalid or authentication fails."""
    pass


class RegistrationError(Exception):
    """Raised when registration fails due to business rule violations."""
    pass


class AuthService:
    """Stateless service class for authentication operations."""

    @staticmethod
    def register_user(validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new user and return JWT tokens.

        Args:
            validated_data: Cleaned data from RegisterSerializer.

        Returns:
            Dict with 'user' (User instance) and 'tokens' (access + refresh).

        Raises:
            RegistrationError: If the email is already registered.
        """
        email     = validated_data["email"]
        full_name = validated_data["full_name"]
        password  = validated_data["password"]

        # Pre-flight check before DB write to give a clear error
        if User.objects.filter(email=email).exists():
            raise RegistrationError(ERR_DUPLICATE_EMAIL)

        try:
            user = User.objects.create_user(
                email=email,
                full_name=full_name,
                password=password,
                terms_accepted=True,
                terms_accepted_at=datetime.now(tz=timezone.utc),
            )
        except IntegrityError:
            # Race condition guard: another request registered same email
            logger.warning("Race condition on registration for: %s", email)
            raise RegistrationError(ERR_DUPLICATE_EMAIL)
        except Exception as exc:
            logger.exception("Unexpected error during registration: %s", exc)
            raise RegistrationError("Registration failed due to a server error.")

        tokens = TokenService.generate_tokens(user)
        logger.info("New user registered: %s (id=%s)", email, user.id)

        # Trigger async email verification (Celery task — plugged in later)
        # from users.tasks import send_verification_email
        # send_verification_email.delay(str(user.id))

        return {"user": user, "tokens": tokens}

    @staticmethod
    def login_user(validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate a user by email + password.

        Args:
            validated_data: Cleaned data from LoginSerializer.

        Returns:
            Dict with 'user' and 'tokens'.

        Raises:
            AuthenticationError: If credentials are invalid or account is inactive.
        """
        email       = validated_data["email"]
        password    = validated_data["password"]
        remember_me = validated_data.get("remember_me", False)

        user = authenticate(username=email, password=password)

        if user is None:
            # Do NOT reveal whether email exists — generic message only
            logger.warning("Failed login attempt for: %s", email)
            raise AuthenticationError(ERR_INVALID_CREDENTIALS)

        if not user.is_active:
            logger.warning("Login attempt on inactive account: %s", email)
            raise AuthenticationError(ERR_ACCOUNT_INACTIVE)

        # Update last_login_at
        user.last_login_at = datetime.now(tz=timezone.utc)
        user.save(update_fields=["last_login_at"])

        tokens = TokenService.generate_tokens(user, remember_me=remember_me)
        logger.info("User logged in: %s (id=%s)", email, user.id)

        return {"user": user, "tokens": tokens}
