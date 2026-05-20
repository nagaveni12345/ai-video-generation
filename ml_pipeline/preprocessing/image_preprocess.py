"""
ml_pipeline/preprocessing/image_preprocess.py
Full preprocessing chain for a single uploaded avatar IMAGE.
"""

from __future__ import annotations

import time
from pathlib import Path

import cv2

from ml_pipeline.config.app_config import FACE_PADDING_RATIO, TARGET_FACE_SIZE, TARGET_MOUTH_SIZE
from ml_pipeline.preprocessing.face_alignment import align_face, save_aligned_face
from ml_pipeline.preprocessing.face_detection import detect_faces
from ml_pipeline.preprocessing.media_validator import ValidationError, validate_media
from ml_pipeline.preprocessing.mouth_cropper import extract_mouth_crop, save_mouth_crop
from ml_pipeline.utils.file_manager import create_job_directories
from ml_pipeline.utils.logger import get_logger
from ml_pipeline.utils.response_builder import (
    ImageProcessingOutputs,
    PipelineResult,
    build_failure,
    build_success,
)

logger = get_logger("image_preprocess")


def preprocess_image(
    file_path: str | Path,
    job_id: str,
) -> PipelineResult:

    start = time.time()
    path = Path(file_path)
    logger.info("[job=%s] Starting image preprocessing: %s", job_id, path.name)

    # ── 1. Validate ─────────────────────────────────────────────────────
    try:
        validate_media(path)
    except (ValidationError, FileNotFoundError) as exc:
        logger.error("[job=%s] Validation failed: %s", job_id, exc)
        return build_failure(job_id, "image", str(path), str(exc), start_time=start)

    # ── 2. Create job directories ──────────────────────────────────────
    dirs = create_job_directories(job_id)

    # ── 3. Read image ───────────────────────────────────────────────────
    img = cv2.imread(str(path))
    if img is None:
        msg = f"cv2.imread returned None for {path}"
        logger.error("[job=%s] %s", job_id, msg)
        return build_failure(job_id, "image", str(path), msg, start_time=start)

    h, w = img.shape[:2]
    logger.info("[job=%s] Image loaded: %dx%d", job_id, w, h)

    # Save ORIGINAL full-resolution frame (used later for high-res final merge)
    original_frame_path = dirs["original_frames"] / f"{job_id}_original.jpg"
    cv2.imwrite(str(original_frame_path), img, [cv2.IMWRITE_JPEG_QUALITY, 98])
    logger.info("[job=%s] Original frame saved: %s", job_id, original_frame_path)

    # ── 4. Face detection ───────────────────────────────────────────────
    faces = detect_faces(img, max_faces=1)
    if not faces:
        msg = "No face detected in the uploaded image."
        logger.warning("[job=%s] %s", job_id, msg)
        return build_failure(job_id, "image", str(path), msg, start_time=start)

    face_box = faces[0]
    logger.info("[job=%s] Face detected: %s conf=%.3f", job_id, face_box.to_dict(), face_box.confidence)

    # ── 5. Face alignment / crop ───────────────────────────────────────
    try:
        aligned_img, landmark_data = align_face(
            img,
            face_box,
            target_size=TARGET_FACE_SIZE,
            padding=FACE_PADDING_RATIO,
        )
    except Exception as exc:
        logger.exception("[job=%s] Face alignment failed.", job_id)
        return build_failure(job_id, "image", str(path), f"Face alignment error: {exc}", start_time=start)

    aligned_path = save_aligned_face(aligned_img, dirs["faces"] / f"{job_id}_aligned.jpg")

    # ── 6. Mouth crop ───────────────────────────────────────────────────
    mouth_img, mouth_lm = extract_mouth_crop(aligned_img, target_size=TARGET_MOUTH_SIZE)
    mouth_path: Path | None = None
    warnings: list[str] = []

    if mouth_img is not None:
        mouth_path = save_mouth_crop(mouth_img, dirs["mouth_crops"] / f"{job_id}_mouth.jpg")
        logger.info("[job=%s] Mouth crop saved: %s", job_id, mouth_path)
    else:
        msg = "Mouth landmarks not detected – mouth crop skipped."
        logger.warning("[job=%s] %s", job_id, msg)
        warnings.append(msg)

    # ── 7. Build outputs ────────────────────────────────────────────────
    outputs = ImageProcessingOutputs(
        validated_path=str(path),
        face_crop_path=str(dirs["faces"] / f"{job_id}_aligned.jpg"),
        aligned_face_path=str(aligned_path),
        mouth_crop_path=str(mouth_path) if mouth_path else "",
        landmark_data={**landmark_data, "mouth": mouth_lm},
    )

    metadata = {
        "original_resolution": (w, h),
        "original_frame_path": str(original_frame_path),
        "face_box": face_box.to_dict(),
        "target_face_size": TARGET_FACE_SIZE,
        "target_mouth_size": TARGET_MOUTH_SIZE,
    }

    result = build_success(
        job_id=job_id,
        media_type="image",
        input_path=str(path),
        outputs=outputs,
        metadata=metadata,
        start_time=start,
        warnings=warnings,
    )

    logger.info("[job=%s] Image preprocessing complete in %.2fs.", job_id, result.duration_sec)
    return result