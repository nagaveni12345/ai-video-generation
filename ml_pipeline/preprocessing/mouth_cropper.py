"""
ml_pipeline/preprocessing/mouth_cropper.py
Extracts a normalised mouth-region crop from a face image using
MediaPipe Face Mesh lip landmarks.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np

from ml_pipeline.config.app_config import (
    FACE_MESH_MAX_FACES,
    FACE_MESH_MIN_DETECTION_CONF,
    FACE_MESH_MIN_TRACKING_CONF,
    TARGET_MOUTH_SIZE,
)
from ml_pipeline.utils.logger import get_logger

logger = get_logger("mouth_cropper")

_mp_face_mesh = mp.solutions.face_mesh

# ── Lip landmark indices (MediaPipe 468-point mesh) ───────────────────────────
# Outer lip contour (approx)
_OUTER_LIPS = [
    61, 185, 40, 39, 37, 0, 267, 269, 270, 409,
    291, 375, 321, 405, 314, 17, 84, 181, 91, 146,
]
# Inner lip contour (approx)
_INNER_LIPS = [
    78, 191, 80, 81, 82, 13, 312, 311, 310, 415,
    308, 324, 318, 402, 317, 14, 87, 178, 88, 95,
]

# Combined set for bounding box calculation
_ALL_LIP_INDICES = list(set(_OUTER_LIPS + _INNER_LIPS))

# Mouth-region padding multiplier (relative to detected mouth bounding box)
_MOUTH_PAD_RATIO = 0.35



def extract_mouth_crop(
    image: np.ndarray,
    target_size: tuple[int, int] = TARGET_MOUTH_SIZE,
    pad_ratio:   float           = _MOUTH_PAD_RATIO,
) -> tuple[Optional[np.ndarray], dict]:
    """
    Detect lip landmarks with MediaPipe Face Mesh and return a normalised
    mouth-region crop.

    Args:
        image:       BGR uint8 image (full face or full frame).
        target_size: (width, height) of the output mouth crop.
        pad_ratio:   Extra padding around the detected lip bounding box.

    Returns:
        Tuple of ``(mouth_crop_bgr | None, landmark_metadata_dict)``.
        ``None`` is returned when no face / no lip landmarks are found.
    """
    h, w      = image.shape[:2]
    rgb        = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    lm_data:  dict = {"detected": False, "landmarks": []}

    with _mp_face_mesh.FaceMesh(
        static_image_mode        = True,
        max_num_faces            = FACE_MESH_MAX_FACES,
        refine_landmarks         = False,
        min_detection_confidence = FACE_MESH_MIN_DETECTION_CONF,
        min_tracking_confidence  = FACE_MESH_MIN_TRACKING_CONF,
    ) as face_mesh:
        results = face_mesh.process(rgb)

    if not results.multi_face_landmarks:
        logger.debug("No face landmarks detected by Face Mesh for mouth crop.")
        return None, lm_data

    landmarks = results.multi_face_landmarks[0].landmark

    # ── Collect lip landmark pixel coordinates ────────────────────────────────
    lip_pts: list[tuple[int, int]] = []
    for idx in _ALL_LIP_INDICES:
        if idx < len(landmarks):
            lm   = landmarks[idx]
            px   = int(lm.x * w)
            py   = int(lm.y * h)
            lip_pts.append((px, py))

    if not lip_pts:
        logger.warning("Lip landmark indices out of range – mesh has %d points.", len(landmarks))
        return None, lm_data

    # ── Bounding box with padding ─────────────────────────────────────────────
    xs = [p[0] for p in lip_pts]
    ys = [p[1] for p in lip_pts]
    bw = max(xs) - min(xs)
    bh = max(ys) - min(ys)
    pad_x = int(bw * pad_ratio)
    pad_y = int(bh * pad_ratio)

    x1 = max(0, min(xs) - pad_x)
    y1 = max(0, min(ys) - pad_y)
    x2 = min(w, max(xs) + pad_x)
    y2 = min(h, max(ys) + pad_y)

    if x2 <= x1 or y2 <= y1:
        logger.warning("Mouth bounding box is invalid: (%d,%d,%d,%d).", x1, y1, x2, y2)
        return None, lm_data

    mouth_crop = image[y1:y2, x1:x2]
    mouth_crop = cv2.resize(mouth_crop, target_size, interpolation=cv2.INTER_AREA)

    lm_data = {
        "detected":   True,
        "bbox":       {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
        "landmarks":  [{"x": p[0], "y": p[1]} for p in lip_pts],
        "target_size": target_size,
    }

    logger.debug("Mouth crop extracted: bbox=(%d,%d,%d,%d) → %s", x1, y1, x2, y2, target_size)
    return mouth_crop, lm_data


def save_mouth_crop(
    mouth_img:   np.ndarray,
    output_path: str | Path,
) -> Path:
    """Save a mouth crop image and return its absolute Path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), mouth_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    logger.debug("Saved mouth crop → %s", path)
    return path