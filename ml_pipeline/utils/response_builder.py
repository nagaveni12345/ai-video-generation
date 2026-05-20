"""
ml_pipeline/utils/response_builder.py
Standardised response / result object builders for the ML pipeline.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional


# ──────────────────────────────────────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class PipelineResult:
    """Top-level result returned by any pipeline run."""

    job_id:       str
    status:       str                    # "success" | "failure" | "partial"
    media_type:   str                    # "image"   | "video"
    input_path:   str                    = ""
    duration_sec: float                  = 0.0
    outputs:      dict[str, Any]         = field(default_factory=dict)
    metadata:     dict[str, Any]         = field(default_factory=dict)
    errors:       list[str]              = field(default_factory=list)
    warnings:     list[str]              = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return a plain-dict representation safe for JSON serialisation."""
        d = asdict(self)
        # Convert any Path objects that slipped through
        d["outputs"] = _paths_to_str(d["outputs"])
        return d

    def is_success(self) -> bool:
        return self.status == "success"


@dataclass
class ImageProcessingOutputs:
    """Structured output paths produced by the image preprocessing chain."""

    validated_path:    str = ""
    face_crop_path:    str = ""
    aligned_face_path: str = ""
    mouth_crop_path:   str = ""
    landmark_data:     dict[str, Any] = field(default_factory=dict)


@dataclass
class VideoProcessingOutputs:
    """Structured output paths produced by the video preprocessing chain."""

    validated_path:     str         = ""
    frames_dir:         str         = ""
    total_frames:       int         = 0
    sampled_frames:     list[str]   = field(default_factory=list)
    face_crops_dir:     str         = ""
    mouth_crops_dir:    str         = ""
    faces_detected:     int         = 0
    frames_with_faces:  int         = 0
    fps:                float       = 0.0
    duration_sec:       float       = 0.0
    resolution:         tuple[int, int] = (0, 0)


# ──────────────────────────────────────────────────────────────────────────────
# Builder functions
# ──────────────────────────────────────────────────────────────────────────────

def build_success(
    job_id:     str,
    media_type: str,
    input_path: str,
    outputs:    Any,
    metadata:   Optional[dict] = None,
    start_time: Optional[float] = None,
    warnings:   Optional[list[str]] = None,
) -> PipelineResult:
    """Construct a successful PipelineResult."""
    duration = round(time.time() - start_time, 3) if start_time else 0.0

    outputs_dict = asdict(outputs) if hasattr(outputs, "__dataclass_fields__") else (outputs or {})

    return PipelineResult(
        job_id       = job_id,
        status       = "success",
        media_type   = media_type,
        input_path   = input_path,
        duration_sec = duration,
        outputs      = _paths_to_str(outputs_dict),
        metadata     = metadata or {},
        warnings     = warnings or [],
    )


def build_failure(
    job_id:     str,
    media_type: str,
    input_path: str,
    error:      str,
    metadata:   Optional[dict] = None,
    start_time: Optional[float] = None,
) -> PipelineResult:
    """Construct a failure PipelineResult."""
    duration = round(time.time() - start_time, 3) if start_time else 0.0

    return PipelineResult(
        job_id       = job_id,
        status       = "failure",
        media_type   = media_type,
        input_path   = input_path,
        duration_sec = duration,
        outputs      = {},
        metadata     = metadata or {},
        errors       = [error],
    )


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _paths_to_str(obj: Any) -> Any:
    """Recursively convert Path objects to strings within dicts / lists."""
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {k: _paths_to_str(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        converted = [_paths_to_str(v) for v in obj]
        return type(obj)(converted)
    return obj