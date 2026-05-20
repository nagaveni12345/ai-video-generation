from __future__ import annotations

import os
import sys
from pathlib import Path

from celery import Celery

# ---------------------------------------------------------
# Ensure monorepo root is in PYTHONPATH
# ---------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# ---------------------------------------------------------
# Ensure backend package also visible
# ---------------------------------------------------------
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# ---------------------------------------------------------
# Django settings bootstrap
# ---------------------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.core.settings")

app = Celery("video_generation_worker")

# Load all CELERY_* settings from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto discover shared_task from installed apps + explicit worker package
app.autodiscover_tasks()

# Explicitly import worker tasks to ensure registration
app.conf.imports = ("worker.tasks",)