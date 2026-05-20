"""
ml_pipeline/config/model_config.py
Paths and hyper-parameters for every ML model used in the pipeline.
"""

import os
from pathlib import Path

ML_PIPELINE_ROOT = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────
# Model root directories
# ──────────────────────────────────────────────
MODELS_ROOT   = ML_PIPELINE_ROOT / "models"
CHECKPOINTS   = MODELS_ROOT / "checkpoints"
WEIGHTS_DIR   = MODELS_ROOT / "weights"
ONNX_DIR      = MODELS_ROOT / "onnx"

for _d in (CHECKPOINTS, WEIGHTS_DIR, ONNX_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────
# Wav2Lip
# ──────────────────────────────────────────────
WAV2LIP_CHECKPOINT = os.getenv(
    "WAV2LIP_CHECKPOINT",
    str(CHECKPOINTS / "wav2lip_gan.pth"),
)
WAV2LIP_BATCH_SIZE = int(os.getenv("WAV2LIP_BATCH_SIZE", "128"))
WAV2LIP_RESIZE_FACTOR = int(os.getenv("WAV2LIP_RESIZE_FACTOR", "1"))
WAV2LIP_FACE_DET_BATCH = int(os.getenv("WAV2LIP_FACE_DET_BATCH", "16"))
WAV2LIP_PAD_TOP    = int(os.getenv("WAV2LIP_PAD_TOP", "0"))
WAV2LIP_PAD_BOTTOM = int(os.getenv("WAV2LIP_PAD_BOTTOM", "10"))
WAV2LIP_PAD_LEFT   = int(os.getenv("WAV2LIP_PAD_LEFT", "0"))
WAV2LIP_PAD_RIGHT  = int(os.getenv("WAV2LIP_PAD_RIGHT", "0"))

# ──────────────────────────────────────────────
# Whisper (speech-to-text / transcription)
# ──────────────────────────────────────────────
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")  # tiny/base/small/medium/large
WHISPER_DEVICE     = os.getenv("WHISPER_DEVICE", "cpu")

# ──────────────────────────────────────────────
# XTTS (voice cloning / TTS)
# ──────────────────────────────────────────────
XTTS_MODEL_PATH   = os.getenv("XTTS_MODEL_PATH", str(MODELS_ROOT / "xtts"))
XTTS_SAMPLE_RATE  = int(os.getenv("XTTS_SAMPLE_RATE", "22050"))

# ──────────────────────────────────────────────
# Face detection (OpenCV DNN or MediaPipe)
# ──────────────────────────────────────────────
USE_MEDIAPIPE_FACE_DETECTION = os.getenv("USE_MEDIAPIPE_FACE_DETECTION", "true").lower() == "true"

# OpenCV Haar-cascade fallback
HAAR_CASCADE_PATH = os.getenv(
    "HAAR_CASCADE_PATH",
    str(WEIGHTS_DIR / "haarcascade_frontalface_default.xml"),
)

# ──────────────────────────────────────────────
# GPU / device
# ──────────────────────────────────────────────
DEVICE              = os.getenv("ML_DEVICE", "cpu")   # "cpu" | "cuda" | "cuda:0"
GPU_MEMORY_FRACTION = float(os.getenv("GPU_MEMORY_FRACTION", "0.8"))