"""
users/services/password_reset_service.py

Handles forgot-password and reset-password flows.

Token storage:
- Tokens are stored in Redis (hashed) with TTL.
- Raw token is sent via email; hashed token is looked up on reset.

Current implementation: DB-based stub for environments without Redis.
Production: swap stub with Redis-backed implementation (commented below).
"""

import logging
from typing import Optional

from users.models import User
from users.services.email_service import EmailService
from users.utils.token_generator import hash_token
from users.utils.constants import ERR_INVALID_RESET_TOKEN

logger = logging.getLogger(__name__)


class PasswordResetError(Exception):
    """Raised when a password reset operation fails."""
    pass


class PasswordResetService:
    """
    Stateless service for password reset lifecycle.
    """

    @staticmethod
    def initiate_reset(email: str) -> None:
        """
        Trigger the password reset flow for the given email.

        Security: Always returns success response regardless of
        whether the email is registered (prevents user enumeration).

        Args:
            email: Normalized email address.
        """
        user: Optional[User] = User.objects.filter(email=email, is_active=True).first()

        if user:
            EmailService.send_password_reset_email(user)
            logger.info("Password reset initiated for: %s", email)
        else:
            # Silently swallow — do not reveal email existence
            logger.info("Password reset requested for unknown email: %s", email)

    @staticmethod
    def confirm_reset(raw_token: str, new_password: str) -> None:
        """
        Validate the reset token and set the new password.

        Args:
            raw_token: Token from the reset link.
            new_password: Already-validated new password.

        Raises:
            PasswordResetError: If token is invalid or expired.
        """
        hashed = hash_token(raw_token)

        # --- Redis-backed lookup (production) ---
        # redis_key = f"{REDIS_PASSWORD_RESET_PREFIX}{hashed}"
        # user_id = redis_client.get(redis_key)
        # if not user_id:
        #     raise PasswordResetError(ERR_INVALID_RESET_TOKEN)
        # user = User.objects.filter(id=user_id, is_active=True).first()
        # if not user:
        #     raise PasswordResetError(ERR_INVALID_RESET_TOKEN)
        # redis_client.delete(redis_key)  # Single-use

        # --- DB-based stub (development fallback) ---
        # Replace this block with the Redis implementation above.
        raise PasswordResetError(
            "Password reset service requires Redis. "
            "Connect a Redis instance and enable the Redis-backed implementation."
        )

        # user.set_password(new_password)
        # user.save(update_fields=["password"])
        # logger.info("Password reset successful for user id: %s", user.id)
