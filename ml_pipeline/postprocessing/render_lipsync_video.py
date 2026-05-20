"""
ml_pipeline/postprocessing/render_lipsync_video.py
Renders the final talking-avatar MP4 from merged frames + original audio.

Responsibilities:
  - Assemble ordered talking frames into a silent video via OpenCV
  - Mux the cleaned 16 kHz audio onto the silent video using ffmpeg-python
  - Apply optional H.264 encoding quality settings
  - Return the path to the final MP4
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import List, Optional

import cv2

from ml_pipeline.utils.logger import get_logger

logger = get_logger("render_lipsync_video")

# ── Encoding defaults ──────────────────────────────────────────────────────────
_DEFAULT_FPS      = 25
_DEFAULT_CRF      = 18          # H.264 CRF (lower = better quality)
_DEFAULT_PRESET   = "medium"    # ffmpeg encoding speed/quality preset
_PIXEL_FORMAT     = "yuv420p"   # broadest compatibility


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def render_lipsync_video(
    merged_frame_paths: List[str],
    audio_path:         str | Path,
    output_dir:         str | Path,
    job_id:             str,
    fps:                float       = _DEFAULT_FPS,
    crf:                int         = _DEFAULT_CRF,
    preset:             str         = _DEFAULT_PRESET,
) -> dict:
    """
    Render the final lipsync MP4.

    Args:
        merged_frame_paths: Sorted list of talking-frame image paths.
        audio_path:         Path to the 16 kHz WAV produced by audio_preprocess.
        output_dir:         Directory for the final MP4.
        job_id:             Job identifier for file naming.
        fps:                Output video frame rate.
        crf:                H.264 CRF quality (0–51; default 18).
        preset:             ffmpeg encoding preset.

    Returns:
        Dict with:
          - ``success``    bool
          - ``video_path`` str   — absolute path to output MP4
          - ``error``      str | None
    """
    start      = time.time()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = Path(audio_path)

    logger.info(
        "[job=%s] Rendering video | frames=%d  fps=%.1f  audio=%s",
        job_id, len(merged_frame_paths), fps, audio_path.name,
    )

    if not merged_frame_paths:
        return _fail("No merged frames provided for video rendering.")
    if not audio_path.exists():
        return _fail(f"Audio file not found: {audio_path}")

    # ── Step 1: Write silent video ─────────────────────────────────────────────
    silent_path = output_dir / f"{job_id}_silent.avi"
    try:
        _write_silent_video(merged_frame_paths, silent_path, fps)
    except Exception as exc:
        logger.exception("[job=%s] Failed to write silent video.", job_id)
        return _fail(f"Silent video write error: {exc}")

    # ── Step 2: Mux audio with ffmpeg ─────────────────────────────────────────
    final_path = output_dir / f"{job_id}_lipsync.mp4"
    try:
        _mux_audio(silent_path, audio_path, final_path, crf, preset)
    except Exception as exc:
        logger.exception("[job=%s] ffmpeg mux failed.", job_id)
        return _fail(f"ffmpeg mux error: {exc}")
    finally:
        # Clean up intermediate silent video
        if silent_path.exists():
            silent_path.unlink()

    elapsed = time.time() - start
    logger.info("[job=%s] Video rendered in %.2fs → %s", job_id, elapsed, final_path)

    return {
        "success":    True,
        "video_path": str(final_path),
        "error":      None,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _write_silent_video(
    frame_paths: List[str],
    output_path: Path,
    fps:         float,
) -> None:
    """Use OpenCV VideoWriter to assemble frames into a silent AVI."""
    first_frame = cv2.imread(str(frame_paths[0]))
    if first_frame is None:
        raise IOError(f"Cannot read first frame: {frame_paths[0]}")

    h, w = first_frame.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (w, h))

    if not writer.isOpened():
        raise IOError(f"VideoWriter failed to open output: {output_path}")

    for path in frame_paths:
        frame = cv2.imread(str(path))
        if frame is None:
            logger.warning("Skipping unreadable frame: %s", path)
            continue
        if frame.shape[:2] != (h, w):
            frame = cv2.resize(frame, (w, h))
        writer.write(frame)

    writer.release()
    logger.info("Silent video written: %s (%d frames, %dx%d @ %.1ffps)", output_path, len(frame_paths), w, h, fps)


def _mux_audio(
    video_path:  Path,
    audio_path:  Path,
    output_path: Path,
    crf:         int,
    preset:      str,
) -> None:
    """
    Mux video + audio into MP4 using a subprocess ffmpeg call.
    Raises subprocess.CalledProcessError on failure.
    """
    cmd = [
        "ffmpeg",
        "-y",                               # overwrite without prompt
        "-i", str(video_path),              # silent video
        "-i", str(audio_path),              # audio track
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-pix_fmt", _PIXEL_FORMAT,
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",                        # trim to the shorter stream
        str(output_path),
    ]
    logger.info("ffmpeg command: %s", " ".join(cmd))

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=600,                        # 10-minute safety timeout
    )

    if result.returncode != 0:
        stderr_text = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(f"ffmpeg exited with code {result.returncode}:\n{stderr_text}")

    if not output_path.exists():
        raise FileNotFoundError(f"ffmpeg completed but output file not found: {output_path}")


def _fail(msg: str) -> dict:
    return {
        "success":    False,
        "video_path": "",
        "error":      msg,
    }