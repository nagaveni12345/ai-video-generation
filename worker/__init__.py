# worker/__init__.py
# Makes `worker` a proper Python package.
# Celery app is imported here so Django's AppConfig.ready()
# and the `celery -A worker.celery_app worker` boot command
# can both find the app instance without circular imports.

from worker.celery_app import app as celery_app  # noqa: F401

__all__ = ("celery_app",)