"""
backend/core/settings_additions.py
====================================
MERGE these settings blocks into your existing backend/core/settings.py.

Changes from the original:
  - Celery / Redis settings REMOVED (no longer needed)
  - ML pipeline path settings ADDED
  - MEDIA_ROOT updated to support generated_videos subdirectory
  - Request timeout settings ADDED for long-running sync pipeline calls
  - REST_FRAMEWORK DEFAULT_PERMISSION_CLASSES fixed (was AllowAny + IsAuthenticated)
"""

import os
from pathlib import Path
from datetime import timedelta
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# ──────────────────────────────────────────────────────────────────────────────
# MEDIA FILES  (replace existing MEDIA_URL / MEDIA_ROOT block)
# ──────────────────────────────────────────────────────────────────────────────

MEDIA_URL  = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# ──────────────────────────────────────────────────────────────────────────────
# ML PIPELINE PATHS
# ──────────────────────────────────────────────────────────────────────────────

# Absolute path to the Wav2Lip GAN checkpoint.
# Override in .env with WAV2LIP_CHECKPOINT=/abs/path/to/wav2lip_gan.pth
WAV2LIP_CHECKPOINT = config(
    "WAV2LIP_CHECKPOINT",
    default=str(BASE_DIR.parent / "ml_pipeline" / "models" / "checkpoints" / "wav2lip_gan.pth"),
)

# Root directory where avatar preprocessing writes output artifacts.
ML_STORAGE_ROOT = config(
    "ML_STORAGE_ROOT",
    default=str(BASE_DIR.parent / "ml_pipeline" / "storage"),
)

# Root for processed frame sub-dirs (avatar_frames/, mouth_frames/).
ML_PROCESSED_ROOT = config(
    "ML_PROCESSED_ROOT",
    default=str(BASE_DIR.parent / "ml_pipeline" / "data" / "processed"),
)

# ──────────────────────────────────────────────────────────────────────────────
# REST FRAMEWORK  (replace existing REST_FRAMEWORK block)
# ──────────────────────────────────────────────────────────────────────────────

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    # IMPORTANT: only ONE default permission class.
    # Having both IsAuthenticated and AllowAny simultaneously is contradictory.
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# ──────────────────────────────────────────────────────────────────────────────
# GUNICORN / UWSGI REQUEST TIMEOUT
# ──────────────────────────────────────────────────────────────────────────────
# The synchronous lipsync pipeline can take 30–90 seconds.
# Ensure your WSGI server timeout is set to at least 300 seconds.
#
# Gunicorn example (gunicorn.conf.py or CLI flag):
#   timeout = 300
#
# Django development server has no timeout.

# ──────────────────────────────────────────────────────────────────────────────
# LOGGING  (replace or merge into existing LOGGING block)
# ──────────────────────────────────────────────────────────────────────────────

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] [{levelname}] [{name}] {message}",
            "style":  "{",
        },
    },
    "handlers": {
        "console": {
            "class":     "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "users":                {"handlers": ["console"], "level": "INFO",    "propagate": False},
        "processing":           {"handlers": ["console"], "level": "INFO",    "propagate": False},
        "ml_pipeline":          {"handlers": ["console"], "level": "INFO",    "propagate": False},
        "wav2lip_inference":    {"handlers": ["console"], "level": "DEBUG",   "propagate": False},
        "pro_landmark_merge":   {"handlers": ["console"], "level": "INFO",    "propagate": False},
        "temporal_smoothing":   {"handlers": ["console"], "level": "INFO",    "propagate": False},
        "render_final_video":   {"handlers": ["console"], "level": "INFO",    "propagate": False},
        "lipsync_pipeline":     {"handlers": ["console"], "level": "INFO",    "propagate": False},
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# NOTE: Remove ALL Celery settings from settings.py.
# The following keys are no longer used and should be deleted:
#   CELERY_BROKER_URL
#   CELERY_RESULT_BACKEND
#   CELERY_TASK_SERIALIZER
#   CELERY_RESULT_SERIALIZER
#   CELERY_ACCEPT_CONTENT
#   CELERY_TIMEZONE
#   CELERY_ENABLE_UTC
#   CELERY_TASK_ROUTES
#   CELERY_WORKER_CONCURRENCY
#   CELERY_TASK_ACKS_LATE
#   CELERY_WORKER_PREFETCH_MULTIPLIER
#   CELERY_TASK_SOFT_TIME_LIMIT
#   CELERY_TASK_TIME_LIMIT
#   CELERY_IMPORTS
# ──────────────────────────────────────────────────────────────────────────────
