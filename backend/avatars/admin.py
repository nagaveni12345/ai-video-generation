from django.contrib import admin
from .models import Avatar


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = (
        "avatar_name",
        "gender",
        "age_range",
        "ethnicity",
        "hair_style",
        "avatar_type",
        "avatar_image",
        "status",
    )