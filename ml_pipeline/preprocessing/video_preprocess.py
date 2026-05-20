"""
ml_pipeline/preprocessing/video_preprocess.py
Full preprocessing chain for a single uploaded avatar VIDEO.

Steps:
  1. Validate the file
  2. Extract all frames
  3. Sample stable frames
  4. Detect faces in every sampled frame
  5. Align each detected face and save
  6. Extract mouth crop from each aligned face
  7. Return structured metadata
"""

from __future__ import annotations

import time
from pathlib import Path

import cv2

from ml_pipeline.config.app_config import (
    FACE_PADDING_RATIO,
    STABLE_FRAME_SAMPLE_COUNT,
    TARGET_FACE_SIZE,
    TARGET_MOUTH_SIZE,
)
from ml_pipeline.preprocessing.face_alignment import align_face, save_aligned_face
from ml_pipeline.preprocessing.face_detection import detect_faces
from ml_pipeline.preprocessing.frame_extractor import extract_frames, sample_stable_frames
from ml_pipeline.preprocessing.media_validator import ValidationError, validate_media
from ml_pipeline.preprocessing.mouth_cropper import extract_mouth_crop, save_mouth_crop
from ml_pipeline.utils.file_manager import create_job_directories
from ml_pipeline.utils.logger import get_logger
from ml_pipeline.utils.response_builder import (
    PipelineResult,
    VideoProcessingOutputs,
    build_failure,
    build_success,
)

logger = get_logger("video_preprocess")


def preprocess_video(
    file_path: str | Path,
    job_id:    str,
) -> PipelineResult:
    """
    Run the full preprocessing pipeline for an uploaded avatar video.

    Args:
        file_path: Absolute path to the uploaded video file.
        job_id:    Unique job identifier.

    Returns:
        :class:`~ml_pipeline.utils.response_builder.PipelineResult`.
    """
    start = time.time()
    path  = Path(file_path)
    logger.info("[job=%s] Starting video preprocessing: %s", job_id, path.name)

    # ── 1. Validate ───────────────────────────────────────────────────────────
    try:
        validate_media(path)
    except (ValidationError, FileNotFoundError) as exc:
        logger.error("[job=%s] Validation failed: %s", job_id, exc)
        return build_failure(job_id, "video", str(path), str(exc), start_time=start)

    # ── 2. Create job directories ─────────────────────────────────────────────
    dirs = create_job_directories(job_id)

    # ── 3. Frame extraction ───────────────────────────────────────────────────
    try:
        extraction_result = extract_frames(
            video_path = path,
            output_dir = dirs["frames"],
        )
    except Exception as exc:
        logger.exception("[job=%s] Frame extraction failed.", job_id)
        return build_failure(job_id, "video", str(path), f"Frame extraction error: {exc}", start_time=start)

    all_frames   = extraction_result["frame_paths"]
    video_fps    = extraction_result["video_fps"]
    total_frames = extraction_result["total_frames"]
    resolution   = extraction_result["resolution"]
    duration_sec = extraction_result["duration_sec"]

    logger.info("[job=%s] Extracted %d frames.", job_id, len(all_frames))

    # ── 4. Sample stable frames ───────────────────────────────────────────────
    sampled_frames = sample_stable_frames(all_frames, sample_count=STABLE_FRAME_SAMPLE_COUNT)
    logger.info("[job=%s] Using %d sampled frames for face processing.", job_id, len(sampled_frames))

    # ── 5-6. Face detection + alignment + mouth crop per frame ────────────────
    faces_detected    = 0
    frames_with_faces = 0
    warnings: list[str] = []

    for frame_path_str in sampled_frames:
        frame_path = Path(frame_path_str)
        stem       = frame_path.stem     # e.g. "frame_000023"

        img = cv2.imread(str(frame_path))
        if img is None:
            logger.warning("[job=%s] Could not read frame: %s", job_id, frame_path.name)
            warnings.append(f"Could not read frame: {frame_path.name}")
            continue

        faces = detect_faces(img, max_faces=1)
        if not faces:
            logger.debug("[job=%s] No face in %s – skipping.", job_id, frame_path.name)
            continue

        frames_with_faces += 1
        face_box = faces[0]
        faces_detected += 1

        # Align face
        try:
            aligned_img, _ = align_face(
                img, face_box, target_size=TARGET_FACE_SIZE, padding=FACE_PADDING_RATIO
            )
            save_aligned_face(aligned_img, dirs["faces"] / f"{stem}_face.jpg")
        except Exception as exc:
            logger.warning("[job=%s] Face alignment failed for %s: %s", job_id, stem, exc)
            warnings.append(f"Alignment failed for {stem}: {exc}")
            continue

        # Mouth crop
        mouth_img, _ = extract_mouth_crop(aligned_img, target_size=TARGET_MOUTH_SIZE)
        if mouth_img is not None:
            save_mouth_crop(mouth_img, dirs["mouth_crops"] / f"{stem}_mouth.jpg")
        else:
            logger.debug("[job=%s] No mouth crop for frame %s.", job_id, stem)

    logger.info(
        "[job=%s] Face processing done: %d/%d sampled frames had faces.",
        job_id, frames_with_faces, len(sampled_frames),
    )

    # ── 7. Build result ───────────────────────────────────────────────────────
    outputs = VideoProcessingOutputs(
        validated_path    = str(path),
        frames_dir        = str(dirs["frames"]),
        total_frames      = total_frames,
        sampled_frames    = sampled_frames,
        face_crops_dir    = str(dirs["faces"]),
        mouth_crops_dir   = str(dirs["mouth_crops"]),
        faces_detected    = faces_detected,
        frames_with_faces = frames_with_faces,
        fps               = video_fps,
        duration_sec      = duration_sec,
        resolution        = tuple(resolution),  # type: ignore[arg-type]
    )

    metadata = {
        "video_fps":      video_fps,
        "total_frames":   total_frames,
        "sampled_count":  len(sampled_frames),
        "duration_sec":   duration_sec,
        "resolution":     resolution,
        "target_face_size":  TARGET_FACE_SIZE,
        "target_mouth_size": TARGET_MOUTH_SIZE,
    }

    result = build_success(
        job_id     = job_id,
        media_type = "video",
        input_path = str(path),
        outputs    = outputs,
        metadata   = metadata,
        start_time = start,
        warnings   = warnings,
    )

    logger.info("[job=%s] Video preprocessing complete in %.2fs.", job_id, result.duration_sec)
    return result