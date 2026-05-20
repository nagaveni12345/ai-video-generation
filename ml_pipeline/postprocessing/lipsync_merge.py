"""
ml_pipeline/postprocessing/lipsync_merge.py
Merges Wav2Lip-generated mouth crops back into the original avatar face frames.

Responsibilities:
  - Load landmark / bounding-box metadata stored by the preprocessing pipeline
  - For each output lipsync frame, blend the generated mouth ROI into the
    corresponding avatar face frame
  - Preserve face alignment and colour consistency
  - Write merged "talking" frames to the job output directory
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np

from ml_pipeline.utils.logger import get_logger

logger = get_logger("lipsync_merge")

# ── Blending parameters ────────────────────────────────────────────────────────
_FEATHER_RADIUS = 7          # Gaussian feather radius for seamless blending
_BLEND_ALPHA    = 1.0        # 1.0 = full replacement; < 1.0 = soft overlay


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def merge_lipsync_frames(
    avatar_frame_paths:    List[str],
    lipsync_frame_paths:   List[str],
    landmark_metadata_dir: str | Path,
    output_dir:            str | Path,
    job_id:                str,
    face_box_fallback:     Optional[dict] = None,
) -> dict:
    """
    Merge generated mouth frames into original avatar frames.

    Args:
        avatar_frame_paths:    Ordered list of the original extracted avatar frame
                               paths (from ml_pipeline/data/processed/avatar_frames/).
        lipsync_frame_paths:   Ordered list of Wav2Lip output mouth frame paths.
        landmark_metadata_dir: Directory containing per-job JSON landmark files
                               written by the avatar preprocessing pipeline.
        output_dir:            Destination for merged talking frames.
        job_id:                Job identifier.
        face_box_fallback:     Optional face bounding box dict ``{x1,y1,x2,y2}``
                               used when per-frame landmark JSON is missing.

    Returns:
        Dict with:
          - ``success``       bool
          - ``merged_frames`` list[str]
          - ``num_frames``    int
          - ``error``         str | None
    """
    start      = time.time()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    landmark_metadata_dir = Path(landmark_metadata_dir)

    logger.info(
        "[job=%s] Merging lipsync | avatar_frames=%d  lipsync_frames=%d",
        job_id, len(avatar_frame_paths), len(lipsync_frame_paths),
    )

    if not avatar_frame_paths:
        return _fail("No avatar frames provided for merge.")
    if not lipsync_frame_paths:
        return _fail("No lipsync frames provided for merge.")

    # ── Align sequence lengths ─────────────────────────────────────────────────
    # If avatar has fewer frames (static image or short clip), tile avatar frames
    # to match lipsync frame count.

    num_out = len(lipsync_frame_paths)

    avatar_paths = []
    while len(avatar_paths) < num_out:
        avatar_paths.extend(avatar_frame_paths)

    avatar_paths = avatar_paths[:num_out]
    lipsync_paths = lipsync_frame_paths[:num_out]

    merged_frames: List[str] = []
    warnings: List[str]      = []

    for idx, (av_path, ls_path) in enumerate(zip(avatar_paths, lipsync_paths)):
        av_path = Path(av_path)
        ls_path = Path(ls_path)

        # Load frames
        avatar_img  = cv2.imread(str(av_path))
        lipsync_img = cv2.imread(str(ls_path))

        if avatar_img is None:
            msg = f"Cannot read avatar frame: {av_path.name}"
            logger.warning("[job=%s] %s", job_id, msg)
            warnings.append(msg)
            continue
        if lipsync_img is None:
            msg = f"Cannot read lipsync frame: {ls_path.name}"
            logger.warning("[job=%s] %s", job_id, msg)
            warnings.append(msg)
            continue

        # Load landmark metadata for this frame (or fall back to global bbox)
        face_box = _resolve_face_box(
            frame_stem            = av_path.stem,
            landmark_metadata_dir = landmark_metadata_dir,
            fallback              = face_box_fallback,
            img_shape             = avatar_img.shape,
        )

        # Perform the merge
        merged = _merge_single_frame(avatar_img, lipsync_img, face_box)

        # Save merged frame
        out_path = output_dir / f"talking_{idx:06d}.jpg"
        cv2.imwrite(str(out_path), merged, [cv2.IMWRITE_JPEG_QUALITY, 95])
        merged_frames.append(str(out_path))

    merged_frames.sort()
    elapsed = time.time() - start

    logger.info(
        "[job=%s] Merge complete: %d frames in %.2fs  warnings=%d",
        job_id, len(merged_frames), elapsed, len(warnings),
    )

    return {
        "success":       True,
        "merged_frames": merged_frames,
        "num_frames":    len(merged_frames),
        "warnings":      warnings,
        "error":         None,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _resolve_face_box(
    frame_stem:            str,
    landmark_metadata_dir: Path,
    fallback:              Optional[dict],
    img_shape:             tuple,
) -> dict:
    """
    Attempt to load a per-frame landmark JSON and extract the face bounding box.
    Falls back to *fallback* dict, then to the full-image bounding box.
    """
    # Try exact match: <stem>_landmarks.json
    candidates = [
        landmark_metadata_dir / f"{frame_stem}_landmarks.json",
        landmark_metadata_dir / f"{frame_stem}.json",
        landmark_metadata_dir / "landmarks.json",   # single-image job
    ]
    for cand in candidates:
        if cand.exists():
            try:
                with open(cand) as f:
                    data = json.load(f)
                # Support both flat dict and nested { "face_box": {...} }
                box = data.get("face_box") or data
                if all(k in box for k in ("x1", "y1", "x2", "y2")):
                    return box
            except Exception as exc:
                logger.debug("Could not parse landmark JSON %s: %s", cand, exc)

    if fallback and all(k in fallback for k in ("x1", "y1", "x2", "y2")):
        return fallback

    # Ultimate fallback: lower half of image
    h, w = img_shape[:2]
    return {"x1": 0, "y1": h // 2, "x2": w, "y2": h}


def _merge_single_frame(
    avatar_bgr:   np.ndarray,
    lipsync_bgr:  np.ndarray,
    face_box:     dict,
) -> np.ndarray:
    """
    Paste the lipsync mouth region into the avatar frame inside *face_box*.

    Strategy:
      1. Extract lower half of the face bounding box (mouth region).
      2. Resize Wav2Lip output to match that region.
      3. Feather-blend into the avatar frame for seamless edges.
    """
    avatar  = avatar_bgr.copy()
    img_h, img_w = avatar.shape[:2]

    x1 = max(0, int(face_box["x1"]))
    y1 = max(0, int(face_box["y1"]))
    x2 = min(img_w, int(face_box["x2"]))
    y2 = min(img_h, int(face_box["y2"]))

    face_h = y2 - y1
    face_w = x2 - x1
    if face_h <= 0 or face_w <= 0:
        return avatar

    # Mouth region = lower half of face bounding box
    mouth_y1 = y1 + face_h // 2
    mouth_y2 = y2
    mouth_x1 = x1
    mouth_x2 = x2
    mouth_h  = mouth_y2 - mouth_y1
    mouth_w  = mouth_x2 - mouth_x1

    if mouth_h <= 0 or mouth_w <= 0:
        return avatar

    # Resize Wav2Lip output to match the mouth ROI dimensions
    resized_lipsync = cv2.resize(lipsync_bgr, (mouth_w, mouth_h), interpolation=cv2.INTER_AREA)

    # Build feather mask (white centre, black edges → smooth blend)
    mask = np.ones((mouth_h, mouth_w), dtype=np.float32)
    ksize = max(3, _FEATHER_RADIUS * 2 + 1)
    mask  = cv2.GaussianBlur(mask, (ksize, ksize), _FEATHER_RADIUS)
    mask  = np.clip(mask * _BLEND_ALPHA, 0.0, 1.0)
    mask3 = mask[:, :, np.newaxis]

    # Blend
    roi           = avatar[mouth_y1:mouth_y2, mouth_x1:mouth_x2].astype(np.float32)
    lipsync_f     = resized_lipsync.astype(np.float32)
    blended       = lipsync_f * mask3 + roi * (1.0 - mask3)
    avatar[mouth_y1:mouth_y2, mouth_x1:mouth_x2] = np.clip(blended, 0, 255).astype(np.uint8)

    return avatar


def _fail(msg: str) -> dict:
    return {
        "success":       False,
        "merged_frames": [],
        "num_frames":    0,
        "warnings":      [],
        "error":         msg,
    }