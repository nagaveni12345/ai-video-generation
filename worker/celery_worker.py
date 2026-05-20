"""
worker/celery_worker.py
=======================
Optional standalone entry-point for environments that can't easily use
`celery -A worker.celery_app worker` (e.g., Docker CMD, Windows batch).

Usage:
    python -m worker.celery_worker

Or as a Docker CMD:
    CMD ["python", "-m", "worker.celery_worker"]
"""

from __future__ import annotations

import sys

from worker.celery_app import app

if __name__ == "__main__":
    # Pass any extra CLI args through (e.g., --loglevel=debug)
    argv = ["worker", "--loglevel=info", "-Q", "ml_tasks,celery"] + sys.argv[1:]
    app.worker_main(argv)