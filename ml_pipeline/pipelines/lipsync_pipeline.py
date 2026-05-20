"""
ml_pipeline/pipelines/lipsync_pipeline.py
==========================================
Central synchronous orchestrator for the end-to-end Wav2Lip pipeline.

Stage flow:
  1.  Resolve preprocessed avatar artifacts (face frames + mouth crops)
  2.  Audio preprocessing   → mel chunks + cleaned WAV
  3.  Wav2Lip inference     → 96×96 lipsync mouth frames
  4.  Pro landmark merge    → full-res talking frames
  5.  Temporal smoothing    → flicker-reduced frames
  6.  Final video render    → H.264 MP4 with normalised audio

Everything runs in the calling thread/process.  No Celery, no queues.
The function blocks until the MP4 is written, then returns a
LipsyncPipelineResult.

Avatar artifact layout (written by avatar_pipeline.py):
  ml_pipeline/storage/processed/<avatar_id>/
    faces/          ← aligned face frames (JPEG)
    mouth_crops/    ← mouth crop frames (JPEG)
    landmarks/      ← optional JSON metadata
    metadata.json   ← optional face_box global metadata
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from ml_pipeline.utils.logger import get_logger

logger = get_logger("lipsync_pipeline")

# ── Image glob patterns ────────────────────────────────────────────────────────
_IMG_GLOBS = ("*.jpg", "*.jpeg", "*.png")


# ──────────────────────────────────────────────────────────────────────────────
# Storage path resolution  (same helper as before; avoids circular imports)
# ──────────────────────────────────────────────────────────────────────────────

def _storage_root(setting_name: str, default_relative: str) -> Path:
    try:
        from django.conf import settings  # noqa: PLC0415
        configured = getattr(settings, setting_name, None)
        if configured:
            return Path(configured).resolve()
        base_dir = Path(settings.BASE_DIR)
        return (base_dir.parent / default_relative).resolve()
    except Exception:
        here         = Path(__file__).resolve()
        project_root = here.parent.parent.parent  # pipelines → ml_pipeline → root
        return (project_root / default_relative).resolve()


_PROCESSED_ROOT  = _storage_root("ML_PROCESSED_ROOT", "ml_pipeline/data/processed")
_STORAGE_ROOT    = _storage_root("ML_STORAGE_ROOT",   "ml_pipeline/storage")
_WAV2LIP_CKPT    = _storage_root(
    "WAV2LIP_CHECKPOINT",
    "ml_pipeline/models/checkpoints/wav2lip_gan.pth",
)


# ──────────────────────────────────────────────────────────────────────────────
# Result dataclass
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class LipsyncPipelineResult:
    success:       bool
    job_id:        str
    avatar_id:     str
    video_path:    str           = ""
    wav_path:      str           = ""
    num_frames:    int           = 0
    duration_sec:  float         = 0.0
    elapsed_sec:   float         = 0.0
    stage_timings: dict          = field(default_factory=dict)
    warnings:      List[str]     = field(default_factory=list)
    error:         Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "success":       self.success,
            "job_id":        self.job_id,
            "avatar_id":     self.avatar_id,
            "video_path":    self.video_path,
            "wav_path":      self.wav_path,
            "num_frames":    self.num_frames,
            "duration_sec":  self.duration_sec,
            "elapsed_sec":   self.elapsed_sec,
            "stage_timings": self.stage_timings,
            "warnings":      self.warnings,
            "error":         self.error,
        }


# ──────────────────────────────────────────────────────────────────────────────
# Main entry point
# ──────────────────────────────────────────────────────────────────────────────

def run_lipsync_pipeline(
    job_id:     str,
    avatar_id:  str,
    audio_path: str | Path,
    video_fps:  float = 25.0,
) -> LipsyncPipelineResult:
    """
    Run all five stages of the lipsync pipeline and return a
    LipsyncPipelineResult.

    Args:
        job_id:     Unique job identifier (used as directory key).
        avatar_id:  The preprocessing job id whose artifacts to use.
        audio_path: Absolute path to the user's audio file.
        video_fps:  Target output frame rate (default 25).

    Returns:
        LipsyncPipelineResult (check .success and .error).
    """
    wall_start = time.time()
    timings:  dict       = {}
    warnings: List[str]  = []

    logger.info(
        "[job=%s] ════════ LipsyncPipeline START | avatar=%s ════════",
        job_id, avatar_id,
    )

    # ── Resolve preprocessed artifacts ────────────────────────────────────────
    artifacts = _resolve_avatar_artifacts(avatar_id)
    if artifacts is None:
        return _fail(
            job_id, avatar_id,
            f"No preprocessed artifacts found for avatar '{avatar_id}'. "
            f"Searched: {_STORAGE_ROOT / 'processed' / avatar_id}",
            wall_start,
        )

    avatar_frames = artifacts["avatar_frames"]      # aligned crops for Wav2Lip
    original_frames = artifacts["original_frames"]  # full resolution for final merge
    mouth_frames = artifacts["mouth_frames"]

    if not avatar_frames:
        return _fail(job_id, avatar_id, "No face frames in preprocessed output.", wall_start)
    if not mouth_frames:
        return _fail(job_id, avatar_id, "No mouth crop frames in preprocessed output.", wall_start)

    logger.info(
        "[job=%s] Artifacts resolved | face_frames=%d  mouth_frames=%d",
        job_id, len(avatar_frames), len(mouth_frames),
    )

    # ── Job output directory layout ───────────────────────────────────────────
    job_dir         = _STORAGE_ROOT / "processed" / job_id
    audio_out_dir   = job_dir / "audio"
    lipsync_out_dir = job_dir / "lipsync_frames"
    merged_out_dir  = job_dir / "talking_frames"
    smooth_out_dir  = job_dir / "smooth_frames"
    video_out_dir   = _resolve_media_output_dir(job_id)

    for d in [audio_out_dir, lipsync_out_dir, merged_out_dir, smooth_out_dir, video_out_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # ─────────────────────────────────────────────────────────────────────────
    # STAGE 1: Audio preprocessing
    # ─────────────────────────────────────────────────────────────────────────
    logger.info("[job=%s] ── Stage 1/5: Audio preprocessing", job_id)
    t0 = time.time()

    from ml_pipeline.preprocessing.audio_preprocess import preprocess_audio  # noqa: PLC0415

    audio_result = preprocess_audio(
        audio_path = audio_path,
        job_id     = job_id,
        output_dir = audio_out_dir,
        video_fps  = video_fps,
    )
    timings["audio_sec"] = round(time.time() - t0, 3)

    if not audio_result["success"]:
        return _fail(
            job_id, avatar_id,
            f"Audio preprocessing failed: {audio_result['error']}",
            wall_start,
        )

    mel_chunks   = audio_result["mel_chunks"]
    wav_path     = audio_result["wav_path"]
    duration_sec = audio_result["duration_sec"]
    logger.info(
        "[job=%s] Audio done | mel_chunks=%d  duration=%.2fs",
        job_id, len(mel_chunks), duration_sec,
    )

    # ─────────────────────────────────────────────────────────────────────────
    # STAGE 2: Wav2Lip inference
    # ─────────────────────────────────────────────────────────────────────────
    logger.info("[job=%s] ── Stage 2/5: Wav2Lip inference", job_id)
    t0 = time.time()

    from ml_pipeline.inference.wav2lip_inference import run_lipsync_inference  # noqa: PLC0415

    inference_result = run_lipsync_inference(
        mouth_frame_paths = avatar_frames,
        mel_chunks        = mel_chunks,
        output_dir        = lipsync_out_dir,
        job_id            = job_id,
        checkpoint_path   = _WAV2LIP_CKPT,
    )
    timings["inference_sec"] = round(time.time() - t0, 3)

    if not inference_result["success"]:
        return _fail(
            job_id, avatar_id,
            f"Wav2Lip inference failed: {inference_result['error']}",
            wall_start,
        )

    generated_frames = inference_result["generated_frames"]
    logger.info("[job=%s] Inference done | frames=%d", job_id, len(generated_frames))

    # ─────────────────────────────────────────────────────────────────────────
    # STAGE 3: Professional landmark-based merge
    # ─────────────────────────────────────────────────────────────────────────
    logger.info("[job=%s] ── Stage 3/5: Pro landmark merge", job_id)
    t0 = time.time()

    from ml_pipeline.postprocessing.pro_landmark_merge import merge_lipsync_frames_pro  # noqa: PLC0415

    merge_result = merge_lipsync_frames_pro(
        avatar_frame_paths  = original_frames,
        lipsync_frame_paths = generated_frames,
        output_dir          = merged_out_dir,
        job_id              = job_id,
    )
    timings["merge_sec"] = round(time.time() - t0, 3)

    if not merge_result["success"]:
        return _fail(
            job_id, avatar_id,
            f"Frame merge failed: {merge_result['error']}",
            wall_start,
        )

    merged_frames = merge_result["merged_frames"]
    warnings.extend(merge_result.get("warnings", []))
    logger.info("[job=%s] Merge done | frames=%d", job_id, len(merged_frames))

    # ─────────────────────────────────────────────────────────────────────────
    # STAGE 4: Temporal smoothing
    # ─────────────────────────────────────────────────────────────────────────
    logger.info("[job=%s] ── Stage 4/5: Temporal smoothing", job_id)
    t0 = time.time()

    from ml_pipeline.postprocessing.temporal_smoothing import smooth_talking_frames  # noqa: PLC0415

    smooth_result = smooth_talking_frames(
        frame_paths = merged_frames,
        output_dir  = smooth_out_dir,
        job_id      = job_id,
        window      = 5,
        sigma       = 1.0,
        use_optical_flow = False,   # set True for video avatars with head motion
    )
    timings["smooth_sec"] = round(time.time() - t0, 3)

    if not smooth_result["success"]:
        # Smoothing failure is non-fatal — fall back to unsmoothed frames
        warnings.append(
            f"Temporal smoothing failed ({smooth_result['error']}); "
            "using unsmoothed frames."
        )
        final_frames = merged_frames
    else:
        final_frames = smooth_result["smooth_frames"]
        logger.info("[job=%s] Smoothing done | frames=%d", job_id, len(final_frames))

    # ─────────────────────────────────────────────────────────────────────────
    # STAGE 5: Final video render
    # ─────────────────────────────────────────────────────────────────────────
    logger.info("[job=%s] ── Stage 5/5: Final video render", job_id)
    t0 = time.time()

    from ml_pipeline.postprocessing.render_final_video import render_final_video  # noqa: PLC0415

    render_result = render_final_video(
        frame_paths = final_frames,
        audio_path  = wav_path,
        output_dir  = video_out_dir,
        job_id      = job_id,
        fps         = video_fps,
    )
    timings["render_sec"] = round(time.time() - t0, 3)

    if not render_result["success"]:
        return _fail(
            job_id, avatar_id,
            f"Video render failed: {render_result['error']}",
            wall_start,
        )

    video_path  = render_result["video_path"]
    elapsed_sec = round(time.time() - wall_start, 3)

    logger.info(
        "[job=%s] ════════ LipsyncPipeline COMPLETE | %.2fs | video=%s ════════",
        job_id, elapsed_sec, video_path,
    )

    return LipsyncPipelineResult(
        success       = True,
        job_id        = job_id,
        avatar_id     = avatar_id,
        video_path    = video_path,
        wav_path      = wav_path,
        num_frames    = len(final_frames),
        duration_sec  = duration_sec,
        elapsed_sec   = elapsed_sec,
        stage_timings = timings,
        warnings      = warnings,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Artifact resolution
# ──────────────────────────────────────────────────────────────────────────────

def _glob_images(directory: Path) -> List[str]:
    results = []
    for pat in _IMG_GLOBS:
        results.extend(directory.glob(pat))
    return sorted(str(p) for p in results)


def _resolve_avatar_artifacts(avatar_id: str) -> Optional[dict]:
    """
    Locate face frames and mouth crops for a given preprocessing job id.

    Layout 1 (storage/processed/<id>/):
      faces/        mouth_crops/    landmarks/    metadata.json

    Layout 2 (data/processed/):
      avatar_frames/<id>/    mouth_frames/<id>/    landmarks/<id>/
    """
    # Layout 1
    storage_dir   = _STORAGE_ROOT / "processed" / avatar_id
    faces_dir      = storage_dir / "faces"
    originals_dir  = storage_dir / "original_frames"
    mouths_dir     = storage_dir / "mouth_crops"
    landmarks_dir  = storage_dir / "landmarks"

    # Layout 2 fallback
    if not faces_dir.exists():
        faces_dir     = _PROCESSED_ROOT / "avatar_frames" / avatar_id
        mouths_dir    = _PROCESSED_ROOT / "mouth_frames"  / avatar_id
        landmarks_dir = _PROCESSED_ROOT / "landmarks"     / avatar_id

    if not faces_dir.exists():
        logger.error(
            "_resolve_avatar_artifacts: no faces dir found.\n"
            "  Tried: %s\n  Tried: %s",
            storage_dir / "faces",
            _PROCESSED_ROOT / "avatar_frames" / avatar_id,
        )
        return None

    avatar_frames = _glob_images(faces_dir)
    original_frames = _glob_images(originals_dir) if originals_dir.exists() else _glob_images(faces_dir)
    mouth_frames = _glob_images(mouths_dir) if mouths_dir.exists() else []

    # Read optional global face_box metadata
    face_box = None
    for meta_path in [
        landmarks_dir / "metadata.json",
        storage_dir   / "metadata.json",
    ]:
        if meta_path.exists():
            try:
                with open(meta_path) as f:
                    meta = json.load(f)
                face_box = meta.get("face_box")
                break
            except Exception as exc:
                logger.debug("Failed reading metadata %s: %s", meta_path, exc)

    return {
        "avatar_frames": avatar_frames,
        "original_frames": original_frames,
        "mouth_frames":  mouth_frames,
        "landmark_dir":  str(landmarks_dir),
        "face_box":      face_box,
    }


def _resolve_media_output_dir(job_id: str) -> Path:
    """
    Return (and create) the Django media output directory for this job.
    Falls back to ml_pipeline/storage/exports/<job_id>/ if Django is not
    configured.
    """
    try:
        from django.conf import settings  # noqa: PLC0415
        media_root = Path(settings.MEDIA_ROOT)
        out_dir    = media_root / "generated_videos" / job_id
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir
    except Exception:
        fallback = _STORAGE_ROOT / "exports" / job_id
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def _fail(
    job_id:     str,
    avatar_id:  str,
    error_msg:  str,
    wall_start: float,
) -> LipsyncPipelineResult:
    logger.error("[job=%s] Pipeline FAILED: %s", job_id, error_msg)
    return LipsyncPipelineResult(
        success     = False,
        job_id      = job_id,
        avatar_id   = avatar_id,
        elapsed_sec = round(time.time() - wall_start, 3),
        error       = error_msg,
    )
