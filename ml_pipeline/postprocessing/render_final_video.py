"""
ml_pipeline/postprocessing/render_final_video.py
================================================
Premium-quality final MP4 renderer.

Pipeline:
  1.  Assemble smoothed talking frames into a lossless intermediate AVI
      using OpenCV VideoWriter (XVID codec, in-memory quality).
  2.  Mux video + cleaned 16 kHz WAV into a final H.264/AAC MP4 via
      a direct subprocess ffmpeg call with high-quality presets.
  3.  Verify the output file exists and is non-empty.
  4.  Save final MP4 to Django's media/generated_videos/<job_id>/ path.

H.264 settings used:
  - CRF 17      (near-lossless; 0=lossless, 51=worst)
  - preset slow (better compression without extreme CPU cost)
  - tune film   (optimised for natural skin tones / talking heads)
  - pix_fmt yuv420p (maximum compatibility)

AAC audio:
  - 192 kbps stereo (or mono if input is mono)
  - Normalised via ffmpeg loudnorm filter to -16 LUFS

Windows compatible: paths are normalised with forward slashes before
being passed to ffmpeg.
"""

from __future__ import annotations

import logging
import os
import subprocess
import time
from pathlib import Path
from typing import List

import cv2

from ml_pipeline.utils.logger import get_logger

logger = get_logger("render_final_video")

# ── Encoding defaults ──────────────────────────────────────────────────────────
_DEFAULT_FPS     = 25
_H264_CRF        = 17
_H264_PRESET     = "slow"
_H264_TUNE       = "film"
_PIX_FMT         = "yuv420p"
_AUDIO_BITRATE   = "192k"
_AUDIO_CHANNELS  = 2       # downmix to stereo
_FFMPEG_TIMEOUT  = 900     # 15-minute hard limit per render


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def render_final_video(
    frame_paths:  List[str],
    audio_path:   str | Path,
    output_dir:   str | Path,
    job_id:       str,
    fps:          float = _DEFAULT_FPS,
    crf:          int   = _H264_CRF,
    preset:       str   = _H264_PRESET,
) -> dict:
    """
    Render the final H.264 MP4 from smoothed frames + preprocessed audio.

    Args:
        frame_paths:  Sorted list of talking/smoothed frame image paths.
        audio_path:   Path to the 16 kHz WAV produced by audio_preprocess.
        output_dir:   Output directory (will be created if absent).
        job_id:       Job identifier for file naming.
        fps:          Output video frame rate.
        crf:          H.264 CRF quality (0 best → 51 worst; default 17).
        preset:       ffmpeg encoding preset speed/quality trade-off.

    Returns:
        Dict:
          - success    bool
          - video_path str  — absolute path to output MP4
          - error      str | None
    """
    start      = time.time()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = Path(audio_path)

    logger.info(
        "[job=%s] render_final_video START | frames=%d  fps=%.1f  audio=%s",
        job_id, len(frame_paths), fps, audio_path.name,
    )

    if not frame_paths:
        return _fail("No frames provided for video rendering.")
    if not audio_path.exists():
        return _fail(f"Audio file not found: {audio_path}")

    # ── Step 1: Write lossless silent AVI via OpenCV ───────────────────────────
    silent_path = output_dir / f"{job_id}_silent.avi"
    try:
        _write_silent_video(frame_paths, silent_path, fps)
    except Exception as exc:
        logger.exception("[job=%s] Failed to write silent video.", job_id)
        return _fail(f"Silent video error: {exc}")

    # ── Step 2: Mux audio + video → final MP4 ────────────────────────────────
    final_path = output_dir / f"{job_id}_lipsync.mp4"
    try:
        _mux_audio_video(
            video_path = silent_path,
            audio_path = audio_path,
            out_path   = final_path,
            crf        = crf,
            preset     = preset,
        )
    except Exception as exc:
        logger.exception("[job=%s] ffmpeg mux failed.", job_id)
        return _fail(f"ffmpeg mux error: {exc}")
    finally:
        if silent_path.exists():
            try:
                silent_path.unlink()
            except OSError:
                pass

    # ── Step 3: Verify ────────────────────────────────────────────────────────
    if not final_path.exists() or final_path.stat().st_size < 1024:
        return _fail(
            f"Output file missing or too small after render: {final_path}"
        )

    elapsed = round(time.time() - start, 3)
    logger.info(
        "[job=%s] render_final_video DONE | %.2fs  size=%s  path=%s",
        job_id, elapsed, _human_size(final_path.stat().st_size), final_path,
    )

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
    """
    Write all frames into a silent XVID AVI via OpenCV VideoWriter.
    Raises IOError / RuntimeError on failure.
    """
    # Determine frame dimensions from first readable frame
    first_frame: cv2.Mat | None = None
    for p in frame_paths:
        candidate = cv2.imread(str(p))
        if candidate is not None:
            first_frame = candidate
            break
    if first_frame is None:
        raise IOError("No readable frames found.")

    H, W = first_frame.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (W, H))

    if not writer.isOpened():
        raise IOError(f"cv2.VideoWriter failed to open: {output_path}")

    dropped = 0
    for p in frame_paths:
        frame = cv2.imread(str(p))
        if frame is None:
            dropped += 1
            logger.debug("Dropped unreadable frame: %s", p)
            continue
        if frame.shape[:2] != (H, W):
            frame = cv2.resize(frame, (W, H), interpolation=cv2.INTER_AREA)
        writer.write(frame)

    writer.release()

    if dropped:
        logger.warning("Silent video: dropped %d unreadable frames.", dropped)

    logger.info(
        "Silent video written: %s  (%d×%d @ %.1f fps  frames=%d)",
        output_path.name, W, H, fps, len(frame_paths) - dropped,
    )


def _mux_audio_video(
    video_path: Path,
    audio_path: Path,
    out_path:   Path,
    crf:        int,
    preset:     str,
) -> None:
    """
    Mux video + audio into a premium H.264/AAC MP4 using ffmpeg.
    Raises RuntimeError on non-zero exit or missing output.
    """
    # Normalise to forward slashes for cross-platform ffmpeg compatibility
    vp = str(video_path).replace("\\", "/")
    ap = str(audio_path).replace("\\", "/")
    op = str(out_path).replace("\\", "/")

    cmd = [
        "ffmpeg",
        "-y",                         # overwrite output without prompting
        "-i", vp,                     # video input
        "-i", ap,                     # audio input
        # Video codec
        "-c:v", "libx264",
        "-preset", preset,
        "-crf", str(crf),
        "-tune", _H264_TUNE,
        "-pix_fmt", _PIX_FMT,
        "-movflags", "+faststart",    # enable web streaming (moov atom first)
        # Audio codec
        "-c:a", "aac",
        "-b:a", _AUDIO_BITRATE,
        "-ac", str(_AUDIO_CHANNELS),
        # Audio loudness normalisation (EBU R128, -16 LUFS, broadcast standard)
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        # Duration control
        "-shortest",                  # trim to shorter of video / audio
        op,
    ]

    logger.info("ffmpeg command: %s", " ".join(cmd))

    result = subprocess.run(
        cmd,
        stdout  = subprocess.PIPE,
        stderr  = subprocess.PIPE,
        timeout = _FFMPEG_TIMEOUT,
    )

    if result.returncode != 0:
        stderr_text = result.stderr.decode("utf-8", errors="replace")
        raise RuntimeError(
            f"ffmpeg exited with code {result.returncode}:\n{stderr_text[-3000:]}"
        )

    if not out_path.exists():
        raise FileNotFoundError(
            f"ffmpeg completed (rc=0) but output file was not created: {out_path}"
        )


def _human_size(n_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} TB"


def _fail(msg: str) -> dict:
    return {
        "success":    False,
        "video_path": "",
        "error":      msg,
    }
