"""
ml_pipeline/pipelines/avatar_pipeline.py
Top-level pipeline that dispatches uploaded avatar media (image OR video)
to the correct preprocessing chain and returns a unified PipelineResult.
"""

from __future__ import annotations

import time
from pathlib import Path

from ml_pipeline.config.app_config import (
    SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_VIDEO_EXTENSIONS,
)
from ml_pipeline.preprocessing.image_preprocess import preprocess_image
from ml_pipeline.preprocessing.video_preprocess import preprocess_video
from ml_pipeline.utils.file_manager import generate_job_id
from ml_pipeline.utils.logger import get_logger
from ml_pipeline.utils.response_builder import PipelineResult, build_failure

logger = get_logger("avatar_pipeline")


def run_avatar_pipeline(
    file_path: str | Path,
    job_id:    str | None = None,
) -> PipelineResult:
    """
    Entry point for avatar preprocessing.

    Detects whether the uploaded file is an image or video and delegates
    to the appropriate preprocessing module.

    Args:
        file_path: Absolute path to the uploaded file.
        job_id:    Optional job identifier.  A new UUID is generated when
                   not provided.

    Returns:
        :class:`~ml_pipeline.utils.response_builder.PipelineResult`
        containing status, output paths, and metadata.
    """
    start    = time.time()
    path     = Path(file_path)
    job_id   = job_id or generate_job_id()

    logger.info("=== AvatarPipeline START | job=%s | file=%s ===", job_id, path.name)

    # ── Existence check ────────────────────────────────────────────────────────
    if not path.exists():
        msg = f"Uploaded file not found: {path}"
        logger.error("[job=%s] %s", job_id, msg)
        return build_failure(job_id, "unknown", str(path), msg, start_time=start)

    # ── Type dispatch ──────────────────────────────────────────────────────────
    suffix = path.suffix.lower()

    if suffix in SUPPORTED_IMAGE_EXTENSIONS:
        logger.info("[job=%s] Detected media type: IMAGE", job_id)
        result = preprocess_image(path, job_id)

    elif suffix in SUPPORTED_VIDEO_EXTENSIONS:
        logger.info("[job=%s] Detected media type: VIDEO", job_id)
        result = preprocess_video(path, job_id)

    else:
        msg = (
            f"Unsupported file extension '{suffix}'. "
            f"Accepted images: {SUPPORTED_IMAGE_EXTENSIONS}  "
            f"Accepted videos: {SUPPORTED_VIDEO_EXTENSIONS}"
        )
        logger.error("[job=%s] %s", job_id, msg)
        result = build_failure(job_id, "unknown", str(path), msg, start_time=start)

    logger.info(
        "=== AvatarPipeline END | job=%s | status=%s | %.2fs ===",
        job_id, result.status, result.duration_sec,
    )
    return result