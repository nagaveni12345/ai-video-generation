"""
users/migrations/0001_initial.py

Initial migration for the custom User model.
Generated manually to match the model definition precisely.
"""

import uuid
import django.utils.timezone
from django.db import migrations, models
import django.contrib.auth.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False,
                        serialize=False,
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        verbose_name="superuser status",
                        help_text=(
                            "Designates that this user has all permissions "
                            "without explicitly assigning them."
                        ),
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254,
                        unique=True,
                        db_index=True,
                        verbose_name="email address",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        related_name="custom_user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        related_name="custom_user_permission_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "db_table": "users",
                "verbose_name": "User",
                "verbose_name_plural": "Users",
                "ordering": ["-created_at"],
            },
            managers=[
                ("objects", django.contrib.auth.models.BaseUserManager()),
            ],
        ),
    ]
