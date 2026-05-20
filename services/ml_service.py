"""
services/ml_service.py
Communication layer between the Django backend and the ml_pipeline.

This module is the ONLY entry-point from the backend to the ML subsystem.
It deliberately imports from ml_pipeline at call-time to avoid circular
imports and to keep Django boot-up fast.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("services.ml_service")


class MLServiceError(Exception):
    """Raised when the ML service encounters an unrecoverable error."""


def process_avatar(
    file_path: str | Path,
    job_id:    str,
) -> dict[str, Any]:
    """
    Trigger the avatar preprocessing pipeline for a given uploaded file.

    This function is called by the Django backend API view (or a Celery
    task if async processing is preferred).

    Args:
        file_path: Absolute path to the uploaded media file.
        job_id:    Unique identifier for this processing job (should match
                   the Django ProcessingJob primary key or UUID).

    Returns:
        Plain dictionary derived from
        :class:`~ml_pipeline.utils.response_builder.PipelineResult`.

    Raises:
        MLServiceError: if the pipeline raises an unhandled exception.
    """
    logger.info("[MLService] process_avatar called | job_id=%s | file=%s", job_id, file_path)

    try:
        # Import here to avoid loading heavy ML dependencies at Django boot
        from ml_pipeline.pipelines.avatar_pipeline import run_avatar_pipeline

        result = run_avatar_pipeline(file_path=file_path, job_id=job_id)
    except Exception as exc:
        logger.exception("[MLService] Unhandled exception in avatar pipeline.")
        raise MLServiceError(f"Avatar pipeline crashed: {exc}") from exc

    result_dict = result.to_dict()
    logger.info(
        "[MLService] process_avatar finished | job_id=%s | status=%s | duration=%.2fs",
        job_id, result.status, result.duration_sec,
    )
    return result_dict


def get_processing_status(job_id: str) -> dict[str, Any]:
    """
    Convenience helper to query whether processed artefacts exist on disk
    for a given job_id.

    Returns a lightweight status dict (does not re-run any ML code).
    """
    from ml_pipeline.config.app_config import PROCESSED_DIR

    job_root = Path(PROCESSED_DIR) / job_id
    if not job_root.exists():
        return {"job_id": job_id, "exists": False, "artefacts": {}}

    artefacts: dict[str, Any] = {}
    for sub in ("frames", "faces", "mouth_crops"):
        sub_dir = job_root / sub
        if sub_dir.exists():
            artefacts[sub] = [str(p) for p in sorted(sub_dir.iterdir()) if p.is_file()]
        else:
            artefacts[sub] = []

    return {"job_id": job_id, "exists": True, "artefacts": artefacts}


def cleanup_job(job_id: str) -> None:
    """
    Remove all on-disk artefacts for the given job.
    Delegates to the file_manager utility.
    """
    from ml_pipeline.utils.file_manager import cleanup_job as _cleanup

    logger.info("[MLService] Cleaning up artefacts for job_id=%s", job_id)
    _cleanup(job_id)