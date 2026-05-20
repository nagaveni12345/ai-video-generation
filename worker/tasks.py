"""
worker/tasks.py
===============
Celery task definitions for the video-generation monorepo.

All heavy ML work is delegated to ml_pipeline.pipelines.* which the
Celery worker imports directly (same process, same venv, same server).
No HTTP calls. No separate inference service.
"""

from __future__ import annotations

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Lip-sync generation task
# ──────────────────────────────────────────────────────────────────────────────

@shared_task(
    bind                  = True,
    # NOTE: task name now reflects the real package name `worker`, not `worker`.
    # If you have existing task results stored under the old name in your
    # result backend, update them or keep a compat alias (see bottom of file).
    name                  = "worker.tasks.run_lipsync_generation_task",
    max_retries           = 2,
    default_retry_delay   = 30,        # seconds between retries
    soft_time_limit       = 1800,      # 30 min  — raises SoftTimeLimitExceeded
    time_limit            = 2100,      # 35 min  — hard SIGKILL
    acks_late             = True,      # only ack after task completes (safe for crashes)
    reject_on_worker_lost = True,      # re-worker if worker dies mid-task
)
def run_lipsync_generation_task(
    self,
    job_id:          str,
    avatar_id:       str,
    audio_path:      str,
    artifact_job_id: str   = "",
    video_fps:       float = 25.0,
) -> dict:
    """
    Asynchronously run Wav2Lip lip-sync inference for one job.

    Parameters
    ----------
    job_id:
        UUID string of the LipsyncJob DB record.
    avatar_id:
        The AvatarUpload.id (kept on the DB record for reference).
    audio_path:
        Absolute path to the preprocessed 16 kHz WAV file on disk.
    artifact_job_id:
        ProcessingJob.id — the storage directory key that holds
        extracted frames and mouth crops.  Falls back to avatar_id
        for backwards compatibility.
    video_fps:
        Frame rate of the avatar source video (default 25 fps).
    """
    resolved_artifact_id = artifact_job_id if artifact_job_id else avatar_id

    logger.info(
        "[task] run_lipsync_generation_task START | "
        "job=%s  upload_id=%s  artifact_job_id=%s  audio=%s",
        job_id, avatar_id, resolved_artifact_id, audio_path,
    )

    # ── Load DB record ────────────────────────────────────────────────────────
    job = _get_job(job_id)
    if job is None:
        logger.error("[task] LipsyncJob not found in DB: job_id=%s", job_id)
        return {"success": False, "error": "Job record not found in database."}

    job.mark_processing()

    # ── Import ML pipeline (deferred to avoid import-time GPU init on
    #    the Django/API process — only the Celery worker process loads this) ──
    try:
        from ml_pipeline.pipelines.lipsync_pipeline import (  # noqa: PLC0415
            run_lipsync_pipeline,
        )
    except ImportError as exc:
        err = f"Failed to import lipsync_pipeline: {exc}"
        logger.exception("[task] %s", err)
        job.mark_failed(err)
        return {"success": False, "error": err}

    # ── Run inference ─────────────────────────────────────────────────────────
    try:
        result = run_lipsync_pipeline(
            job_id     = job_id,
            avatar_id  = resolved_artifact_id,
            audio_path = audio_path,
            video_fps  = video_fps,
        )
    except Exception as exc:
        logger.exception("[task] Unhandled exception in lipsync pipeline.")
        job.mark_failed(f"Unhandled pipeline error: {exc}")
        # Celery will retry up to max_retries times
        raise self.retry(exc=exc)

    # ── Persist result ────────────────────────────────────────────────────────
    if result.success:
        video_url = _build_video_url(result.video_path)
        job.mark_completed(
            video_path    = result.video_path,
            video_url     = video_url,
            num_frames    = result.num_frames,
            duration_sec  = result.duration_sec,
            elapsed_sec   = result.elapsed_sec,
            stage_timings = result.stage_timings,
            warnings      = result.warnings,
        )
        logger.info(
            "[task] DONE | job=%s  elapsed=%.2fs  video=%s",
            job_id, result.elapsed_sec, result.video_path,
        )
    else:
        job.mark_failed(result.error or "Pipeline returned failure without error message.")
        logger.error("[task] FAILED | job=%s  error=%s", job_id, result.error)

    return result.to_dict()


# ──────────────────────────────────────────────────────────────────────────────
# Private helpers
# ──────────────────────────────────────────────────────────────────────────────

def _get_job(job_id: str):
    """
    Load LipsyncJob from the database.
    Returns None (instead of raising) so the task can fail gracefully.
    """
    try:
        # Deferred import: Django ORM must not be touched before
        # django.setup() runs, which happens automatically because
        # celery_app.py sets DJANGO_SETTINGS_MODULE before Celery starts.
        from processing.models import LipsyncJob  # noqa: PLC0415
        return LipsyncJob.objects.get(job_id=job_id)
    except Exception as exc:
        logger.warning("Could not load LipsyncJob job_id=%s: %s", job_id, exc)
        return None


def _build_video_url(video_path: str) -> str:
    """
    Convert an absolute filesystem path to a Django MEDIA_URL-relative URL.
    Falls through and returns the raw path if it cannot be made relative.
    """
    from django.conf import settings  # noqa: PLC0415

    media_root = str(getattr(settings, "MEDIA_ROOT", "media")).rstrip("/")
    media_url  = str(getattr(settings, "MEDIA_URL",  "/media/")).rstrip("/")

    if video_path.startswith(media_root):
        relative = video_path[len(media_root):].lstrip("/")
        return f"{media_url}/{relative}"
    return video_path


# ──────────────────────────────────────────────────────────────────────────────
# Backwards-compat alias
# If you have task results or beat schedules stored under the OLD task name
# "worker.tasks.run_lipsync_generation_task", keep this alias so those
# existing records still resolve.  Remove once all in-flight jobs are done.
# ──────────────────────────────────────────────────────────────────────────────
run_lipsync_generation_task_compat = run_lipsync_generation_task
run_lipsync_generation_task_compat.name = "worker.tasks.run_lipsync_generation_task"