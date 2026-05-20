from django.db import models
from django.conf import settings


class Avatar(models.Model):

    # ===============================
    # AVATAR TYPE
    # ===============================
    AVATAR_TYPES = (
        ("ai", "AI Avatar"),
        ("image", "Image Upload"),
        ("video", "Video Upload"),
    )

    # ===============================
    # FILTER CHOICES (NEW)
    # ===============================
    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
    )

    ETHNICITY_CHOICES = (
        ("diverse", "Diverse"),
        ("asian", "Asian"),
        ("caucasian", "Caucasian"),
        ("african", "African"),
        ("hispanic", "Hispanic"),
        ("middle_eastern", "Middle Eastern"),
    )

    HAIR_STYLE_CHOICES = (
        ("long", "Long"),
        ("short", "Short"),
        ("curly", "Curly"),
        ("bald", "Bald"),
    )

    AGE_RANGE_CHOICES = (
        ("18-25", "18-25"),
        ("26-35", "26-35"),
        ("36-45", "36-45"),
        ("46-55", "46-55"),
        ("56-70", "56-70"),
    )

    # ===============================
    # BASIC INFO
    # ===============================
    avatar_name = models.CharField(max_length=100)

    # FIX ✅ default must exist in choices
    avatar_type = models.CharField(
        max_length=20,
        choices=AVATAR_TYPES,
        default="ai",
    )

    # ===============================
    # FILTER FIELDS (ADMIN MATCHING)
    # ===============================
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
    )

    age_range = models.CharField(
        max_length=20,
        choices=AGE_RANGE_CHOICES,
        blank=True,
        null=True,
    )

    ethnicity = models.CharField(
        max_length=50,
        choices=ETHNICITY_CHOICES,
        blank=True,
        null=True,
    )

    hair_style = models.CharField(
        max_length=50,
        choices=HAIR_STYLE_CHOICES,
        blank=True,
        null=True,
    )

    # ===============================
    # ADMIN AVATAR IMAGE
    # ===============================
    avatar_image = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True,
    )

    # ===============================
    # USER UPLOADS
    # ===============================
    user_image = models.ImageField(
        upload_to="user_avatars/",
        null=True,
        blank=True,
    )

    user_video = models.FileField(
        upload_to="user_videos/",
        null=True,
        blank=True,
    )

    status = models.CharField(
        default="pending",
        max_length=20,
    )

    # FIX ✅ REMOVE INVALID UUID DEFAULT
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.avatar_name