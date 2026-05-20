"""
services/file_helpers.py
Reusable file-system, path, and ffmpeg utility helpers shared across
the video-generation monolith.

Import anywhere:
    from services.file_helpers import ensure_dir, get_job_output_dir, probe_video
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional

# ──────────────────────────────────────────────────────────────────────────────
# Directory helpers
# ──────────────────────────────────────────────────────────────────────────────

def ensure_dir(path: str | Path) -> Path:
    """Create *path* (including parents) if it doesn't exist and return it."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_job_output_dir(base: str | Path, job_id: str) -> Path:
    """Return ml_pipeline/storage/processed/<job_id>/ and ensure it exists."""
    return ensure_dir(Path(base) / job_id)


def safe_delete(path: str | Path) -> bool:
    """Delete a file or directory tree; return True if deleted, False if absent."""
    p = Path(path)
    try:
        if p.is_file():
            p.unlink()
            return True
        if p.is_dir():
            shutil.rmtree(str(p))
            return True
    except Exception:
        pass
    return False


def collect_images(directory: str | Path, extensions: tuple = (".jpg", ".jpeg", ".png")) -> list[str]:
    """Return a sorted list of image paths inside *directory*."""
    d = Path(directory)
    if not d.exists():
        return []
    return sorted(str(p) for p in d.iterdir() if p.suffix.lower() in extensions)


# ──────────────────────────────────────────────────────────────────────────────
# ffmpeg helpers
# ──────────────────────────────────────────────────────────────────────────────

def ffmpeg_available() -> bool:
    """Return True if ffmpeg is present in PATH."""
    return shutil.which("ffmpeg") is not None


def probe_video(video_path: str | Path) -> Optional[dict]:
    """
    Run ffprobe on *video_path* and return a dict with basic stream info.
    Returns None if ffprobe is unavailable or fails.

    Returned keys:
      duration_sec, width, height, fps, codec_name, audio_codec
    """
    if shutil.which("ffprobe") is None:
        return None

    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        str(video_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode != 0:
            return None
        data    = json.loads(result.stdout)
        streams = data.get("streams", [])

        video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})

        fps_raw = video_stream.get("avg_frame_rate", "0/1")
        try:
            num, den = fps_raw.split("/")
            fps = float(num) / float(den) if float(den) else 0.0
        except Exception:
            fps = 0.0

        return {
            "duration_sec": float(video_stream.get("duration", 0)),
            "width":        int(video_stream.get("width",    0)),
            "height":       int(video_stream.get("height",   0)),
            "fps":          fps,
            "codec_name":   video_stream.get("codec_name", ""),
            "audio_codec":  audio_stream.get("codec_name", ""),
        }
    except Exception:
        return None


def extract_audio_from_video(
    video_path:  str | Path,
    output_path: str | Path,
    sample_rate: int = 16_000,
) -> bool:
    """
    Extract audio from *video_path* and save as a mono WAV at *sample_rate*.
    Returns True on success.
    """
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-ac", "1",
        "-ar", str(sample_rate),
        "-vn",
        str(output_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=120)
        return result.returncode == 0 and Path(output_path).exists()
    except Exception:
        return False


def concat_videos(
    input_paths: list[str | Path],
    output_path: str | Path,
) -> bool:
    """
    Concatenate multiple MP4 files into a single output using ffmpeg concat demuxer.
    Returns True on success.
    """
    if not input_paths:
        return False

    # Write concat list file
    concat_list = Path(output_path).parent / "_concat_list.txt"
    with open(concat_list, "w") as f:
        for p in input_paths:
            f.write(f"file '{Path(p).resolve()}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(output_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=300)
        return result.returncode == 0 and Path(output_path).exists()
    except Exception:
        return False
    finally:
        safe_delete(concat_list)