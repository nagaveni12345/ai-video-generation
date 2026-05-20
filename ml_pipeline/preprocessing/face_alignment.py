"""
ml_pipeline/preprocessing/face_alignment.py
Crops and normalises the face region from an image using a FaceBox,
then optionally aligns it using eye landmarks from MediaPipe Face Mesh.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np

from ml_pipeline.config.app_config import (
    FACE_PADDING_RATIO,
    FACE_MESH_MIN_DETECTION_CONF,
    FACE_MESH_MIN_TRACKING_CONF,
    FACE_MESH_MAX_FACES,
    TARGET_FACE_SIZE,
)
from ml_pipeline.preprocessing.face_detection import FaceBox
from ml_pipeline.utils.logger import get_logger

logger = get_logger("face_alignment")

_mp_face_mesh = mp.solutions.face_mesh

# MediaPipe Face Mesh landmark indices for eye centres
# Left eye centre  ≈ landmark 468 (iris), fallback: mean of 33,133,160,7,163,144,145,153,154,155,133
# Right eye centre ≈ landmark 473 (iris), fallback: mean of 362,382,381,380,374,373,390,249,263,466,388

_LEFT_EYE_IRIS  = 468
_RIGHT_EYE_IRIS = 473


def align_face(
    image:      np.ndarray,
    face_box:   FaceBox,
    target_size: tuple[int, int] = TARGET_FACE_SIZE,
    padding:    float            = FACE_PADDING_RATIO,
) -> tuple[np.ndarray, dict]:
    """
    Crop, optionally rotate to align eyes to horizontal, and resize the face.

    Args:
        image:       BGR uint8 source image.
        face_box:    Detected face bounding box.
        target_size: (width, height) of the output face image.
        padding:     Fractional padding applied to each side of the bounding box.

    Returns:
        Tuple of (aligned_face_bgr_image, landmark_metadata_dict).
    """
    h, w = image.shape[:2]

    # ── 1. Padded crop ────────────────────────────────────────────────────────
    padded = face_box.padded(ratio=padding)
    face_crop = image[padded.y1:padded.y2, padded.x1:padded.x2]

    if face_crop.size == 0:
        raise ValueError("Face crop is empty after padding – check bounding box values.")

    # ── 2. Get eye landmarks from Face Mesh for rotation alignment ─────────────
    angle, landmark_data = _get_eye_angle(image, w, h)

    if angle is not None:
        # Rotate the full image slightly to level eyes, then re-crop
        face_crop = _rotate_and_recrop(image, padded, angle)

    # ── 3. Resize to target ───────────────────────────────────────────────────
    aligned = cv2.resize(face_crop, target_size, interpolation=cv2.INTER_AREA)
    logger.debug("Face aligned: target_size=%s, rotation_angle=%.2f°", target_size, angle or 0.0)

    return aligned, landmark_data


def save_aligned_face(
    aligned_img: np.ndarray,
    output_path: str | Path,
) -> Path:
    """Save the aligned face image to *output_path* and return the Path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), aligned_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    logger.debug("Saved aligned face → %s", path)
    return path


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _get_eye_angle(
    image: np.ndarray,
    img_w: int,
    img_h: int,
) -> tuple[Optional[float], dict]:
    """
    Run MediaPipe Face Mesh and compute the rotation angle between the eye centres.

    Returns (angle_degrees, landmark_dict).  angle is None if no face detected.
    """
    rgb     = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    lm_data: dict = {}

    with _mp_face_mesh.FaceMesh(
        static_image_mode        = True,
        max_num_faces            = FACE_MESH_MAX_FACES,
        refine_landmarks         = True,          # required for iris landmarks 468/473
        min_detection_confidence = FACE_MESH_MIN_DETECTION_CONF,
        min_tracking_confidence  = FACE_MESH_MIN_TRACKING_CONF,
    ) as face_mesh:
        results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        logger.debug("Face Mesh returned no landmarks for eye alignment.")
        return None, lm_data

    landmarks = results.multi_face_landmarks[0].landmark

    # Check if iris refinement landmarks are present (index 468 / 473)
    if len(landmarks) > _RIGHT_EYE_IRIS:
        left_eye  = landmarks[_LEFT_EYE_IRIS]
        right_eye = landmarks[_RIGHT_EYE_IRIS]
    else:
        # Fallback to simpler outer eye corners
        left_eye  = landmarks[33]
        right_eye = landmarks[263]

    lx = int(left_eye.x  * img_w)
    ly = int(left_eye.y  * img_h)
    rx = int(right_eye.x * img_w)
    ry = int(right_eye.y * img_h)

    lm_data = {
        "left_eye":  {"x": lx, "y": ly},
        "right_eye": {"x": rx, "y": ry},
        "num_landmarks": len(landmarks),
    }

    dx    = rx - lx
    dy    = ry - ly
    angle = float(np.degrees(np.arctan2(dy, dx)))
    logger.debug("Eye angle: %.2f° (left=%s right=%s)", angle, (lx, ly), (rx, ry))
    return angle, lm_data


def _rotate_and_recrop(
    image:   np.ndarray,
    face_box: FaceBox,
    angle:   float,
) -> np.ndarray:
    """Rotate the image around the face centre and re-extract the padded crop."""
    h, w = image.shape[:2]
    cx = (face_box.x1 + face_box.x2) // 2
    cy = (face_box.y1 + face_box.y2) // 2

    M       = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR)

    # Re-crop from the (now level) rotated image
    x1 = max(0, face_box.x1)
    y1 = max(0, face_box.y1)
    x2 = min(w, face_box.x2)
    y2 = min(h, face_box.y2)
    return rotated[y1:y2, x1:x2]