


"""
backend/processing/models.py
============================
Django ORM model for lipsync job tracking.

Updated for synchronous (no-Celery) architecture:
  - mark_processing() / mark_completed() / mark_failed() convenience methods
  - elapsed_sec and stage_timings fields for performance telemetry
  - No Celery task_id field (removed; no async workers)
"""

from __future__ import annotations
import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings


def video_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"processing/videos/{filename}"

def result_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return f"processing/results/{filename}"

class VideoSync(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='video_syncs')
    video               = models.FileField(upload_to=video_upload_path)
    script              = models.TextField()
    hand_gestures       = models.BooleanField(default=True)
    head_movement       = models.BooleanField(default=True)
    facial_expressions  = models.BooleanField(default=True)
    status              = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result_video        = models.FileField(upload_to=result_upload_path, null=True, blank=True)
    error_message       = models.TextField(null=True, blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.status} - {self.created_at}"

    class Meta:
        ordering = ['-created_at']
        

User = get_user_model()


class LipsyncJob(models.Model):
    """
    Tracks one lip-sync video generation job from request to completion.
    In the synchronous architecture, status transitions happen in the
    same HTTP request:
        pending → processing → completed  (or failed)
    """

    STATUS_PENDING    = "pending"
    STATUS_PROCESSING = "processing"
    STATUS_COMPLETED  = "completed"
    STATUS_FAILED     = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING,    "Pending"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_COMPLETED,  "Completed"),
        (STATUS_FAILED,     "Failed"),
    ]

    # ── Identity ──────────────────────────────────────────────────────────────
    job_id = models.UUIDField(
        default    = uuid.uuid4,
        unique     = True,
        db_index   = True,
        editable   = False,
    )
    user = models.ForeignKey(
        User,
        on_delete    = models.CASCADE,
        related_name = "lipsync_jobs",
    )

    # ── Inputs ────────────────────────────────────────────────────────────────
    avatar_id = models.CharField(max_length=255, db_index=True)
    audio_id  = models.CharField(max_length=255)

    # ── Status ────────────────────────────────────────────────────────────────
    status        = models.CharField(
        max_length = 20,
        choices    = STATUS_CHOICES,
        default    = STATUS_PENDING,
        db_index   = True,
    )
    error_message = models.TextField(blank=True, null=True)

    # ── Output ────────────────────────────────────────────────────────────────
    video_path   = models.CharField(max_length=512, blank=True)
    video_url    = models.URLField(max_length=512,  blank=True)
    num_frames   = models.IntegerField(default=0)
    duration_sec = models.FloatField(default=0.0)
    elapsed_sec  = models.FloatField(default=0.0)

    # ── Metadata ──────────────────────────────────────────────────────────────
    stage_timings = models.JSONField(default=dict,  blank=True)
    warnings      = models.JSONField(default=list,  blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes  = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["avatar_id"]),
        ]

    def __str__(self) -> str:
        return (
            f"LipsyncJob {self.job_id} [{self.status}] "
            f"— user={self.user_id}  avatar={self.avatar_id}"
        )

    # ── Status transition helpers ─────────────────────────────────────────────

    def mark_processing(self) -> None:
        self.status = self.STATUS_PROCESSING
        self.save(update_fields=["status", "updated_at"])

    def mark_completed(
        self,
        video_path:    str,
        video_url:     str,
        num_frames:    int,
        duration_sec:  float,
        elapsed_sec:   float,
        stage_timings: dict,
        warnings:      list,
    ) -> None:
        self.status        = self.STATUS_COMPLETED
        self.video_path    = video_path
        self.video_url     = video_url
        self.num_frames    = num_frames
        self.duration_sec  = duration_sec
        self.elapsed_sec   = elapsed_sec
        self.stage_timings = stage_timings
        self.warnings      = warnings
        self.save()

    def mark_failed(self, error_message: str) -> None:
        self.status        = self.STATUS_FAILED
        self.error_message = error_message
        self.save(update_fields=["status", "error_message", "updated_at"])
