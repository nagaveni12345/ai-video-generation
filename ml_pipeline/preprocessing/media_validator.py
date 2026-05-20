"""
ml_pipeline/preprocessing/media_validator.py
Validates uploaded image and video files before processing.
"""

from __future__ import annotations

from pathlib import Path

import cv2

from ml_pipeline.config.app_config import (
    MAX_IMAGE_SIZE_BYTES,
    MAX_VIDEO_SIZE_BYTES,
    SUPPORTED_IMAGE_EXTENSIONS,
    SUPPORTED_VIDEO_EXTENSIONS,
)
from ml_pipeline.utils.logger import get_logger

logger = get_logger("media_validator")


class ValidationError(Exception):
    """Raised when a media file fails validation."""


def validate_media(file_path: str | Path) -> str:
    """
    Validate a media file and return its type.

    Args:
        file_path: Absolute path to the uploaded file.

    Returns:
        ``"image"`` or ``"video"``

    Raises:
        ValidationError: on any validation failure.
        FileNotFoundError: if the file does not exist.
    """
    path = Path(file_path)

    # ── Existence ──────────────────────────────────────────────────────────────
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not path.is_file():
        raise ValidationError(f"Path is not a file: {path}")

    # ── Extension ─────────────────────────────────────────────────────────────
    suffix = path.suffix.lower()
    if suffix in SUPPORTED_IMAGE_EXTENSIONS:
        media_type = "image"
    elif suffix in SUPPORTED_VIDEO_EXTENSIONS:
        media_type = "video"
    else:
        raise ValidationError(
            f"Unsupported file extension '{suffix}'. "
            f"Supported: {SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_VIDEO_EXTENSIONS}"
        )

    # ── File size ─────────────────────────────────────────────────────────────
    size_bytes = path.stat().st_size
    if size_bytes == 0:
        raise ValidationError("File is empty (0 bytes).")

    if media_type == "image" and size_bytes > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(
            f"Image exceeds maximum allowed size "
            f"({size_bytes / 1e6:.1f} MB > {MAX_IMAGE_SIZE_BYTES / 1e6:.0f} MB)."
        )

    if media_type == "video" and size_bytes > MAX_VIDEO_SIZE_BYTES:
        raise ValidationError(
            f"Video exceeds maximum allowed size "
            f"({size_bytes / 1e6:.1f} MB > {MAX_VIDEO_SIZE_BYTES / 1e6:.0f} MB)."
        )

    # ── Content integrity ─────────────────────────────────────────────────────
    if media_type == "image":
        _validate_image_content(path)
    else:
        _validate_video_content(path)

    logger.info("Validation passed: %s (%s, %.2f MB)", path.name, media_type, size_bytes / 1e6)
    return media_type


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _validate_image_content(path: Path) -> None:
    """Attempt to decode image with OpenCV; raise ValidationError on failure."""
    img = cv2.imread(str(path))
    if img is None:
        raise ValidationError(
            f"OpenCV could not read the image file '{path.name}'. "
            "The file may be corrupt or an unsupported format."
        )
    h, w = img.shape[:2]
    if h < 64 or w < 64:
        raise ValidationError(
            f"Image resolution {w}×{h} is too small (minimum 64×64 pixels)."
        )
    logger.debug("Image OK: %s  resolution=%dx%d", path.name, w, h)


def _validate_video_content(path: Path) -> None:
    """Open video with OpenCV; validate it has readable frames."""
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValidationError(
            f"OpenCV could not open the video file '{path.name}'. "
            "The file may be corrupt or an unsupported codec."
        )

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps         = cap.get(cv2.CAP_PROP_FPS)
    width       = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height      = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    if frame_count <= 0:
        raise ValidationError(
            f"Video '{path.name}' reports 0 frames. The file may be corrupt."
        )
    if fps <= 0:
        raise ValidationError(
            f"Video '{path.name}' has an invalid FPS ({fps}). "
            "The file may be corrupt."
        )
    if width < 64 or height < 64:
        raise ValidationError(
            f"Video resolution {width}×{height} is too small (minimum 64×64)."
        )

    logger.debug(
        "Video OK: %s  frames=%d  fps=%.2f  resolution=%dx%d",
        path.name, frame_count, fps, width, height,
    )