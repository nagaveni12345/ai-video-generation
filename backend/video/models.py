"""
backend/video/models.py
Django ORM models for:
  - Avatar upload and preprocessing job tracking
  - Dashboard project management and statistics
"""

import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


# ──────────────────────────────────────────────────────────────────────────────
# Avatar Processing Models
# ──────────────────────────────────────────────────────────────────────────────

class AvatarUpload(models.Model):
    """
    Stores metadata for a user-uploaded avatar media file
    (image or video).
    """

    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user          = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="avatar_uploads",
        null=True,
        blank=True,
    )
    media_type    = models.CharField(max_length=10, choices=MediaType.choices, default=MediaType.IMAGE)
    original_file = models.FileField(upload_to="avatars/original/%Y/%m/%d/")
    file_name     = models.CharField(max_length=255, blank=True)
    file_size_mb  = models.FloatField(default=0.0)
    uploaded_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering            = ["-uploaded_at"]
        verbose_name        = "Avatar Upload"
        verbose_name_plural = "Avatar Uploads"

    def __str__(self):
        return f"AvatarUpload({self.id}) [{self.media_type}] {self.file_name}"


class ProcessingJob(models.Model):
    """
    Tracks the status of a single avatar preprocessing job.
    One job is created per AvatarUpload.
    """

    class Status(models.TextChoices):
        PENDING    = "pending",    "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED  = "completed",  "Completed"
        FAILED     = "failed",     "Failed"

    id            = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avatar_upload = models.OneToOneField(
        AvatarUpload,
        on_delete=models.CASCADE,
        related_name="processing_job",
    )
    status        = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    error_message = models.TextField(blank=True, default="")

    # Outputs from the ML pipeline (stored as JSON)
    result_metadata = models.JSONField(default=dict, blank=True)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Processed artefact paths (relative to PROCESSED_DIR)
    aligned_face_path = models.CharField(max_length=512, blank=True, default="")
    mouth_crop_path   = models.CharField(max_length=512, blank=True, default="")
    frames_dir        = models.CharField(max_length=512, blank=True, default="")

    class Meta:
        ordering            = ["-created_at"]
        verbose_name        = "Processing Job"
        verbose_name_plural = "Processing Jobs"

    def __str__(self):
        return f"ProcessingJob({self.id}) [{self.status}]"

    @property
    def job_id(self) -> str:
        return str(self.id)


# ──────────────────────────────────────────────────────────────────────────────
# Dashboard Models
# ──────────────────────────────────────────────────────────────────────────────

class DashboardProject(models.Model):
    """Project model for the user dashboard."""

    PROJECT_TYPES = [
        ("text_to_video", "Text to Video"),
        ("record_sync",   "Record & Sync"),
        ("avatar",        "Avatar"),
        ("voice_clone",   "Voice Clone"),
        ("translation",   "Translation"),
    ]

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user         = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dashboard_projects",
    )
    name         = models.CharField(max_length=255)
    project_type = models.CharField(max_length=50, choices=PROJECT_TYPES)

    # Avatar project fields
    avatar_name  = models.CharField(max_length=255, blank=True, null=True)
    avatar_image = models.ImageField(upload_to="avatars/", blank=True, null=True)

    # Voice clone project fields
    voice_name   = models.CharField(max_length=255, blank=True, null=True)

    # Translation project fields
    source_language = models.CharField(max_length=50, blank=True, null=True)
    target_language = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def get_time_ago(self) -> str:
        """Return a human-readable relative timestamp."""
        delta = timezone.now() - self.created_at
        if delta.days > 0:
            return f"{delta.days} days ago"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600} hours ago"
        elif delta.seconds > 60:
            return f"{delta.seconds // 60} minutes ago"
        return "just now"

    def __str__(self):
        return self.name


class DashboardStats(models.Model):
    """Per-user statistics; computed on demand via :meth:`update_stats`."""

    user               = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dashboard_stats",
    )
    total_projects     = models.IntegerField(default=0)
    videos_created     = models.IntegerField(default=0)
    avatars_count      = models.IntegerField(default=0)
    translations_count = models.IntegerField(default=0)
    updated_at         = models.DateTimeField(auto_now=True)

    @classmethod
    def update_stats(cls, user) -> "DashboardStats":
        """Recompute and persist stats for *user*, then return the instance."""
        stats, _ = cls.objects.get_or_create(user=user)
        stats.total_projects = DashboardProject.objects.filter(user=user).count()
        stats.videos_created = DashboardProject.objects.filter(
            user=user,
            project_type__in=["text_to_video", "record_sync"],
        ).count()
        stats.avatars_count = DashboardProject.objects.filter(
            user=user,
            project_type="avatar",
        ).count()
        stats.translations_count = DashboardProject.objects.filter(
            user=user,
            project_type="translation",
        ).count()
        stats.save()
        return stats

    def __str__(self):
        identifier = getattr(self.user, "email", None) or self.user.username
        return f"Stats for {identifier}"