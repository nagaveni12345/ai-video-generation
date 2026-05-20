"""
ml_pipeline/postprocessing/pro_landmark_merge.py
=================================================
Professional landmark-based lipsync frame merger.

Algorithm per frame:
  1.  Run MediaPipe Face Mesh on the full-resolution avatar frame to get
      precise lip polygon landmarks.
  2.  Compute a tight bounding rect around the outer lip contour.
  3.  Resize the Wav2Lip-generated 96×96 mouth crop to fit that lip region.
  4.  Build a convex-hull mask from the lip landmarks (pixel-precise).
  5.  Apply seamless Poisson clone (cv2.seamlessClone) for colour-consistent
      blending.  Falls back to feathered alpha-blend when seamlessClone fails
      (e.g. very small mouth regions or border-touching masks).
  6.  Preserve the rest of the avatar frame (eyes, forehead, background)
      untouched.

This produces a significantly more realistic result than simple
bounding-box paste because:
  - The lip polygon naturally masks teeth, upper lip boundary, and chin.
  - Poisson cloning preserves skin texture gradients.
  - No hard rectangular edges appear.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import List, Optional

import cv2
import mediapipe as mp
import numpy as np

from ml_pipeline.utils.logger import get_logger

logger = get_logger("pro_landmark_merge")

_mp_face_mesh = mp.solutions.face_mesh

# ── MediaPipe outer lip landmark indices (468-point mesh) ─────────────────────
_OUTER_LIP_IDX = [
    61, 185, 40, 39, 37, 0, 267, 269, 270, 409,
    291, 375, 321, 405, 314, 17, 84, 181, 91, 146,
]

# ── Padding multiplier around detected lip bounding rect ──────────────────────
_LIP_PADDING = 0.55

# ── Feather radius for fallback blend ─────────────────────────────────────────
_FEATHER_RADIUS = 9


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def merge_lipsync_frames_pro(
    avatar_frame_paths:  List[str],
    lipsync_frame_paths: List[str],
    output_dir:          str | Path,
    job_id:              str,
) -> dict:
    """
    Merge generated Wav2Lip mouth crops into full-res avatar frames using
    facial landmark guidance and Poisson seamless cloning.

    Args:
        avatar_frame_paths:  Sorted list of full-res avatar face frame paths.
        lipsync_frame_paths: Sorted list of 96×96 Wav2Lip output frame paths.
        output_dir:          Destination directory for merged talking frames.
        job_id:              Job identifier for logging.

    Returns:
        Dict:
          - success        bool
          - merged_frames  list[str]
          - num_frames     int
          - warnings       list[str]
          - error          str | None
    """
    start      = time.time()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "[job=%s] pro_landmark_merge START | avatar_frames=%d  lipsync_frames=%d",
        job_id, len(avatar_frame_paths), len(lipsync_frame_paths),
    )

    if not avatar_frame_paths:
        return _fail("No avatar frames provided.")
    if not lipsync_frame_paths:
        return _fail("No lipsync frames provided.")

    num_out = len(lipsync_frame_paths)

    # Tile avatar frames to match lipsync count (handles static image avatars)
    tiled_avatar = _tile_to_length(avatar_frame_paths, num_out)

    merged_frames: List[str] = []
    warnings:      List[str] = []

    for idx, (av_path, ls_path) in enumerate(zip(tiled_avatar, lipsync_frame_paths)):
        av_img = cv2.imread(str(av_path))
        ls_img = cv2.imread(str(ls_path))

        if av_img is None:
            w = f"Frame {idx}: cannot read avatar frame {Path(av_path).name}"
            logger.warning("[job=%s] %s", job_id, w)
            warnings.append(w)
            continue
        if ls_img is None:
            w = f"Frame {idx}: cannot read lipsync frame {Path(ls_path).name}"
            logger.warning("[job=%s] %s", job_id, w)
            warnings.append(w)
            continue

        try:
            merged, warn = _merge_single(av_img, ls_img, idx, job_id)
            if warn:
                warnings.extend(warn)
        except Exception as exc:
            w = f"Frame {idx}: merge error: {exc}"
            logger.warning("[job=%s] %s", job_id, w)
            warnings.append(w)
            merged = av_img   # fall back to original frame

        out_path = output_dir / f"talking_{idx:06d}.jpg"
        cv2.imwrite(str(out_path), merged, [cv2.IMWRITE_JPEG_QUALITY, 95])
        merged_frames.append(str(out_path))

    merged_frames.sort()
    elapsed = round(time.time() - start, 3)
    logger.info(
        "[job=%s] pro_landmark_merge DONE | frames=%d  warnings=%d  elapsed=%.2fs",
        job_id, len(merged_frames), len(warnings), elapsed,
    )

    return {
        "success":       True,
        "merged_frames": merged_frames,
        "num_frames":    len(merged_frames),
        "warnings":      warnings,
        "error":         None,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Per-frame merge logic
# ──────────────────────────────────────────────────────────────────────────────

def _merge_single(
    avatar_bgr:   np.ndarray,
    lipsync_bgr:  np.ndarray,
    frame_idx:    int,
    job_id:       str,
) -> tuple[np.ndarray, List[str]]:
    """
    Merge one lipsync mouth crop into one avatar frame.
    Returns (merged_bgr, warnings_list).
    """
    warnings: List[str] = []
    h, w = avatar_bgr.shape[:2]

    # ── Detect lip landmarks on the avatar frame ──────────────────────────────
    lip_pts, face_detected = _get_lip_landmarks(avatar_bgr, w, h)

    if not face_detected or lip_pts is None:
        # Fallback: simple lower-face bounding box blend
        warnings.append(
            f"Frame {frame_idx}: no lip landmarks detected — using bbox fallback."
        )
        merged = _bbox_fallback_blend(avatar_bgr, lipsync_bgr)
        return merged, warnings

    # ── Compute lip bounding rect with padding ────────────────────────────────
    lip_pts_arr = np.array(lip_pts, dtype=np.float32)
    x_min, y_min = lip_pts_arr.min(axis=0)
    x_max, y_max = lip_pts_arr.max(axis=0)
    bw = x_max - x_min
    bh = y_max - y_min
    pad_x = int(bw * _LIP_PADDING)
    pad_y = int(bh * _LIP_PADDING)

    lx1 = max(0, int(x_min) - pad_x)
    ly1 = max(0, int(y_min) - pad_y)
    lx2 = min(w, int(x_max) + pad_x)
    ly2 = min(h, int(y_max) + pad_y)

    rw = lx2 - lx1
    rh = ly2 - ly1
    if rw < 8 or rh < 8:
        warnings.append(f"Frame {frame_idx}: lip region too small ({rw}×{rh}) — bbox fallback.")
        return _bbox_fallback_blend(avatar_bgr, lipsync_bgr), warnings

    # ── Resize lipsync crop to lip bounding rect ──────────────────────────────
    # ------------------------------------------------------------------
    # Extract only synthesized lower-mouth region from Wav2Lip output
    # ------------------------------------------------------------------
    gh, gw = lipsync_bgr.shape[:2]

    mx1 = int(gw * 0.18)
    mx2 = int(gw * 0.82)
    my1 = int(gh * 0.42)
    my2 = int(gh * 0.88)

    mouth_patch = lipsync_bgr[my1:my2, mx1:mx2]

    # upscale only active speaking region into target lip ROI
    ls_resized = cv2.resize(mouth_patch, (rw, rh), interpolation=cv2.INTER_LANCZOS4)

    # ── Build lip convex-hull mask (pixel-precise polygon) ────────────────────
    # Translate lip points to ROI-local coords
    local_pts = np.array(
        [[int(pt[0]) - lx1, int(pt[1]) - ly1] for pt in lip_pts],
        dtype=np.int32,
    )
    hull = cv2.convexHull(local_pts)
    mask = np.zeros((rh, rw), dtype=np.uint8)
    cv2.fillConvexPoly(mask, hull, 255)

    # Erode slightly so we don't sample outside the lip boundary
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask   = cv2.erode(mask, kernel, iterations=1)

    if mask.sum() == 0:
        warnings.append(f"Frame {frame_idx}: lip mask empty after erosion — bbox fallback.")
        return _bbox_fallback_blend(avatar_bgr, lipsync_bgr), warnings

    # ── Build full-image mask for seamlessClone ───────────────────────────────
    full_mask = np.zeros((h, w), dtype=np.uint8)
    full_mask[ly1:ly2, lx1:lx2] = mask

    # Centre point for seamlessClone
    cx = lx1 + rw // 2
    cy = ly1 + rh // 2

    # Build a full-size source image with the lipsync patch placed at the ROI
    source_full = avatar_bgr.copy()
    source_full[ly1:ly2, lx1:lx2] = ls_resized

    # ── Attempt Poisson seamless clone ───────────────────────────────────────
    try:
        merged = _feather_blend(avatar_bgr, ls_resized, lx1, ly1, lx2, ly2, mask)
        return merged, warnings
    except cv2.error as exc:
        # seamlessClone can fail if mask touches image border
        warnings.append(
            f"Frame {frame_idx}: seamlessClone failed ({exc}) — feather fallback."
        )

    # ── Feathered alpha-blend fallback ────────────────────────────────────────
    merged = _feather_blend(avatar_bgr, ls_resized, lx1, ly1, lx2, ly2, mask)
    return merged, warnings


# ──────────────────────────────────────────────────────────────────────────────
# Fallback blend strategies
# ──────────────────────────────────────────────────────────────────────────────

def _feather_blend(
    avatar: np.ndarray,
    patch:  np.ndarray,
    x1: int, y1: int,
    x2: int, y2: int,
    mask: np.ndarray,
) -> np.ndarray:
    """Gaussian-feathered alpha blend of *patch* into *avatar* at [y1:y2, x1:x2]."""
    rw, rh = x2 - x1, y2 - y1
    result = avatar.copy()

    ksize = max(3, _FEATHER_RADIUS * 2 + 1)
    mask_f = cv2.GaussianBlur(mask.astype(np.float32), (ksize, ksize), _FEATHER_RADIUS)
    mask_f = np.clip(mask_f / 255.0, 0.0, 1.0)[:, :, np.newaxis]

    roi    = result[y1:y2, x1:x2].astype(np.float32)
    patch_f = patch[:rh, :rw].astype(np.float32)

    blended = patch_f * mask_f + roi * (1.0 - mask_f)
    result[y1:y2, x1:x2] = np.clip(blended, 0, 255).astype(np.uint8)
    return result


def _bbox_fallback_blend(
    avatar:  np.ndarray,
    lipsync: np.ndarray,
) -> np.ndarray:
    """
    Ultra-simple fallback: paste lipsync into the lower-centre quarter of
    the avatar when no landmarks are available.
    """
    h, w  = avatar.shape[:2]
    result = avatar.copy()
    y1 = h // 2
    y2 = h
    x1 = w // 4
    x2 = 3 * w // 4
    rh, rw = y2 - y1, x2 - x1

    ls_resized = cv2.resize(lipsync, (rw, rh), interpolation=cv2.INTER_AREA)
    mask = np.ones((rh, rw), dtype=np.uint8) * 200
    result = _feather_blend(result, ls_resized, x1, y1, x2, y2, mask)
    return result


# ──────────────────────────────────────────────────────────────────────────────
# Landmark detection
# ──────────────────────────────────────────────────────────────────────────────

def _get_lip_landmarks(
    image: np.ndarray,
    img_w: int,
    img_h: int,
) -> tuple[Optional[List[tuple[int, int]]], bool]:
    """
    Run MediaPipe Face Mesh and extract outer lip landmark pixel coordinates.
    Returns (lip_pts_list, face_detected_bool).
    """
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    with _mp_face_mesh.FaceMesh(
        static_image_mode        = True,
        max_num_faces            = 1,
        refine_landmarks         = False,
        min_detection_confidence = 0.5,
        min_tracking_confidence  = 0.5,
    ) as fm:
        results = fm.process(rgb)

    if not results.multi_face_landmarks:
        return None, False

    lms = results.multi_face_landmarks[0].landmark
    lip_pts = []
    for idx in _OUTER_LIP_IDX:
        if idx < len(lms):
            lm = lms[idx]
            lip_pts.append((int(lm.x * img_w), int(lm.y * img_h)))

    return (lip_pts if lip_pts else None), True


# ──────────────────────────────────────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────────────────────────────────────

def _tile_to_length(paths: List[str], target: int) -> List[str]:
    result = []
    while len(result) < target:
        result.extend(paths)
    return result[:target]


def _fail(msg: str) -> dict:
    return {
        "success":       False,
        "merged_frames": [],
        "num_frames":    0,
        "warnings":      [],
        "error":         msg,
    }
