"""
worker/ml_tasks.py
Celery task definitions for asynchronous ML processing.

These tasks are triggered by the Django backend when a request
should be processed in the background (non-blocking response).
"""

from __future__ import annotations

import logging

logger = logging.getLogger("worker.ml_tasks")


def _get_celery_app():
    """Lazy import of the Celery app to avoid circular dependencies."""
    try:
        from backend.core.celery import app
        return app
    except ImportError:
        try:
            from worker.celery_worker import app
            return app
        except ImportError as exc:
            raise RuntimeError(
                "Celery app not found. Ensure backend.core.celery or "
                "worker.celery_worker exports an `app` instance."
            ) from exc


# ──────────────────────────────────────────────────────────────────────────────
# Task definitions
# ──────────────────────────────────────────────────────────────────────────────

def process_avatar_task(file_path: str, job_id: str) -> dict:
    """
    Celery task: run the full avatar preprocessing pipeline.

    Args:
        file_path: Absolute path to the uploaded media file.
        job_id:    Django ProcessingJob UUID string.

    Returns:
        Plain dict from PipelineResult.to_dict().
    """
    app = _get_celery_app()

    @app.task(
        bind            = True,
        name            = "ml_tasks.process_avatar",
        max_retries     = 2,
        default_retry_delay = 30,
        acks_late       = True,
        track_started   = True,
    )
    def _task(self, _file_path: str, _job_id: str) -> dict:
        logger.info("[CeleryTask] process_avatar START | job=%s", _job_id)

        # Update Django DB job status to PROCESSING
        _update_job_status(_job_id, "processing")

        try:
            from services.ml_service import MLServiceError, process_avatar
            result = process_avatar(_file_path, _job_id)
        except Exception as exc:
            logger.exception("[CeleryTask] Avatar pipeline failed for job=%s", _job_id)
            _update_job_status(_job_id, "failed", error=str(exc))
            raise self.retry(exc=exc)

        status = result.get("status", "failure")
        _update_job_status(_job_id, "completed" if status == "success" else "failed")

        logger.info("[CeleryTask] process_avatar END | job=%s | status=%s", _job_id, status)
        return result

    # Register and immediately call (caller receives AsyncResult)
    return _task.apply_async(args=[file_path, job_id])


def process_avatar_sync(file_path: str, job_id: str) -> dict:
    """
    Synchronous (non-Celery) wrapper for environments where Celery is not
    configured.  Called directly from the Django view in development mode.

    Args:
        file_path: Absolute path to the uploaded media file.
        job_id:    Job identifier string.

    Returns:
        Plain dict from PipelineResult.to_dict().
    """
    logger.info("[MLTask-Sync] process_avatar START | job=%s | file=%s", job_id, file_path)
    _update_job_status(job_id, "processing")

    try:
        from services.ml_service import process_avatar
        result = process_avatar(file_path, job_id)
    except Exception as exc:
        logger.exception("[MLTask-Sync] Pipeline crashed for job=%s", job_id)
        _update_job_status(job_id, "failed", error=str(exc))
        raise

    status = result.get("status", "failure")
    _update_job_status(job_id, "completed" if status == "success" else "failed")
    logger.info("[MLTask-Sync] process_avatar END | job=%s | status=%s", job_id, status)
    return result


# ──────────────────────────────────────────────────────────────────────────────
# DB helper
# ──────────────────────────────────────────────────────────────────────────────

def _update_job_status(job_id: str, status: str, error: str = "") -> None:
    """
    Update the Django ProcessingJob record status.
    Fails silently if Django ORM is unavailable (e.g. standalone ML tests).
    """
    try:
        import django
        from django.conf import settings
        if not settings.configured:
            return

        # Import model here to avoid issues when Django is not fully set up
        from processing.models import ProcessingJob  # type: ignore

        ProcessingJob.objects.filter(job_id=job_id).update(
            status        = status,
            error_message = error,
        )
        logger.debug("[MLTask] DB status updated | job=%s → %s", job_id, status)
    except Exception as db_exc:
        logger.warning("[MLTask] Could not update DB status for job=%s: %s", job_id, db_exc)