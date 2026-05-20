# backend/core/__init__.py
# Ensure the Celery app is loaded when Django starts so that
# @shared_task decorators in worker/tasks.py are bound to our app.
#from .celery import app as celery_app  # noqa: F401

#__all__ = ("celery_app",)