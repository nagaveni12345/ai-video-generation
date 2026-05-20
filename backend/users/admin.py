"""
users/admin.py

Django admin configuration for the User model.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display  = ["email", "full_name", "auth_provider", "is_email_verified",
                     "is_active", "is_staff", "created_at"]
    list_filter   = ["is_active", "is_staff", "is_email_verified", "auth_provider", "created_at"]
    search_fields = ["email", "full_name"]
    ordering      = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at", "last_login_at", "terms_accepted_at"]

    fieldsets = (
        (None,              {"fields": ("id", "email", "password")}),
        ("Personal Info",   {"fields": ("full_name",)}),
        ("Auth Provider",   {"fields": ("auth_provider",)}),
        ("Verification",    {"fields": ("is_email_verified",)}),
        ("Compliance",      {"fields": ("terms_accepted", "terms_accepted_at")}),
        ("Permissions",     {"fields": ("is_active", "is_staff", "is_superuser",
                                       "groups", "user_permissions")}),
        ("Timestamps",      {"fields": ("created_at", "updated_at", "last_login_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "password1", "password2",
                       "is_active", "is_staff", "is_email_verified"),
        }),
    )

    filter_horizontal = ("groups", "user_permissions")
