"""
ml_pipeline/preprocessing/frame_extractor.py
Extracts individual frames from a video file using OpenCV.
Supports FPS-based sampling and uniform sub-sampling to a target count.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2

from ml_pipeline.config.app_config import (
    FRAME_EXTRACTION_FPS,
    FRAME_QUALITY,
    MAX_FRAMES_TO_EXTRACT,
    STABLE_FRAME_SAMPLE_COUNT,
)
from ml_pipeline.utils.logger import get_logger

logger = get_logger("frame_extractor")


def extract_frames(
    video_path:     str | Path,
    output_dir:     str | Path,
    target_fps:     int            = FRAME_EXTRACTION_FPS,
    max_frames:     int            = MAX_FRAMES_TO_EXTRACT,
    jpeg_quality:   int            = FRAME_QUALITY,
) -> dict:
    """
    Extract frames from a video at (approximately) *target_fps* fps,
    capped at *max_frames*.

    Args:
        video_path:   Path to the source video file.
        output_dir:   Directory where extracted JPEG frames are saved.
        target_fps:   Desired extraction rate (default from app_config).
        max_frames:   Hard cap on total extracted frames.
        jpeg_quality: JPEG write quality (1-100).

    Returns:
        Dict with keys:
          - ``frame_paths``   – list[str] of saved frame paths
          - ``total_frames``  – int, total frames in the video
          - ``extracted``     – int, number of frames actually saved
          - ``video_fps``     – float, native FPS of the video
          - ``duration_sec``  – float
          - ``resolution``    – tuple (width, height)
    """
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise IOError(f"Cannot open video: {video_path}")

    video_fps    = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height       = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration_sec = total_frames / video_fps if video_fps > 0 else 0.0

    logger.info(
        "Video: %s | fps=%.2f | frames=%d | res=%dx%d | dur=%.2fs",
        video_path.name, video_fps, total_frames, width, height, duration_sec,
    )

    # ── Determine which frame indices to save ─────────────────────────────────
    # step = how many source frames to skip per extracted frame
    if video_fps > 0 and target_fps > 0:
        step = max(1, int(round(video_fps / target_fps)))
    else:
        step = 1

    candidate_indices = list(range(0, total_frames, step))
    if len(candidate_indices) > max_frames:
        # uniform sub-sample to stay within max_frames
        import numpy as np
        candidate_indices = [
            candidate_indices[i]
            for i in np.linspace(0, len(candidate_indices) - 1, max_frames, dtype=int)
        ]

    frame_paths: list[str] = []
    saved_count            = 0

    for frame_idx in candidate_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret or frame is None:
            logger.debug("Skipped frame %d (read failed).", frame_idx)
            continue

        out_path = output_dir / f"frame_{frame_idx:06d}.jpg"
        cv2.imwrite(str(out_path), frame, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
        frame_paths.append(str(out_path))
        saved_count += 1

    cap.release()
    logger.info("Extracted %d/%d frames → %s", saved_count, total_frames, output_dir)

    return {
        "frame_paths":   frame_paths,
        "total_frames":  total_frames,
        "extracted":     saved_count,
        "video_fps":     video_fps,
        "duration_sec":  duration_sec,
        "resolution":    (width, height),
    }


def sample_stable_frames(
    frame_paths:  list[str],
    sample_count: int = STABLE_FRAME_SAMPLE_COUNT,
) -> list[str]:
    """
    Uniformly sub-sample *frame_paths* to *sample_count* paths.
    Useful when we want a smaller representative set for face detection.

    Args:
        frame_paths:  Full list of extracted frame file paths.
        sample_count: How many frames to return.

    Returns:
        Sub-sampled list of frame paths (ordered).
    """
    if not frame_paths:
        return []

    if len(frame_paths) <= sample_count:
        return list(frame_paths)

    import numpy as np
    indices = np.linspace(0, len(frame_paths) - 1, sample_count, dtype=int)
    sampled = [frame_paths[i] for i in indices]
    logger.debug("Sampled %d frames from %d total.", len(sampled), len(frame_paths))
    return sampled