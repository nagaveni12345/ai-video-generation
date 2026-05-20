"""
ml_pipeline/config/app_config.py
Application-level configuration for the ML pipeline.
"""

import os
from pathlib import Path

# ──────────────────────────────────────────────
# Base paths
# ──────────────────────────────────────────────
ML_PIPELINE_ROOT = Path(__file__).resolve().parent.parent          # ml_pipeline/
PROJECT_ROOT     = ML_PIPELINE_ROOT.parent                          # VIDEO-GENERATION/

STORAGE_ROOT      = ML_PIPELINE_ROOT / "storage"
TEMP_DIR          = STORAGE_ROOT / "temp"
PROCESSED_DIR     = STORAGE_ROOT / "processed"
EXPORTS_DIR       = STORAGE_ROOT / "exports"

# Ensure directories exist at import time
for _d in (TEMP_DIR, PROCESSED_DIR, EXPORTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────
# Supported media types
# ──────────────────────────────────────────────
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
SUPPORTED_EXTENSIONS       = SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_VIDEO_EXTENSIONS

MAX_IMAGE_SIZE_MB = int(os.getenv("MAX_IMAGE_SIZE_MB", "20"))
MAX_VIDEO_SIZE_MB = int(os.getenv("MAX_VIDEO_SIZE_MB", "500"))

MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
MAX_VIDEO_SIZE_BYTES = MAX_VIDEO_SIZE_MB * 1024 * 1024

# ──────────────────────────────────────────────
# Frame extraction settings
# ──────────────────────────────────────────────
FRAME_EXTRACTION_FPS        = int(os.getenv("FRAME_EXTRACTION_FPS", "25"))
MAX_FRAMES_TO_EXTRACT       = int(os.getenv("MAX_FRAMES_TO_EXTRACT", "300"))
STABLE_FRAME_SAMPLE_COUNT   = int(os.getenv("STABLE_FRAME_SAMPLE_COUNT", "30"))
FRAME_QUALITY               = int(os.getenv("FRAME_QUALITY", "95"))   # JPEG quality

# ──────────────────────────────────────────────
# Face / image processing settings
# ──────────────────────────────────────────────
TARGET_FACE_SIZE   = (256, 256)   # (width, height) for aligned face
TARGET_MOUTH_SIZE  = (96, 96)     # (width, height) for mouth crop
FACE_PADDING_RATIO = 0.20          # extra padding around detected face bbox

# MediaPipe face mesh
FACE_MESH_MAX_FACES          = int(os.getenv("FACE_MESH_MAX_FACES", "1"))
FACE_MESH_MIN_DETECTION_CONF = float(os.getenv("FACE_MESH_MIN_DETECTION_CONF", "0.5"))
FACE_MESH_MIN_TRACKING_CONF  = float(os.getenv("FACE_MESH_MIN_TRACKING_CONF", "0.5"))

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────
LOG_LEVEL = os.getenv("ML_LOG_LEVEL", "INFO")
LOG_DIR   = ML_PIPELINE_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────
# Processing job settings
# ──────────────────────────────────────────────
JOB_TIMEOUT_SECONDS = int(os.getenv("JOB_TIMEOUT_SECONDS", "600"))