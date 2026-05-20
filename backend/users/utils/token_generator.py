"""
users/utils/token_generator.py

Secure token generation utilities for email verification and password reset.
Designed for Redis-backed storage (see PasswordResetService / EmailService).
"""

import secrets
import hashlib


def generate_secure_token(nbytes: int = 32) -> str:
    """
    Generate a URL-safe, cryptographically secure random token.

    Args:
        nbytes: Entropy size in bytes. Default 32 = 256-bit token.

    Returns:
        URL-safe hex string token.
    """
    return secrets.token_urlsafe(nbytes)


def hash_token(token: str) -> str:
    """
    Hash a token with SHA-256 before storing in Redis/DB.
    Prevents raw token exposure if storage is compromised.

    Args:
        token: Raw token string.

    Returns:
        SHA-256 hex digest.
    """
    return hashlib.sha256(token.encode()).hexdigest()


def generate_token_pair() -> tuple[str, str]:
    """
    Generate a (raw_token, hashed_token) pair.
    Send raw_token to user. Store hashed_token in Redis.

    Returns:
        (raw_token, hashed_token) tuple.
    """
    raw = generate_secure_token()
    hashed = hash_token(raw)
    return raw, hashed
