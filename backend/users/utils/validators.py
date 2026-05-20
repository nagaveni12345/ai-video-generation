"""
users/utils/validators.py

Reusable validation utilities for VidAI Studio auth module.
Kept separate from serializers so they can be used across the codebase.
"""

import re
from rest_framework import serializers

PASSWORD_MIN_LENGTH = 8

PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])"        # at least one lowercase letter
    r"(?=.*[A-Z])"         # at least one uppercase letter
    r"(?=.*\d)"            # at least one digit
    r"(?=.*[@$!%*?&#^])"  # at least one special character
    r".{8,}$"
)

FULL_NAME_REGEX = re.compile(r"^[a-zA-Z\s\-'\.]+$")


def validate_password_strength(password: str) -> None:
    """
    Enforce strong password policy.

    Rules:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character: @$!%*?&#^

    Raises:
        serializers.ValidationError
    """
    if not password:
        raise serializers.ValidationError("Password is required.")

    if len(password) < PASSWORD_MIN_LENGTH:
        raise serializers.ValidationError(
            f"Password must be at least {PASSWORD_MIN_LENGTH} characters long."
        )

    if not PASSWORD_REGEX.match(password):
        raise serializers.ValidationError(
            "Password must contain at least one uppercase letter, one lowercase "
            "letter, one digit, and one special character (@$!%*?&#^)."
        )


def validate_full_name(name: str) -> str:
    """
    Validate full name:
        - Must contain at least one alpha character
        - Only letters, spaces, hyphens, apostrophes, dots allowed
        - Minimum 2 characters

    Returns:
        Stripped, title-cased name.

    Raises:
        serializers.ValidationError
    """
    name = name.strip()

    if len(name) < 2:
        raise serializers.ValidationError("Full name must be at least 2 characters.")

    if not any(char.isalpha() for char in name):
        raise serializers.ValidationError("Name must contain at least one letter.")

    if not FULL_NAME_REGEX.match(name):
        raise serializers.ValidationError(
            "Name can only contain letters, spaces, hyphens, apostrophes, and dots."
        )

    return name


def validate_email_format(email: str) -> str:
    """
    Normalize and validate email format.

    Returns:
        Normalized email string.

    Raises:
        serializers.ValidationError
    """
    email = email.strip().lower()
    email_regex = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

    if not email_regex.match(email):
        raise serializers.ValidationError("Enter a valid email address.")

    return email
