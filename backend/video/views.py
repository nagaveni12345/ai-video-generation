"""
backend/video/views.py
Django REST Framework views for:
  - Avatar upload and preprocessing  (ProcessAvatarView, ProcessingJobStatusView)
  - Dashboard projects and stats     (DashboardView, CreateProjectView,
                                      DeleteProjectView, ProjectStatsView)
  - Video job management             (generate_video, get_job_status,
                                      list_jobs, cancel_job)

Endpoints summary
-----------------
POST   /api/video/process-avatar/                  → upload + trigger preprocessing
GET    /api/video/process-avatar/<job_id>/         → poll preprocessing job status
GET    /api/video/dashboard/                       → stats + recent projects
GET    /api/video/dashboard/stats/                 → stats only
POST   /api/video/dashboard/projects/              → create project
DELETE /api/video/dashboard/projects/<project_id>/ → delete project
POST   /api/video/generate/                        → trigger video generation job
GET    /api/video/jobs/<job_id>/                   → get video job status
GET    /api/video/jobs/                            → list video jobs
POST   /api/video/jobs/<job_id>/cancel/            → cancel video job
"""

from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AvatarUpload, DashboardProject, DashboardStats, ProcessingJob
from .serializers import (
    AvatarUploadSerializer,
    DashboardProjectSerializer,
    DashboardStatsSerializer,
    ProcessAvatarResponseSerializer,
    ProcessingJobSerializer,
)

logger = logging.getLogger("backend.video.views")

# ---------------------------------------------------------------------------
# Feature flag: set AVATAR_ASYNC=true in .env to process via Celery worker
# ---------------------------------------------------------------------------
_ASYNC_MODE = os.getenv("AVATAR_ASYNC", "false").lower() == "true"


# ──────────────────────────────────────────────────────────────────────────────
# Avatar preprocessing views
# ──────────────────────────────────────────────────────────────────────────────

class ProcessAvatarView(APIView):
    """
    POST /api/video/process-avatar/

    Accepts a multipart/form-data request with a single field ``file``
    containing the avatar image or video.

    Response (202 Accepted)::

        {
          "job_id":     "<uuid>",
          "status":     "accepted",
          "message":    "Avatar queued for processing.",
          "upload_id":  "<uuid>",
          "async_mode": true | false
        }
    """

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request: Request) -> Response:
        uploaded_file = request.FILES.get("file")

        if uploaded_file is None:
            return Response(
                {"error": "No file provided. Include a 'file' field in the multipart request."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Validate & create AvatarUpload record ─────────────────────────────
        serializer = AvatarUploadSerializer(data={"original_file": uploaded_file})
        if not serializer.is_valid():
            logger.warning("AvatarUpload validation failed: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Determine media type from extension
        suffix = Path(uploaded_file.name).suffix.lower()
        from ml_pipeline.config.app_config import (
            SUPPORTED_IMAGE_EXTENSIONS,
            SUPPORTED_VIDEO_EXTENSIONS,
        )
        if suffix in SUPPORTED_IMAGE_EXTENSIONS:
            media_type = AvatarUpload.MediaType.IMAGE
        elif suffix in SUPPORTED_VIDEO_EXTENSIONS:
            media_type = AvatarUpload.MediaType.VIDEO
        else:
            media_type = AvatarUpload.MediaType.IMAGE  # fallback; validator already approved it

        avatar_upload = AvatarUpload.objects.create(
            user          = request.user if request.user.is_authenticated else None,
            original_file = uploaded_file,
            file_name     = uploaded_file.name,
            file_size_mb  = round(uploaded_file.size / (1024 * 1024), 3),
            media_type    = media_type,
        )
        logger.info("AvatarUpload created: id=%s file=%s", avatar_upload.id, avatar_upload.file_name)

        # ── Create ProcessingJob ───────────────────────────────────────────────
        job      = ProcessingJob.objects.create(avatar_upload=avatar_upload)
        job_id   = str(job.id)
        file_path = str(Path(avatar_upload.original_file.path).resolve())

        logger.info("ProcessingJob created: id=%s | async=%s", job_id, _ASYNC_MODE)

        # ── Dispatch to ML pipeline ────────────────────────────────────────────
        if _ASYNC_MODE:
            _dispatch_async(file_path, job_id)
            message = "Avatar queued for background processing."
        else:
            _dispatch_sync(file_path, job_id, job)
            message = "Avatar processed synchronously."

        response_data = {
            "job_id":     job.id,
            "status":     "accepted",
            "message":    message,
            "upload_id":  avatar_upload.id,
            "async_mode": _ASYNC_MODE,
        }
        return Response(
            ProcessAvatarResponseSerializer(response_data).data,
            status=status.HTTP_202_ACCEPTED,
        )


class ProcessingJobStatusView(APIView):
    """
    GET /api/video/process-avatar/<job_id>/

    Returns the current status and output metadata for a preprocessing job.
    """

    def get(self, request: Request, job_id: str) -> Response:
        try:
            uuid.UUID(job_id)
        except ValueError:
            return Response({"error": "Invalid job_id format."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            job = ProcessingJob.objects.select_related("avatar_upload").get(id=job_id)
        except ProcessingJob.DoesNotExist:
            return Response({"error": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(ProcessingJobSerializer(job).data, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────────────────────────────────────
# Dashboard views
# ──────────────────────────────────────────────────────────────────────────────

class DashboardView(APIView):
    """
    GET /api/video/dashboard/

    Returns dashboard statistics and recent projects (up to 20).
    Supports optional ``?type=<project_type>`` query param for filtering.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        try:
            user  = request.user
            stats = DashboardStats.update_stats(user)

            projects = DashboardProject.objects.filter(user=user)

            project_type = request.query_params.get("type", "all")
            if project_type != "all":
                projects = projects.filter(project_type=project_type)

            projects = projects[:20]

            stats_data = {
                "total_projects":     stats.total_projects,
                "videos_created":     stats.videos_created,
                "avatars_count":      stats.avatars_count,
                "translations_count": stats.translations_count,
            }

            return Response(
                {
                    "success": True,
                    "data": {
                        "stats":    stats_data,
                        "projects": DashboardProjectSerializer(projects, many=True).data,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            logger.error("Dashboard error: %s", exc)
            return Response(
                {"success": False, "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CreateProjectView(APIView):
    """
    POST /api/video/dashboard/projects/

    Create a new dashboard project.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        try:
            user = request.user
            data = request.data

            project = DashboardProject.objects.create(
                user            = user,
                name            = data.get("name"),
                project_type    = data.get("project_type"),
                avatar_name     = data.get("avatar_name", ""),
                voice_name      = data.get("voice_name", ""),
                source_language = data.get("source_language", ""),
                target_language = data.get("target_language", ""),
            )

            DashboardStats.update_stats(user)

            return Response(
                {"success": True, "data": DashboardProjectSerializer(project).data},
                status=status.HTTP_201_CREATED,
            )

        except Exception as exc:
            logger.error("Create project error: %s", exc)
            return Response(
                {"success": False, "error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class DeleteProjectView(APIView):
    """
    DELETE /api/video/dashboard/projects/<project_id>/

    Delete a dashboard project owned by the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request: Request, project_id: str) -> Response:
        try:
            project = DashboardProject.objects.get(
                id=uuid.UUID(project_id),
                user=request.user,
            )
            project.delete()
            DashboardStats.update_stats(request.user)
            return Response(
                {"success": True, "message": "Project deleted successfully."},
                status=status.HTTP_200_OK,
            )

        except DashboardProject.DoesNotExist:
            return Response(
                {"success": False, "error": "Project not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as exc:
            logger.error("Delete project error: %s", exc)
            return Response(
                {"success": False, "error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ProjectStatsView(APIView):
    """
    GET /api/video/dashboard/stats/

    Returns only the dashboard statistics for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        try:
            stats = DashboardStats.update_stats(request.user)
            return Response(
                {
                    "success": True,
                    "data": {
                        "total_projects":     stats.total_projects,
                        "videos_created":     stats.videos_created,
                        "avatars_count":      stats.avatars_count,
                        "translations_count": stats.translations_count,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as exc:
            return Response(
                {"success": False, "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ──────────────────────────────────────────────────────────────────────────────
# Video generation job views (function-based for flexibility)
# ──────────────────────────────────────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_video(request: Request) -> Response:
    """
    POST /api/video/generate/

    Trigger a full video generation job. Stub — wire up to your Celery task.
    """
    # TODO: validate request.data, create a job record, dispatch to queue
    return Response(
        {"success": True, "message": "Video generation job accepted."},
        status=status.HTTP_202_ACCEPTED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_job_status(request: Request, job_id: uuid.UUID) -> Response:
    """
    GET /api/video/jobs/<job_id>/

    Return the status of a video generation job.
    """
    try:
        job = ProcessingJob.objects.get(id=job_id)
    except ProcessingJob.DoesNotExist:
        return Response({"error": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

    return Response(ProcessingJobSerializer(job).data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_jobs(request: Request) -> Response:
    """
    GET /api/video/jobs/

    List all processing jobs for the authenticated user.
    """
    jobs = ProcessingJob.objects.filter(
        avatar_upload__user=request.user
    ).select_related("avatar_upload").order_by("-created_at")

    return Response(
        ProcessingJobSerializer(jobs, many=True).data,
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_job(request: Request, job_id: uuid.UUID) -> Response:
    """
    POST /api/video/jobs/<job_id>/cancel/

    Cancel a pending or processing job.
    """
    try:
        job = ProcessingJob.objects.get(id=job_id, avatar_upload__user=request.user)
    except ProcessingJob.DoesNotExist:
        return Response({"error": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

    if job.status not in (ProcessingJob.Status.PENDING, ProcessingJob.Status.PROCESSING):
        return Response(
            {"error": f"Cannot cancel a job with status '{job.status}'."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    job.status        = ProcessingJob.Status.FAILED
    job.error_message = "Cancelled by user."
    job.completed_at  = timezone.now()
    job.save(update_fields=["status", "error_message", "completed_at", "updated_at"])

    return Response({"success": True, "message": "Job cancelled."}, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────────────────────────────────────
# Internal dispatch helpers
# ──────────────────────────────────────────────────────────────────────────────

def _dispatch_async(file_path: str, job_id: str) -> None:
    """Send the preprocessing job to the Celery worker."""
    try:
        from worker.ml_tasks import process_avatar_task
        process_avatar_task.delay(file_path, job_id)
        logger.info("Job dispatched to Celery: job_id=%s", job_id)
    except Exception as exc:
        logger.exception("Failed to dispatch Celery task for job_id=%s: %s", job_id, exc)
        ProcessingJob.objects.filter(id=job_id).update(
            status=ProcessingJob.Status.FAILED,
            error_message=f"Celery dispatch error: {exc}",
        )


def _dispatch_sync(file_path: str, job_id: str, job: ProcessingJob) -> None:
    """Process synchronously in the current request thread (development / testing)."""
    from services.ml_service import MLServiceError, process_avatar

    try:
        result = process_avatar(file_path, job_id)
    except MLServiceError as exc:
        logger.error("Sync pipeline failed for job_id=%s: %s", job_id, exc)
        job.status        = ProcessingJob.Status.FAILED
        job.error_message = str(exc)
        job.save(update_fields=["status", "error_message", "updated_at"])
        return

    pipeline_status = result.get("status", "failure")
    outputs         = result.get("outputs", {})

    job.status            = (
        ProcessingJob.Status.COMPLETED if pipeline_status == "success"
        else ProcessingJob.Status.FAILED
    )
    job.result_metadata   = result
    job.aligned_face_path = outputs.get("aligned_face_path", "")
    job.mouth_crop_path   = outputs.get("mouth_crop_path", "")
    job.frames_dir        = outputs.get("frames_dir", "")
    job.error_message     = "; ".join(result.get("errors", []))
    job.completed_at      = timezone.now()
    job.save()

    logger.info("Sync job done: job_id=%s | status=%s", job_id, job.status)