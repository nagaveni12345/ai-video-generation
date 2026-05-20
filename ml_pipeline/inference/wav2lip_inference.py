from __future__ import annotations

import time
from pathlib import Path
from typing import List

import cv2
import numpy as np
import torch

from ml_pipeline.inference.wav2lip_model_loader import get_wav2lip_model
from ml_pipeline.utils.logger import get_logger

logger = get_logger("wav2lip_inference")

_IMG_SIZE = 96
_BATCH_SIZE = 16


def run_lipsync_inference(
    mouth_frame_paths: List[str],
    mel_chunks: List[np.ndarray],
    output_dir: str | Path,
    job_id: str,
    checkpoint_path: str | Path,
) -> dict:

    start = time.time()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "[job=%s] wav2lip_inference START | mouth_frames=%d mel_chunks=%d",
        job_id, len(mouth_frame_paths), len(mel_chunks)
    )

    if not mouth_frame_paths:
        return _fail("No mouth frames provided.")

    if not mel_chunks:
        return _fail("No mel chunks provided.")

    try:
        model, device = get_wav2lip_model(checkpoint_path)
    except Exception as exc:
        logger.exception("[job=%s] Wav2Lip model loading failed.", job_id)
        return _fail(f"Model load error: {exc}")

    mouth_paths = _tile_to_length(mouth_frame_paths, len(mel_chunks))
    face_pairs = _load_face_pairs(mouth_paths, job_id)
    mel_tensors = _prepare_mel_tensor(mel_chunks)

    n = min(len(face_pairs), mel_tensors.shape[0])
    face_pairs = face_pairs[:n]
    mel_tensors = mel_tensors[:n]

    generated_frames = []

    logger.info("[job=%s] Inference frames=%d device=%s", job_id, n, device)

    for batch_start in range(0, n, _BATCH_SIZE):
        batch_end = min(batch_start + _BATCH_SIZE, n)

        try:
            batch_face = face_pairs[batch_start:batch_end]
            batch_mel = mel_tensors[batch_start:batch_end]

            img_batch = np.stack([x[1] for x in batch_face], axis=0)
            ref_batch = np.stack([x[0] for x in batch_face], axis=0)

            img_batch = torch.from_numpy(img_batch).permute(0, 3, 1, 2).float() / 255.0
            ref_batch = torch.from_numpy(ref_batch).permute(0, 3, 1, 2).float() / 255.0

            face_input = torch.cat([img_batch, ref_batch], dim=1).contiguous().to(device)
            mel_input = batch_mel.unsqueeze(1).contiguous().to(device)

            with torch.no_grad():
                if device.type == "cuda":
                    with torch.cuda.amp.autocast():
                        pred = model(mel_input, face_input)
                else:
                    pred = model(mel_input, face_input)

            pred = pred.detach().float().cpu()

            if torch.isnan(pred).any():
                logger.warning("[job=%s] NaN predictions in batch %d-%d", job_id, batch_start, batch_end)
                continue

            pred_np = pred.numpy().transpose(0, 2, 3, 1)
            pred_np = np.clip(pred_np * 255.0, 0, 255).astype(np.uint8)

            for i, frame_np in enumerate(pred_np):
                idx = batch_start + i
                bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
                out_path = output_dir / f"lipsync_{idx:06d}.jpg"
                cv2.imwrite(str(out_path), bgr, [cv2.IMWRITE_JPEG_QUALITY, 95])
                generated_frames.append(str(out_path))

        except Exception as batch_exc:
            logger.exception("[job=%s] Batch inference failed %d-%d", job_id, batch_start, batch_end)
            return _fail(f"Inference batch failure: {batch_exc}")

    elapsed = round(time.time() - start, 3)

    logger.info(
        "[job=%s] wav2lip_inference DONE | generated=%d elapsed=%.2fs",
        job_id, len(generated_frames), elapsed
    )

    return {
        "success": True,
        "generated_frames": generated_frames,
        "num_frames": len(generated_frames),
        "elapsed_sec": elapsed,
        "error": None,
    }


def _tile_to_length(paths: List[str], target_len: int) -> List[str]:
    result = []
    while len(result) < target_len:
        result.extend(paths)
    return result[:target_len]


def _load_face_pairs(mouth_paths: List[str], job_id: str):
    pairs = []

    for p in mouth_paths:
        img = cv2.imread(str(p))
        if img is None:
            logger.warning("[job=%s] Could not read %s", job_id, p)
            continue

        img = cv2.resize(img, (_IMG_SIZE, _IMG_SIZE))
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        masked = rgb.copy()
        masked[_IMG_SIZE // 2:, :, :] = 0

        pairs.append((rgb, masked))

    return pairs


def _prepare_mel_tensor(mel_chunks: List[np.ndarray]) -> torch.Tensor:
    fixed = []

    for chunk in mel_chunks:
        chunk = np.asarray(chunk, dtype=np.float32)

        if chunk.shape[1] < 16:
            pad = np.zeros((80, 16 - chunk.shape[1]), dtype=np.float32)
            chunk = np.concatenate([chunk, pad], axis=1)
        elif chunk.shape[1] > 16:
            chunk = chunk[:, :16]

        fixed.append(chunk)

    return torch.from_numpy(np.stack(fixed, axis=0)).float()


def _fail(msg: str) -> dict:
    return {
        "success": False,
        "generated_frames": [],
        "num_frames": 0,
        "elapsed_sec": 0.0,
        "error": msg,
    }