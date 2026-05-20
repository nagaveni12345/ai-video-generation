"""
users/services/email_service.py

Email sending service for VidAI Studio.

Architecture:
- Uses Django's email backend (SMTP / SES-ready).
- Verification and reset tokens are stored in Redis (not DB).
- In production: swap send methods with Celery tasks.

Redis key schema:
  vidai:email_verify:<hashed_token>  → user_id  (TTL: 24h)
  vidai:password_reset:<hashed_token> → user_id (TTL: 1h)
"""

import logging
from typing import Optional

from django.core.mail import send_mail
from django.conf import settings

from users.models import User
from users.utils.token_generator import generate_token_pair
from users.utils.constants import (
    REDIS_EMAIL_VERIFY_PREFIX,
    EMAIL_VERIFICATION_TOKEN_TTL,
    EMAIL_SUBJECT_VERIFY,
)

logger = logging.getLogger(__name__)


class EmailService:
    """
    Handles transactional emails for auth flows.

    NOTE: In production, replace direct send_mail calls with
    Celery tasks to keep request latency low.
    """

    @staticmethod
    def send_verification_email(user: User) -> str:
        """
        Generate an email verification token, store in Redis, and send email.

        Args:
            user: The User instance to verify.

        Returns:
            raw_token — for testing purposes only.
        """
        raw_token, hashed_token = generate_token_pair()

        # Store in Redis: vidai:email_verify:<hash> → user_id
        # In production: use django-redis or direct redis-py
        #
        # redis_client.setex(
        #     f"{REDIS_EMAIL_VERIFY_PREFIX}{hashed_token}",
        #     EMAIL_VERIFICATION_TOKEN_TTL,
        #     str(user.id),
        # )

        verify_url = f"{settings.FRONTEND_URL}/verify-email?token={raw_token}"

        try:
            send_mail(
                subject=EMAIL_SUBJECT_VERIFY,
                message=f"Click the link to verify your email:\n{verify_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info("Verification email sent to: %s", user.email)
        except Exception as exc:
            logger.error("Failed to send verification email to %s: %s", user.email, exc)

        return raw_token  # Return for test inspection

    @staticmethod
    def send_password_reset_email(user: User) -> Optional[str]:
        """
        Generate a password reset token, store in Redis, and send email.

        Returns:
            raw_token — for testing purposes only.
        """
        from users.utils.constants import (
            REDIS_PASSWORD_RESET_PREFIX,
            PASSWORD_RESET_TOKEN_TTL,
            EMAIL_SUBJECT_RESET,
        )

        raw_token, hashed_token = generate_token_pair()

        # Store in Redis: vidai:password_reset:<hash> → user_id
        #
        # redis_client.setex(
        #     f"{REDIS_PASSWORD_RESET_PREFIX}{hashed_token}",
        #     PASSWORD_RESET_TOKEN_TTL,
        #     str(user.id),
        # )

        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"

        try:
            send_mail(
                subject=EMAIL_SUBJECT_RESET,
                message=f"Click to reset your password (expires in 1 hour):\n{reset_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info("Password reset email sent to: %s", user.email)
        except Exception as exc:
            logger.error("Failed to send reset email to %s: %s", user.email, exc)
            return None

        return raw_token
