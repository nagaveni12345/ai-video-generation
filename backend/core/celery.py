"""
backend/core/celery.py
======================
Bootstrap file that Django's AppConfig.ready() will import.
This file intentionally just re-exports the app from worker/celery_app.py
so that `celery -A core.celery worker` also works as an alternative
boot path if developers prefer pointing at the Django core package.

Preferred boot command:
    celery -A worker.celery_app worker --loglevel=info

Alternative (also valid):
    celery -A core.celery worker --loglevel=info
"""

# Re-export from the canonical location.
from worker.celery_app import app as celery_app  # noqa: F401

__all__ = ("celery_app",)