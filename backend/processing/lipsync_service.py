"""
backend/processing/services/lipsync_service.py
===============================================
Synchronous service layer for lip-sync video generation.

Responsibilities:
  1. Resolve avatar_id → artifact storage directory
  2. Resolve audio_id  → absolute WAV path on disk
  3. Create a LipsyncJob DB record
  4. Call the ML pipeline directly (same process, no Celery)
  5. Persist result back to LipsyncJob
  6. Return structured dict to the view

No async. No Celery. No Redis. Everything runs to completion before
this function returns.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Storage root helpers
# ──────────────────────────────────────────────────────────────────────────────

def _storage_root(setting_name: str, default_relative: str) -> Path:
    configured = getattr(settings, setting_name, None)
    if configured:
        return Path(configured).resolve()
    base = Path(settings.BASE_DIR)
    return (base.parent / default_relative).resolve()


_PROCESSED_ROOT = _storage_root("ML_PROCESSED_ROOT", "ml_pipeline/data/processed")
_STORAGE_ROOT   = _storage_root("ML_STORAGE_ROOT",   "ml_pipeline/storage")


# ──────────────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────────────

def run_lipsync_synchronous(user, avatar_id: str, audio_id: str) -> dict:
    """
    Validate inputs, run the full ML pipeline synchronously, persist the result.

    Returns:
        dict with keys:
          success, video_url, video_path, num_frames, duration_sec,
          elapsed_sec, stage_timings, warnings, error (on failure)
    """
    wall_start = time.time()

    # ── 1. Resolve avatar upload → artifact directory key ──────────────────────
    artifact_job_id, err = _resolve_artifact_job_id(avatar_id)
    if artifact_job_id is None:
        return {"success": False, "error": err}

    logger.info(
        "run_lipsync_synchronous: upload_id=%s → artifact_job_id=%s",
        avatar_id, artifact_job_id,
    )

    # ── 2. Validate avatar artifacts exist on disk ─────────────────────────────
    ok, err = _validate_avatar_artifacts(artifact_job_id)
    if not ok:
        return {"success": False, "error": err}

    # ── 3. Resolve audio file path ─────────────────────────────────────────────
    audio_path, err = _resolve_audio_path(user, audio_id)
    if audio_path is None:
        return {"success": False, "error": err}

    # ── 4. Create DB record ────────────────────────────────────────────────────
    try:
        job = _create_job(user, avatar_id, audio_id)
    except Exception as exc:
        logger.exception("Failed to create LipsyncJob record.")
        return {"success": False, "error": f"DB error: {exc}"}

    job.mark_processing()

    # ── 5. Import and run ML pipeline ─────────────────────────────────────────
    try:
        from ml_pipeline.pipelines.lipsync_pipeline import run_lipsync_pipeline  # noqa: PLC0415
    except ImportError as exc:
        err = f"Cannot import lipsync_pipeline: {exc}"
        logger.error(err)
        job.mark_failed(err)
        return {"success": False, "error": err}

    try:
        result = run_lipsync_pipeline(
            job_id     = str(job.job_id),
            avatar_id  = artifact_job_id,
            audio_path = str(audio_path),
        )
    except Exception as exc:
        err = f"Unhandled pipeline error: {exc}"
        logger.exception("ML pipeline crashed for job_id=%s", job.job_id)
        job.mark_failed(err)
        return {"success": False, "error": err}

    # ── 6. Persist result ──────────────────────────────────────────────────────
    if not result.success:
        job.mark_failed(result.error or "Pipeline failed without error message.")
        return {"success": False, "error": result.error}

    video_url = _build_media_url(result.video_path)

    job.mark_completed(
        video_path    = result.video_path,
        video_url     = video_url,
        num_frames    = result.num_frames,
        duration_sec  = result.duration_sec,
        elapsed_sec   = result.elapsed_sec,
        stage_timings = result.stage_timings,
        warnings      = result.warnings,
    )

    total_elapsed = round(time.time() - wall_start, 3)
    logger.info(
        "run_lipsync_synchronous COMPLETE | job=%s  total_elapsed=%.2fs  video=%s",
        job.job_id, total_elapsed, video_url,
    )

    return {
        "success":      True,
        "video_url":    video_url,
        "video_path":   result.video_path,
        "num_frames":   result.num_frames,
        "duration_sec": result.duration_sec,
        "elapsed_sec":  result.elapsed_sec,
        "stage_timings": result.stage_timings,
        "warnings":     result.warnings,
    }


# ──────────────────────────────────────────────────────────────────────────────
# ID resolution helpers
# ──────────────────────────────────────────────────────────────────────────────

def _resolve_artifact_job_id(upload_id: str) -> tuple[str | None, str]:
    """
    Map an avatar identifier to the preprocessing job directory name.

    Tries (in order):
      1. ProcessingJob whose own PK matches directly (frontend sent job_id)
      2. ProcessingJob whose FK avatar_upload__id matches (frontend sent upload_id)
    """
    ProcessingJob = _import_processing_job()
    if ProcessingJob is None:
        return None, "Cannot import ProcessingJob — check INSTALLED_APPS."

    # Strategy 1: direct PK match
    try:
        job = ProcessingJob.objects.get(id=upload_id)
        return str(job.id), ""
    except ProcessingJob.DoesNotExist:
        pass
    except Exception as exc:
        logger.debug("Direct PK lookup failed for %s: %s", upload_id, exc)

    # Strategy 2: FK via AvatarUpload
    try:
        job = ProcessingJob.objects.select_related("avatar_upload").get(
            avatar_upload__id=upload_id
        )
        return str(job.id), ""
    except ProcessingJob.DoesNotExist:
        pass
    except Exception as exc:
        logger.exception("FK lookup error for upload_id=%s", upload_id)
        return None, f"Error resolving preprocessing record: {exc}"

    return None, (
        f"No preprocessing job found for avatar '{upload_id}'. "
        "Ensure avatar preprocessing completed successfully before generating video."
    )


def _import_processing_job():
    import importlib
    for mod_path in ("video.models", "backend.video.models"):
        try:
            mod = importlib.import_module(mod_path)
            return mod.ProcessingJob
        except (ImportError, AttributeError):
            continue
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Validation helpers
# ──────────────────────────────────────────────────────────────────────────────

def _validate_avatar_artifacts(artifact_job_id: str) -> tuple[bool, str]:
    """Confirm preprocessed face and mouth frame directories are non-empty."""
    # Primary layout
    avatar_dir = _PROCESSED_ROOT / "avatar_frames" / artifact_job_id
    mouth_dir  = _PROCESSED_ROOT / "mouth_frames"  / artifact_job_id

    # Fallback layout
    if not avatar_dir.exists():
        avatar_dir = _STORAGE_ROOT / "processed" / artifact_job_id / "faces"
        mouth_dir  = _STORAGE_ROOT / "processed" / artifact_job_id / "mouth_crops"

    if not avatar_dir.exists():
        return False, (
            f"Preprocessed avatar directory not found for job '{artifact_job_id}'. "
            "Please run avatar preprocessing first."
        )

    face_frames = list(avatar_dir.glob("*.jpg")) + list(avatar_dir.glob("*.png"))
    if not face_frames:
        return False, (
            f"No face frames found for job '{artifact_job_id}'. "
            "Please re-run avatar preprocessing."
        )

    mouth_frames = (
        list(mouth_dir.glob("*.jpg")) + list(mouth_dir.glob("*.png"))
        if mouth_dir.exists() else []
    )
    if not mouth_frames:
        return False, (
            f"Mouth crop frames missing for job '{artifact_job_id}'. "
            "Please re-run avatar preprocessing."
        )

    return True, ""


def _resolve_audio_path(user, audio_id: str) -> tuple[Path | None, str]:
    """Locate AudioFile record and return its absolute disk path."""
    import importlib

    AudioFile = None
    for mod_path in (
        "audio_generation.models",
        "backend.audio_generation.models",
        "audio.models",
        "backend.audio.models",
    ):
        try:
            mod = importlib.import_module(mod_path)
            AudioFile = mod.AudioFile
            break
        except (ImportError, AttributeError):
            continue

    if AudioFile is None:
        return None, f"Audio file with id '{audio_id}' not found or access denied."

    try:
        audio_obj = AudioFile.objects.get(pk=audio_id, user=user)
    except AudioFile.DoesNotExist:
        return None, f"Audio file with id '{audio_id}' not found or access denied."
    except Exception as exc:
        return None, f"Error retrieving audio file '{audio_id}': {exc}"

    if not audio_obj.audio_file:
        return None, f"Audio record '{audio_id}' has no file attached."

    abs_path = Path(settings.MEDIA_ROOT) / str(audio_obj.audio_file)
    if not abs_path.exists():
        return None, f"Audio file not found on disk: {abs_path}"

    return abs_path, ""


def _create_job(user, avatar_id: str, audio_id: str):
    from processing.models import LipsyncJob  # noqa: PLC0415

    job = LipsyncJob.objects.create(
        user      = user,
        avatar_id = avatar_id,
        audio_id  = audio_id,
        status    = "pending",
    )
    logger.info("LipsyncJob created: id=%s", job.job_id)
    return job


def _build_media_url(video_path: str) -> str:
    """Convert an absolute path to a Django MEDIA_URL-relative URL."""
    media_root = str(getattr(settings, "MEDIA_ROOT", "media")).rstrip("/\\")
    media_url  = str(getattr(settings, "MEDIA_URL",  "/media/")).rstrip("/")

    vp = video_path.replace("\\", "/")
    mr = media_root.replace("\\", "/")

    if vp.startswith(mr):
        relative = vp[len(mr):].lstrip("/")
        return f"{media_url}/{relative}"
    return video_path
