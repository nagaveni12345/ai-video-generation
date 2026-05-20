"""
ml_pipeline/preprocessing/face_detection.py
Face detection using MediaPipe Face Detection (primary) with an
OpenCV Haar-cascade fallback.

Returns bounding boxes and confidence scores; does NOT produce landmarks
(that is handled by face_mesh.py / face_alignment.py).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import mediapipe as mp
import numpy as np

from ml_pipeline.config.app_config import (
    FACE_MESH_MIN_DETECTION_CONF,
)
from ml_pipeline.config.model_config import HAAR_CASCADE_PATH, USE_MEDIAPIPE_FACE_DETECTION
from ml_pipeline.utils.logger import get_logger

logger = get_logger("face_detection")

# MediaPipe solution handle (loaded once, module-level)
_mp_face_detection = mp.solutions.face_detection


@dataclass
class FaceBox:
    """Axis-aligned bounding box for a detected face."""

    x1:         int
    y1:         int
    x2:         int
    y2:         int
    confidence: float
    img_width:  int
    img_height: int

    # ── Derived properties ────────────────────────────────────────────────────
    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1

    @property
    def center(self) -> tuple[int, int]:
        return (self.x1 + self.width // 2, self.y1 + self.height // 2)

    def padded(self, ratio: float = 0.20) -> "FaceBox":
        """Return a new FaceBox with *ratio* padding applied on each side."""
        pad_x = int(self.width  * ratio)
        pad_y = int(self.height * ratio)
        return FaceBox(
            x1         = max(0, self.x1 - pad_x),
            y1         = max(0, self.y1 - pad_y),
            x2         = min(self.img_width,  self.x2 + pad_x),
            y2         = min(self.img_height, self.y2 + pad_y),
            confidence = self.confidence,
            img_width  = self.img_width,
            img_height = self.img_height,
        )

    def to_dict(self) -> dict:
        return {
            "x1": self.x1, "y1": self.y1,
            "x2": self.x2, "y2": self.y2,
            "width": self.width, "height": self.height,
            "confidence": self.confidence,
        }


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def detect_faces(
    image: np.ndarray,
    min_confidence: float = FACE_MESH_MIN_DETECTION_CONF,
    max_faces: int = 1,
) -> list[FaceBox]:
    """
    Detect faces in a BGR numpy image.

    Args:
        image:          BGR uint8 numpy array (H × W × 3).
        min_confidence: Minimum detection confidence threshold.
        max_faces:      Maximum number of faces to return.

    Returns:
        List of :class:`FaceBox` sorted by confidence (descending).
        Empty list if no face detected.
    """
    if USE_MEDIAPIPE_FACE_DETECTION:
        boxes = _detect_mediapipe(image, min_confidence, max_faces)
    else:
        boxes = []

    if not boxes:
        logger.debug("MediaPipe found no faces – falling back to Haar cascade.")
        boxes = _detect_haar(image)

    # Keep only top-k
    boxes = sorted(boxes, key=lambda b: b.confidence, reverse=True)[:max_faces]
    return boxes


def detect_face_in_file(
    image_path: str | Path,
    min_confidence: float = FACE_MESH_MIN_DETECTION_CONF,
) -> Optional[FaceBox]:
    """
    Convenience wrapper: load image from disk, detect primary face.

    Returns ``None`` if no face is found.
    """
    path = Path(image_path)
    img  = cv2.imread(str(path))
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {path}")

    faces = detect_faces(img, min_confidence=min_confidence, max_faces=1)
    return faces[0] if faces else None


# ──────────────────────────────────────────────────────────────────────────────
# Internal detectors
# ──────────────────────────────────────────────────────────────────────────────

def _detect_mediapipe(
    image: np.ndarray,
    min_confidence: float,
    max_faces: int,
) -> list[FaceBox]:
    """Run MediaPipe Face Detection and return FaceBox list."""
    h, w = image.shape[:2]
    rgb   = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    boxes: list[FaceBox] = []

    with _mp_face_detection.FaceDetection(
        model_selection           = 1,          # 1 = long-range (> 2 m)
        min_detection_confidence  = min_confidence,
    ) as detector:
        results = detector.process(rgb)

    if not results.detections:
        return boxes

    for det in results.detections[:max_faces]:
        bbox   = det.location_data.relative_bounding_box
        score  = det.score[0] if det.score else 0.0

        x1 = max(0, int(bbox.xmin * w))
        y1 = max(0, int(bbox.ymin * h))
        x2 = min(w, int((bbox.xmin + bbox.width)  * w))
        y2 = min(h, int((bbox.ymin + bbox.height) * h))

        if x2 <= x1 or y2 <= y1:
            continue

        boxes.append(FaceBox(x1=x1, y1=y1, x2=x2, y2=y2,
                             confidence=float(score),
                             img_width=w, img_height=h))
        logger.debug("MediaPipe face: bbox=(%d,%d,%d,%d) conf=%.3f", x1, y1, x2, y2, score)

    return boxes


def _detect_haar(image: np.ndarray) -> list[FaceBox]:
    """Haar-cascade fallback for face detection."""
    cascade_path = Path(HAAR_CASCADE_PATH)
    if not cascade_path.exists():
        # Try OpenCV bundled cascades
        import os
        cv2_data = os.path.join(cv2.__file__.rsplit(os.sep, 1)[0], "data")
        fallback  = os.path.join(cv2_data, "haarcascade_frontalface_default.xml")
        cascade_path = Path(fallback)

    if not cascade_path.exists():
        logger.warning("Haar cascade file not found at %s; skipping fallback.", cascade_path)
        return []

    cascade = cv2.CascadeClassifier(str(cascade_path))
    gray    = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w    = image.shape[:2]

    detections = cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    if detections is None or len(detections) == 0:
        return []

    boxes: list[FaceBox] = []
    for (x, y, bw, bh) in detections:
        boxes.append(FaceBox(
            x1=x, y1=y, x2=x + bw, y2=y + bh,
            confidence=0.5,   # Haar has no score; assign neutral
            img_width=w, img_height=h,
        ))

    logger.debug("Haar cascade found %d face(s).", len(boxes))
    return boxes