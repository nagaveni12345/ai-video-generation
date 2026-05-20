"""
scripts/test_avatar_processing.py
Standalone test script for the avatar preprocessing pipeline.

Run from the VIDEO-GENERATION project root:

    python scripts/test_avatar_processing.py --file /path/to/image_or_video

Requirements:
  - Python environment with opencv-python, mediapipe, numpy installed.
  - ml_pipeline package importable (project root in PYTHONPATH).

Usage examples:
    python scripts/test_avatar_processing.py --file tests/assets/sample_face.jpg
    python scripts/test_avatar_processing.py --file tests/assets/sample_avatar.mp4
    python scripts/test_avatar_processing.py --file tests/assets/sample_face.jpg --job-id my-test-001
    python scripts/test_avatar_processing.py --create-dummy-image   # generates a test face image
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import uuid
from pathlib import Path

# ── Add project root to sys.path so ml_pipeline is importable ─────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _create_dummy_image(output_path: Path) -> Path:
    """
    Generate a synthetic BGR image with a simple face-like pattern.
    Useful when no real test assets are available.
    """
    import cv2
    import numpy as np

    img = np.ones((480, 480, 3), dtype=np.uint8) * 220   # light grey background

    # Head
    cv2.ellipse(img, (240, 230), (140, 170), 0, 0, 360, (210, 180, 140), -1)

    # Eyes
    cv2.circle(img, (185, 200), 25, (255, 255, 255), -1)  # left eye white
    cv2.circle(img, (295, 200), 25, (255, 255, 255), -1)  # right eye white
    cv2.circle(img, (185, 200), 12, (50, 80, 200), -1)    # left iris
    cv2.circle(img, (295, 200), 12, (50, 80, 200), -1)    # right iris
    cv2.circle(img, (185, 200), 5,  (0, 0, 0), -1)        # left pupil
    cv2.circle(img, (295, 200), 5,  (0, 0, 0), -1)        # right pupil

    # Nose
    pts = np.array([[240, 230], [220, 290], [260, 290]], np.int32)
    cv2.polylines(img, [pts], True, (160, 120, 90), 2)

    # Mouth
    cv2.ellipse(img, (240, 340), (55, 25), 0, 0, 180, (160, 60, 60), -1)
    cv2.ellipse(img, (240, 340), (55, 25), 0, 0, 180, (80, 30, 30), 2)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), img)
    print(f"[setup] Dummy test image saved → {output_path}")
    return output_path


def run_test(file_path: Path, job_id: str, verbose: bool = True) -> bool:
    """
    Execute the full avatar pipeline and report results.

    Returns True if processing succeeded.
    """
    print("\n" + "=" * 60)
    print(f"  Avatar Preprocessing Test")
    print(f"  File   : {file_path}")
    print(f"  Job ID : {job_id}")
    print("=" * 60)

    # ── Import pipeline ────────────────────────────────────────────────────────
    try:
        from ml_pipeline.pipelines.avatar_pipeline import run_avatar_pipeline
    except ImportError as exc:
        print(f"\n[FAIL] Could not import ml_pipeline: {exc}")
        print("       Make sure the project root is in PYTHONPATH.")
        return False

    # ── Run ────────────────────────────────────────────────────────────────────
    t0     = time.time()
    result = run_avatar_pipeline(file_path=file_path, job_id=job_id)
    elapsed = time.time() - t0

    # ── Report ─────────────────────────────────────────────────────────────────
    status_icon = "✅" if result.is_success() else "❌"
    print(f"\n{status_icon}  Status     : {result.status.upper()}")
    print(f"   Media type : {result.media_type}")
    print(f"   Duration   : {elapsed:.2f}s")

    if result.errors:
        print("\n[ERRORS]")
        for err in result.errors:
            print(f"  • {err}")

    if result.warnings:
        print("\n[WARNINGS]")
        for w in result.warnings:
            print(f"  ⚠ {w}")

    if verbose and result.outputs:
        print("\n[OUTPUTS]")
        print(json.dumps(result.outputs, indent=2, default=str))

    if verbose and result.metadata:
        print("\n[METADATA]")
        print(json.dumps(result.metadata, indent=2, default=str))

    print("\n" + "=" * 60)
    return result.is_success()


def _smoke_test_imports() -> bool:
    """Verify all critical modules can be imported."""
    modules = [
        "cv2",
        "mediapipe",
        "numpy",
        "ml_pipeline.config.app_config",
        "ml_pipeline.config.model_config",
        "ml_pipeline.utils.logger",
        "ml_pipeline.utils.file_manager",
        "ml_pipeline.utils.response_builder",
        "ml_pipeline.preprocessing.media_validator",
        "ml_pipeline.preprocessing.face_detection",
        "ml_pipeline.preprocessing.face_alignment",
        "ml_pipeline.preprocessing.mouth_cropper",
        "ml_pipeline.preprocessing.frame_extractor",
        "ml_pipeline.preprocessing.image_preprocess",
        "ml_pipeline.preprocessing.video_preprocess",
        "ml_pipeline.pipelines.avatar_pipeline",
    ]

    all_ok = True
    print("\n[Import Smoke Test]")
    for mod in modules:
        try:
            __import__(mod)
            print(f"  ✅ {mod}")
        except Exception as exc:
            print(f"  ❌ {mod}  →  {exc}")
            all_ok = False

    return all_ok


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Test the avatar preprocessing pipeline end-to-end."
    )
    parser.add_argument("--file", type=str, help="Path to image or video file to process.")
    parser.add_argument("--job-id", type=str, default=None, help="Custom job ID (optional).")
    parser.add_argument("--create-dummy-image", action="store_true",
                        help="Generate a synthetic test face image and run pipeline on it.")
    parser.add_argument("--smoke", action="store_true",
                        help="Run import smoke tests only (no file required).")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output JSON.")
    args = parser.parse_args()

    if args.smoke:
        ok = _smoke_test_imports()
        sys.exit(0 if ok else 1)

    if args.create_dummy_image:
        dummy = PROJECT_ROOT / "tests" / "assets" / "dummy_face.jpg"
        file_path = _create_dummy_image(dummy)
    elif args.file:
        file_path = Path(args.file).resolve()
        if not file_path.exists():
            print(f"[ERROR] File not found: {file_path}")
            sys.exit(1)
    else:
        parser.print_help()
        print("\n[ERROR] Provide --file <path> or --create-dummy-image.")
        sys.exit(1)

    job_id  = args.job_id or str(uuid.uuid4())
    success = run_test(file_path, job_id, verbose=not args.quiet)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()