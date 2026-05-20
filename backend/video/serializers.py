"""
backend/video/serializers.py
DRF serializers for:
  - AvatarUpload and ProcessingJob (avatar preprocessing pipeline)
  - DashboardProject and DashboardStats (user dashboard)
"""

from rest_framework import serializers

from .models import AvatarUpload, DashboardProject, DashboardStats, ProcessingJob


# ──────────────────────────────────────────────────────────────────────────────
# Avatar / Processing serializers
# ──────────────────────────────────────────────────────────────────────────────

class AvatarUploadSerializer(serializers.ModelSerializer):
    """Serializer for creating and reading AvatarUpload instances."""

    original_file = serializers.FileField(write_only=True)

    class Meta:
        model  = AvatarUpload
        fields = [
            "id",
            "media_type",
            "original_file",
            "file_name",
            "file_size_mb",
            "uploaded_at",
        ]
        read_only_fields = ["id", "media_type", "file_name", "file_size_mb", "uploaded_at"]

    def validate_original_file(self, value):
        """Reject unsupported extensions before saving to disk."""
        from ml_pipeline.config.app_config import SUPPORTED_EXTENSIONS

        suffix = ("." + value.name.rsplit(".", 1)[-1].lower()) if "." in value.name else ""
        if suffix not in SUPPORTED_EXTENSIONS:
            raise serializers.ValidationError(
                f"Unsupported file type '{suffix}'. "
                f"Allowed: {sorted(SUPPORTED_EXTENSIONS)}"
            )
        return value


class ProcessingJobSerializer(serializers.ModelSerializer):
    """Read-only serializer for ProcessingJob status and outputs."""

    class Meta:
        model  = ProcessingJob
        fields = [
            "id",
            "status",
            "error_message",
            "result_metadata",
            "aligned_face_path",
            "mouth_crop_path",
            "frames_dir",
            "created_at",
            "updated_at",
            "completed_at",
        ]
        read_only_fields = fields


class ProcessAvatarResponseSerializer(serializers.Serializer):
    """Response body for POST /api/video/process-avatar/."""

    job_id     = serializers.UUIDField()
    status     = serializers.CharField()
    message    = serializers.CharField()
    upload_id  = serializers.UUIDField()
    async_mode = serializers.BooleanField()


# ──────────────────────────────────────────────────────────────────────────────
# Dashboard serializers
# ──────────────────────────────────────────────────────────────────────────────

class DashboardProjectSerializer(serializers.ModelSerializer):
    """Serializer for dashboard projects, including computed display fields."""

    time_ago             = serializers.SerializerMethodField()
    project_type_display = serializers.SerializerMethodField()

    class Meta:
        model  = DashboardProject
        fields = [
            "id",
            "name",
            "project_type",
            "project_type_display",
            "avatar_name",
            "avatar_image",
            "voice_name",
            "source_language",
            "target_language",
            "created_at",
            "time_ago",
        ]

    def get_time_ago(self, obj) -> str:
        return obj.get_time_ago()

    def get_project_type_display(self, obj) -> str:
        return dict(DashboardProject.PROJECT_TYPES).get(obj.project_type, obj.project_type)


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""

    total_projects     = serializers.IntegerField()
    videos_created     = serializers.IntegerField()
    avatars_count      = serializers.IntegerField()
    translations_count = serializers.IntegerField()


class DashboardResponseSerializer(serializers.Serializer):
    """Complete dashboard response serializer."""

    stats    = DashboardStatsSerializer()
    projects = DashboardProjectSerializer(many=True)