"""
ml_pipeline/utils/file_manager.py
File-system helpers: job directory creation, safe copy/move, cleanup.
"""

import shutil
import uuid
from pathlib import Path
from typing import Optional

from ml_pipeline.config.app_config import PROCESSED_DIR, TEMP_DIR, EXPORTS_DIR
from ml_pipeline.utils.logger import get_logger

logger = get_logger("file_manager")


# ──────────────────────────────────────────────────────────────────────────────
# Job directory helpers
# ──────────────────────────────────────────────────────────────────────────────

def create_job_directories(job_id: str) -> dict[str, Path]:
    """
    Create and return all sub-directories required for a single processing job.

    Directory layout::

        ml_pipeline/storage/
          processed/{job_id}/
            frames/
            faces/
            mouth_crops/
          temp/{job_id}/
          exports/{job_id}/

    Returns:
        Mapping of directory-role → absolute Path.
    """
    dirs: dict[str, Path] = {
        "job_root":        PROCESSED_DIR / job_id,
        "frames":          PROCESSED_DIR / job_id / "frames",
        "faces":           PROCESSED_DIR / job_id / "faces",
        "original_frames": PROCESSED_DIR / job_id / "original_frames",
        "mouth_crops":     PROCESSED_DIR / job_id / "mouth_crops",
        "temp":            TEMP_DIR      / job_id,
        "exports":         EXPORTS_DIR   / job_id,
    }

    for role, path in dirs.items():
        path.mkdir(parents=True, exist_ok=True)
        logger.debug("Created directory [%s]: %s", role, path)

    logger.info("Job directories ready for job_id=%s", job_id)
    return dirs


def generate_job_id() -> str:
    """Return a new UUID4 string to be used as a job identifier."""
    return str(uuid.uuid4())


# ──────────────────────────────────────────────────────────────────────────────
# File operations
# ──────────────────────────────────────────────────────────────────────────────

def safe_copy(src: Path, dst: Path) -> Path:
    """
    Copy *src* to *dst*, creating parent directories as needed.

    Returns the destination path.
    Raises FileNotFoundError if *src* does not exist.
    """
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    logger.debug("Copied %s → %s", src, dst)
    return dst


def safe_move(src: Path, dst: Path) -> Path:
    """
    Move *src* to *dst*, creating parent directories as needed.

    Returns the destination path.
    """
    if not src.exists():
        raise FileNotFoundError(f"Source file not found: {src}")

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    logger.debug("Moved %s → %s", src, dst)
    return dst


def cleanup_job_temp(job_id: str) -> None:
    """Remove the temp directory for the given job to free disk space."""
    temp_path = TEMP_DIR / job_id
    if temp_path.exists():
        shutil.rmtree(temp_path, ignore_errors=True)
        logger.info("Cleaned up temp directory for job_id=%s", job_id)


def cleanup_job(job_id: str) -> None:
    """Remove ALL storage artefacts for a job (processed, temp, exports)."""
    for base_dir in (PROCESSED_DIR, TEMP_DIR, EXPORTS_DIR):
        target = base_dir / job_id
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)
            logger.info("Removed %s for job_id=%s", target, job_id)


# ──────────────────────────────────────────────────────────────────────────────
# Metadata helpers
# ──────────────────────────────────────────────────────────────────────────────

def list_files(directory: Path, extension: Optional[str] = None) -> list[Path]:
    """
    Return sorted list of files in *directory*.

    Args:
        directory: The target directory path.
        extension: If provided (e.g. ".jpg"), filter by this extension.
    """
    if not directory.exists():
        logger.warning("Directory does not exist: %s", directory)
        return []

    files = sorted(directory.iterdir())
    if extension:
        ext = extension.lower()
        files = [f for f in files if f.suffix.lower() == ext]

    return [f for f in files if f.is_file()]


def get_file_size_mb(path: Path) -> float:
    """Return file size in megabytes."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.stat().st_size / (1024 * 1024)