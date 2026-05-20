"""
ml_pipeline/postprocessing/temporal_smoothing.py
=================================================
Temporal smoothing to reduce inter-frame flicker in generated talking-avatar
videos.

Two complementary techniques are applied:

1.  **Weighted rolling average** (fast, O(N)):
    Each pixel value is blended with a weighted average of its neighbours
    across time.  A Gaussian-shaped kernel centred on the current frame is
    used so nearby frames contribute more than distant ones.
    Window sizes of 3–5 frames with σ ≈ 1.0 are typical.

2.  **Optical-flow guided warp** (optional, higher quality, slower):
    Computes dense Farneback optical flow between consecutive frames and
    applies a small compensating warp to reduce sudden positional jumps
    in the lip region.  Useful when the avatar source is a video (not a
    still image) and the head moves between frames.

The mouth region (lower half of the frame bounding-box) receives heavier
smoothing than the rest of the image because Wav2Lip output is most
variable there.  The upper half (forehead, eyes) is left nearly untouched.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np

from ml_pipeline.utils.logger import get_logger

logger = get_logger("temporal_smoothing")

# ── Smoothing parameters ───────────────────────────────────────────────────────
_DEFAULT_WINDOW     = 5       # number of frames in rolling window (must be odd)
_DEFAULT_SIGMA      = 1.0     # Gaussian σ for frame weights
_MOUTH_BLEND_ALPHA  = 0.75    # how much smoothing to apply in mouth region (0–1)
_UPPER_BLEND_ALPHA  = 0.15    # how much smoothing to apply outside mouth region
_OF_WARP_STRENGTH   = 0.3     # optical-flow warp magnitude (0 = off, 1 = full)


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def smooth_talking_frames(
    frame_paths:      List[str],
    output_dir:       str | Path,
    job_id:           str,
    window:           int   = _DEFAULT_WINDOW,
    sigma:            float = _DEFAULT_SIGMA,
    use_optical_flow: bool  = False,
) -> dict:
    """
    Apply temporal smoothing to a sequence of merged talking frames.

    Args:
        frame_paths:      Sorted list of paths to merged talking-frame JPEGs.
        output_dir:       Directory for smoothed output frames.
        job_id:           Job identifier.
        window:           Rolling average window size (odd integer).
        sigma:            Gaussian weight σ.
        use_optical_flow: Whether to additionally apply OF-guided warping.

    Returns:
        Dict:
          - success       bool
          - smooth_frames list[str]
          - num_frames    int
          - elapsed_sec   float
          - error         str | None
    """
    start      = time.time()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "[job=%s] temporal_smoothing START | frames=%d  window=%d  of=%s",
        job_id, len(frame_paths), window, use_optical_flow,
    )

    if not frame_paths:
        return _fail("No frames provided for smoothing.")

    # Force odd window
    if window % 2 == 0:
        window += 1
    half = window // 2

    # ── Pre-load all frames into memory ───────────────────────────────────────
    frames: List[Optional[np.ndarray]] = []
    for p in frame_paths:
        img = cv2.imread(str(p))
        frames.append(img)   # None if unreadable

    num_frames = len(frames)

    # ── Pre-compute Gaussian kernel weights ───────────────────────────────────
    kernel = _gaussian_kernel(window, sigma)

    # ── Determine mouth region (lower 50% of frame) ───────────────────────────
    # Use the first valid frame to get dimensions
    ref = next((f for f in frames if f is not None), None)
    if ref is None:
        return _fail("No readable frames.")
    H, W = ref.shape[:2]
    mouth_y1 = H // 2   # lower half

    # ── Optional: pre-compute optical flow between consecutive frames ──────────
    flows: List[Optional[np.ndarray]] = [None] * num_frames
    if use_optical_flow:
        flows = _compute_flows(frames, job_id)

    # ── Rolling weighted average ──────────────────────────────────────────────
    smooth_paths: List[str] = []

    for i in range(num_frames):
        base = frames[i]
        if base is None:
            logger.warning("[job=%s] Skipping unreadable frame %d.", job_id, i)
            continue

        # Collect weighted neighbours
        accum  = base.astype(np.float32)
        total_w = kernel[half]   # weight of the current frame itself

        for delta, w in enumerate(kernel):
            if delta == half:
                continue  # already counted
            j = i + (delta - half)
            if j < 0 or j >= num_frames or frames[j] is None:
                continue
            neighbour = frames[j].astype(np.float32)
            if use_optical_flow and flows[j] is not None:
                neighbour = _warp_frame(neighbour, flows[j], _OF_WARP_STRENGTH)
            accum   += neighbour * w
            total_w += w

        blended = accum / total_w

        # Spatially-weighted blend: heavier in mouth region, lighter elsewhere
        result = base.astype(np.float32).copy()
        # Upper face: light blend
        result[:mouth_y1, :, :] = (
            blended[:mouth_y1, :, :] * _UPPER_BLEND_ALPHA
            + base[:mouth_y1, :, :].astype(np.float32) * (1.0 - _UPPER_BLEND_ALPHA)
        )
        # Lower face (mouth): heavier blend
        result[mouth_y1:, :, :] = (
            blended[mouth_y1:, :, :] * _MOUTH_BLEND_ALPHA
            + base[mouth_y1:, :, :].astype(np.float32) * (1.0 - _MOUTH_BLEND_ALPHA)
        )

        out_frame = np.clip(result, 0, 255).astype(np.uint8)
        out_path  = output_dir / f"smooth_{i:06d}.jpg"
        cv2.imwrite(str(out_path), out_frame, [cv2.IMWRITE_JPEG_QUALITY, 97])
        smooth_paths.append(str(out_path))

    smooth_paths.sort()
    elapsed = round(time.time() - start, 3)
    logger.info(
        "[job=%s] temporal_smoothing DONE | frames=%d  elapsed=%.2fs",
        job_id, len(smooth_paths), elapsed,
    )

    return {
        "success":      True,
        "smooth_frames": smooth_paths,
        "num_frames":   len(smooth_paths),
        "elapsed_sec":  elapsed,
        "error":        None,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Optical flow helpers
# ──────────────────────────────────────────────────────────────────────────────

def _compute_flows(
    frames: List[Optional[np.ndarray]],
    job_id: str,
) -> List[Optional[np.ndarray]]:
    """
    Compute Farneback dense optical flow from each frame to the next.
    Returns a list of flow arrays (H×W×2) or None for unreadable pairs.
    """
    n     = len(frames)
    flows = [None] * n

    for i in range(n - 1):
        f0 = frames[i]
        f1 = frames[i + 1]
        if f0 is None or f1 is None:
            continue
        try:
            gray0 = cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY)
            gray1 = cv2.cvtColor(f1, cv2.COLOR_BGR2GRAY)
            flow  = cv2.calcOpticalFlowFarneback(
                gray0, gray1,
                None,
                pyr_scale  = 0.5,
                levels     = 3,
                winsize    = 15,
                iterations = 3,
                poly_n     = 5,
                poly_sigma = 1.2,
                flags      = 0,
            )
            flows[i] = flow
        except Exception as exc:
            logger.debug("[job=%s] Optical flow failed for frame %d: %s", job_id, i, exc)

    return flows


def _warp_frame(
    frame:    np.ndarray,
    flow:     np.ndarray,
    strength: float,
) -> np.ndarray:
    """
    Apply a fraction of *flow* as a backward warp to *frame*.
    *strength* = 1.0 fully compensates motion; 0.0 = no-op.
    """
    H, W = frame.shape[:2]
    # Build remap coordinates
    flow_scaled = flow * strength
    coords_x = np.arange(W, dtype=np.float32)
    coords_y = np.arange(H, dtype=np.float32)
    mesh_x, mesh_y = np.meshgrid(coords_x, coords_y)

    map_x = (mesh_x + flow_scaled[:, :, 0]).astype(np.float32)
    map_y = (mesh_y + flow_scaled[:, :, 1]).astype(np.float32)

    warped = cv2.remap(
        frame, map_x, map_y,
        interpolation = cv2.INTER_LINEAR,
        borderMode    = cv2.BORDER_REPLICATE,
    )
    return warped.astype(np.float32)


# ──────────────────────────────────────────────────────────────────────────────
# Utility
# ──────────────────────────────────────────────────────────────────────────────

def _gaussian_kernel(window: int, sigma: float) -> np.ndarray:
    """Return a 1-D normalized Gaussian kernel of length *window*."""
    half = window // 2
    x    = np.arange(-half, half + 1, dtype=np.float32)
    k    = np.exp(-(x ** 2) / (2.0 * sigma ** 2))
    return k / k.sum()


def _fail(msg: str) -> dict:
    return {
        "success":      False,
        "smooth_frames": [],
        "num_frames":   0,
        "elapsed_sec":  0.0,
        "error":        msg,
    }
