"""
ml_pipeline/preprocessing/audio_preprocess.py
Audio preprocessing pipeline for Wav2Lip lip-sync inference.

Responsibilities:
  1. Load wav / mp3 / any librosa-supported format
  2. Resample to 16 kHz mono (Wav2Lip requirement)
  3. Normalize amplitude
  4. Save clean WAV to job directory
  5. Generate mel-spectrogram chunks aligned to video frames
  6. Return structured metadata + chunk array ready for inference
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import List

import librosa
import numpy as np
import soundfile as sf

from ml_pipeline.utils.logger import get_logger

logger = get_logger("audio_preprocess")

# ── Wav2Lip audio constants ────────────────────────────────────────────────────
SAMPLE_RATE       = 16_000          # Hz  — Wav2Lip was trained at 16 kHz
N_FFT             = 800
HOP_LENGTH        = 200             # 200 / 16000 = 12.5 ms per hop
WIN_LENGTH        = 800
N_MELS            = 80
MEL_FMIN          = 55.0
MEL_FMAX          = 7_600.0
# Each Wav2Lip inference step consumes a mel window of this many frames
MEL_STEP_SIZE     = 16              # mel frames per video frame chunk
# Normalisation constant
_MIN_DB           = -100.0          # floor before normalisation


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def preprocess_audio(
    audio_path:  str | Path,
    job_id:      str,
    output_dir:  str | Path,
    video_fps:   float = 25.0,
) -> dict:
    """
    Full audio preprocessing pipeline for a single job.

    Args:
        audio_path:  Path to the uploaded audio file (wav, mp3, ogg, flac …).
        job_id:      Unique job identifier used for output file naming.
        output_dir:  Directory where the preprocessed WAV is saved.
        video_fps:   FPS of the target avatar video (used to align mel chunks).

    Returns:
        Dict with keys:
          - ``success``         bool
          - ``wav_path``        str   — path to saved 16 kHz mono WAV
          - ``mel_chunks``      list[np.ndarray]  — each shape (80, MEL_STEP_SIZE)
          - ``duration_sec``    float
          - ``sample_rate``     int   (16000)
          - ``total_mel_frames`` int
          - ``num_chunks``      int
          - ``error``           str | None
    """
    start     = time.time()
    audio_path = Path(audio_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("[job=%s] Starting audio preprocessing: %s", job_id, audio_path.name)

    # ── 1. Existence check ─────────────────────────────────────────────────────
    if not audio_path.exists():
        msg = f"Audio file not found: {audio_path}"
        logger.error("[job=%s] %s", job_id, msg)
        return _failure(msg)

    # ── 2. Load & resample ─────────────────────────────────────────────────────
    try:
        wav, orig_sr = librosa.load(str(audio_path), sr=None, mono=True)
        logger.info(
            "[job=%s] Loaded audio: orig_sr=%d  samples=%d  dur=%.2fs",
            job_id, orig_sr, len(wav), len(wav) / orig_sr,
        )
    except Exception as exc:
        msg = f"librosa.load failed: {exc}"
        logger.exception("[job=%s] %s", job_id, msg)
        return _failure(msg)

    if orig_sr != SAMPLE_RATE:
        logger.info("[job=%s] Resampling %d → %d Hz …", job_id, orig_sr, SAMPLE_RATE)
        wav = librosa.resample(wav, orig_sr=orig_sr, target_sr=SAMPLE_RATE)

    # ── 3. Normalise amplitude (peak norm to -1 … +1) ─────────────────────────
    peak = np.abs(wav).max()
    if peak > 1e-6:
        wav = wav / peak
    else:
        logger.warning("[job=%s] Audio peak is near-zero — file may be silent.", job_id)

    duration_sec = len(wav) / SAMPLE_RATE
    logger.info("[job=%s] Duration after resample: %.2fs", job_id, duration_sec)

    # ── 4. Save clean WAV ─────────────────────────────────────────────────────
    wav_out = output_dir / f"{job_id}_audio_16k.wav"
    try:
        sf.write(str(wav_out), wav, SAMPLE_RATE, subtype="PCM_16")
        logger.info("[job=%s] Saved 16 kHz WAV → %s", job_id, wav_out)
    except Exception as exc:
        msg = f"Failed to write WAV: {exc}"
        logger.exception("[job=%s] %s", job_id, msg)
        return _failure(msg)

    # ── 5. Mel spectrogram ────────────────────────────────────────────────────
    mel = _wav_to_mel(wav)
    total_mel_frames = mel.shape[1]
    logger.info("[job=%s] Mel shape: %s", job_id, mel.shape)

    # ── 6. Chunk mel into per-video-frame slices ──────────────────────────────
    mel_chunks = _build_mel_chunks(mel, video_fps)
    logger.info("[job=%s] Mel chunks generated: %d", job_id, len(mel_chunks))

    elapsed = time.time() - start
    logger.info("[job=%s] Audio preprocessing done in %.2fs.", job_id, elapsed)

    return {
        "success":          True,
        "wav_path":         str(wav_out),
        "mel_chunks":       mel_chunks,
        "duration_sec":     duration_sec,
        "sample_rate":      SAMPLE_RATE,
        "total_mel_frames": total_mel_frames,
        "num_chunks":       len(mel_chunks),
        "error":            None,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _wav_to_mel(wav: np.ndarray) -> np.ndarray:
    """
    Convert a 16 kHz mono waveform to a normalised mel spectrogram.

    Returns:
        ndarray of shape (N_MELS, T) in range [0, 1].
    """
    mel = librosa.feature.melspectrogram(
        y          = wav,
        sr         = SAMPLE_RATE,
        n_fft      = N_FFT,
        hop_length = HOP_LENGTH,
        win_length = WIN_LENGTH,
        n_mels     = N_MELS,
        fmin       = MEL_FMIN,
        fmax       = MEL_FMAX,
    )
    mel_db = librosa.power_to_db(mel, ref=np.max)

    # Normalise to [0, 1]
    mel_db = np.clip(mel_db, _MIN_DB, 0.0)
    mel_db = (mel_db - _MIN_DB) / (-_MIN_DB)          # → [0, 1]
    return mel_db.astype(np.float32)


def _build_mel_chunks(
    mel:       np.ndarray,
    video_fps: float,
) -> List[np.ndarray]:
    """
    Slice the mel spectrogram into overlapping windows aligned to video frames.

    Each chunk is shape ``(N_MELS, MEL_STEP_SIZE)``; Wav2Lip treats each chunk
    as the audio context for a single output video frame.

    Args:
        mel:       Full mel spectrogram, shape (N_MELS, T).
        video_fps: Target video frame rate.

    Returns:
        List of numpy arrays, one per video frame.
    """
    # How many mel frames correspond to one video frame
    mel_frames_per_video_frame = int(SAMPLE_RATE / HOP_LENGTH / video_fps)
    if mel_frames_per_video_frame < 1:
        mel_frames_per_video_frame = 1

    total_mel_frames = mel.shape[1]
    chunks: List[np.ndarray] = []
    i = 0

    while True:
        start_mel = i * mel_frames_per_video_frame
        end_mel   = start_mel + MEL_STEP_SIZE

        if start_mel >= total_mel_frames:
            break

        if end_mel > total_mel_frames:
            # Pad last chunk with zeros
            chunk = mel[:, start_mel:]
            pad   = MEL_STEP_SIZE - chunk.shape[1]
            chunk = np.pad(chunk, ((0, 0), (0, pad)), mode="constant")
        else:
            chunk = mel[:, start_mel:end_mel]

        chunks.append(chunk.copy())
        i += 1

    return chunks


def _failure(error_msg: str) -> dict:
    return {
        "success":          False,
        "wav_path":         "",
        "mel_chunks":       [],
        "duration_sec":     0.0,
        "sample_rate":      SAMPLE_RATE,
        "total_mel_frames": 0,
        "num_chunks":       0,
        "error":            error_msg,
    }