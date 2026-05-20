"""
users/models.py

Core user model for VidAI Studio.
- UUID primary key
- Email-based authentication
- Email verification tracking
- Password reset token fields moved to dedicated service (Redis-backed)
"""

import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):

    def create_user(
        self,
        email: str,
        full_name: str,
        password: str = None,
        **extra_fields,
    ) -> "User":
        if not email:
            raise ValueError("An email address is required.")
        if not full_name:
            raise ValueError("A full name is required.")

        email = self.normalize_email(email).lower().strip()
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        full_name: str,
        password: str = None,
        **extra_fields,
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model for VidAI Studio.

    Uses email as the primary identifier. Tracks email verification
    status and terms acceptance for compliance.
    """

    class AuthProvider(models.TextChoices):
        EMAIL = "email", "Email"
        GOOGLE = "google", "Google"
        APPLE = "apple", "Apple"

    # Primary key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Core identity
    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255)

    # Account state
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)

    # Auth provider tracking (for social login)
    auth_provider = models.CharField(
        max_length=20,
        choices=AuthProvider.choices,
        default=AuthProvider.EMAIL,
    )

    # Compliance
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.full_name} <{self.email}>"

    def get_full_name(self) -> str:
        return self.full_name

    def get_short_name(self) -> str:
        return self.full_name.split()[0] if self.full_name else ""
