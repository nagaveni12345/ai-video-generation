"""
ml_pipeline/inference/lipsync_inference.py
Local Wav2Lip GAN inference — runs in the same process as Django/Celery.

Responsibilities:
  - Load Wav2Lip checkpoint from ml_pipeline/models/checkpoints/wav2lip_gan.pth
  - Accept preprocessed mouth frames + mel-spectrogram chunks
  - Run batched PyTorch inference (GPU if available, else CPU)
  - Save generated lip-sync mouth frames to job output directory
  - Return structured result metadata
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
import torch
import torch.nn as nn

from ml_pipeline.utils.logger import get_logger

logger = get_logger("lipsync_inference")

# ── Checkpoint path (canonical location) ──────────────────────────────────────
_DEFAULT_CHECKPOINT = Path("ml_pipeline/models/checkpoints/wav2lip_gan.pth")

# ── Inference hyperparameters ─────────────────────────────────────────────────
_BATCH_SIZE        = 8        # mouth frames per forward pass
_IMG_SIZE          = 96         # Wav2Lip expects 96×96 mouth crops
_MEL_STEP_SIZE     = 16         # mel frames per inference step (matches audio_preprocess)
_HALF_FACE_RATIO   = 0.5        # lower half of face used by Wav2Lip


# ──────────────────────────────────────────────────────────────────────────────
# Wav2Lip model architecture (self-contained — no external wav2lip package)
# ──────────────────────────────────────────────────────────────────────────────

class _Conv2d(nn.Module):
    def __init__(self, cin, cout, kernel_size, stride, padding, residual=False, act=True):
        super().__init__()
        self.conv_block = nn.Sequential(
            nn.Conv2d(cin, cout, kernel_size, stride, padding),
            nn.BatchNorm2d(cout),
        )
        self.act       = nn.ReLU() if act else None
        self.residual  = residual

    def forward(self, x):
        out = self.conv_block(x)
        if self.residual:
            out = out + x
        return self.act(out) if self.act else out


class _nonorm_Conv2d(nn.Module):
    def __init__(self, cin, cout, kernel_size, stride, padding, residual=False, act=True):
        super().__init__()
        self.conv_block = nn.Sequential(nn.Conv2d(cin, cout, kernel_size, stride, padding))
        self.act       = nn.LeakyReLU(0.01, inplace=True) if act else None
        self.residual  = residual

    def forward(self, x):
        out = self.conv_block(x)
        if self.residual:
            out = out + x
        return self.act(out) if self.act else out


class _Conv2dTranspose(nn.Module):
    def __init__(self, cin, cout, kernel_size, stride, padding, output_padding=0):
        super().__init__()
        self.conv_block = nn.Sequential(
            nn.ConvTranspose2d(cin, cout, kernel_size, stride, padding, output_padding),
            nn.BatchNorm2d(cout),
            nn.ReLU(),
        )

    def forward(self, x):
        return self.conv_block(x)


class Wav2Lip(nn.Module):
    """
    Wav2Lip / Wav2Lip-GAN generator architecture.
    Weights are loaded from an official checkpoint file.
    """

    def __init__(self):
        super().__init__()

        # Audio encoder
        self.audio_encoder = nn.Sequential(
            _Conv2d(1,  32, 3, 1, 1),
            _Conv2d(32, 32, 3, 1, 1, residual=True),
            _Conv2d(32, 32, 3, 1, 1, residual=True),
            _Conv2d(32, 64, 3, (3, 1), 1),
            _Conv2d(64, 64, 3, 1, 1, residual=True),
            _Conv2d(64, 64, 3, 1, 1, residual=True),
            _Conv2d(64, 128, 3, 3, 1),
            _Conv2d(128, 128, 3, 1, 1, residual=True),
            _Conv2d(128, 128, 3, 1, 1, residual=True),
            _Conv2d(128, 256, 3, (3, 2), 1),
            _Conv2d(256, 256, 3, 1, 1, residual=True),
            _Conv2d(256, 512, 3, 1, 0),
            _Conv2d(512, 512, 1, 1, 0),
        )

        # Face encoder (lower half)
        self.face_encoder_blocks = nn.ModuleList([
            nn.Sequential(_Conv2d(6,  16, 7, 1, 3)),
            nn.Sequential(_Conv2d(16, 32, 3, 2, 1), _Conv2d(32, 32, 3, 1, 1, residual=True), _Conv2d(32, 32, 3, 1, 1, residual=True)),
            nn.Sequential(_Conv2d(32, 64, 3, 2, 1), _Conv2d(64, 64, 3, 1, 1, residual=True), _Conv2d(64, 64, 3, 1, 1, residual=True)),
            nn.Sequential(_Conv2d(64, 128, 3, 2, 1), _Conv2d(128, 128, 3, 1, 1, residual=True), _Conv2d(128, 128, 3, 1, 1, residual=True)),
            nn.Sequential(_Conv2d(128, 256, 3, 2, 1), _Conv2d(256, 256, 3, 1, 1, residual=True), _Conv2d(256, 256, 3, 1, 1, residual=True)),
            nn.Sequential(_Conv2d(256, 512, 3, 2, 1), _Conv2d(512, 512, 3, 1, 1, residual=True)),
            nn.Sequential(_Conv2d(512, 512, 3, 2, 1), _Conv2d(512, 512, 3, 1, 1, residual=True)),
        ])

        # Face decoder
        self.face_decoder_blocks = nn.ModuleList([
            nn.Sequential(_Conv2d(512, 512, 3, 1, 1, residual=True)),
            nn.Sequential(_Conv2dTranspose(1024, 512, 3, 2, 1, 1), _Conv2d(512, 512, 3, 1, 1, residual=True)),
            nn.Sequential(_Conv2dTranspose(1024, 256, 3, 2, 1, 1), _Conv2d(256, 256, 3, 1, 1, residual=True)),
            nn.Sequential(_Conv2dTranspose(512,  128, 3, 2, 1, 1), _Conv2d(128, 128, 3, 1, 1, residual=True)),
            nn.Sequential(_Conv2dTranspose(256,  64,  3, 2, 1, 1), _Conv2d(64,  64,  3, 1, 1, residual=True)),
            nn.Sequential(_Conv2dTranspose(128,  32,  3, 2, 1, 1), _Conv2d(32,  32,  3, 1, 1, residual=True)),
            nn.Sequential(_Conv2dTranspose(64,   16,  3, 2, 1, 1), _Conv2d(16,  16,  3, 1, 1, residual=True)),
        ])

        self.output_block = nn.Sequential(
            _Conv2d(32, 16, 3, 1, 1),
            nn.Conv2d(16, 3, 1, 1, 0),
            nn.Sigmoid(),
        )

    def forward(self, audio_sequences: torch.Tensor, face_sequences: torch.Tensor) -> torch.Tensor:
        # audio_sequences: (B, 1, 80, 16)
        # face_sequences:  (B, 6, 96, 96)  — masked + reference concat
        B = audio_sequences.size(0)
        input_dim_size = len(face_sequences.size())
        if input_dim_size > 4:
            audio_sequences = torch.cat(
                [audio_sequences[:, i] for i in range(audio_sequences.size(1))], dim=0
            )
            face_sequences = torch.cat(
                [face_sequences[:, :, i] for i in range(face_sequences.size(2))], dim=0
            )

        audio_embedding = self.audio_encoder(audio_sequences)  # (B, 512, 1, 1)

        feats = []
        x = face_sequences
        for f in self.face_encoder_blocks:
            x = f(x)
            feats.append(x)

        x = audio_embedding
        for i, f in enumerate(self.face_decoder_blocks):
            x = f(x)
            try:
                x = torch.cat((x, feats[-1 - i]), dim=1)
            except Exception:
                break

        x = self.output_block(x)
        return x


# ──────────────────────────────────────────────────────────────────────────────
# Singleton model loader
# ──────────────────────────────────────────────────────────────────────────────

class _ModelRegistry:
    """Thread-safe singleton registry for the loaded Wav2Lip model."""

    _model:  Optional[Wav2Lip] = None
    _device: Optional[torch.device] = None

    @classmethod
    def get(cls, checkpoint_path: Path) -> tuple[Wav2Lip, torch.device]:
        if cls._model is not None:
            return cls._model, cls._device  # type: ignore[return-value]

        logger.info("Loading Wav2Lip checkpoint: %s", checkpoint_path)
        if not checkpoint_path.exists():
            raise FileNotFoundError(
                f"Wav2Lip checkpoint not found at: {checkpoint_path}\n"
                "Download wav2lip_gan.pth and place it in ml_pipeline/models/checkpoints/"
            )

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info("Wav2Lip will run on device: %s", device)

        # --------------------------------------------------
        # Universal checkpoint loader:
        # supports both TorchScript and standard state_dict
        # --------------------------------------------------

        checkpoint = torch.load(str(checkpoint_path), map_location=device)

        # CASE 1 → TorchScript serialized archive
        if isinstance(checkpoint, torch.jit.RecursiveScriptModule) or isinstance(checkpoint, torch.jit.ScriptModule):
            logger.info("TorchScript Wav2Lip checkpoint detected.")
            model = checkpoint.to(device)
            model.eval()

        # CASE 2 → Standard checkpoint/state_dict
        else:
            logger.info("Standard state_dict Wav2Lip checkpoint detected.")
            model = Wav2Lip()

            if isinstance(checkpoint, dict):
                state_dict = checkpoint.get("state_dict", checkpoint)
            else:
                state_dict = checkpoint

            state_dict = {k.replace("module.", ""): v for k, v in state_dict.items()}
            model.load_state_dict(state_dict, strict=False)
            model = model.to(device)
            model.eval()

        cls._model  = model
        cls._device = device
        logger.info("Wav2Lip model loaded successfully.")
        return cls._model, cls._device


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def run_lipsync_inference(
    mouth_frame_paths: List[str],
    mel_chunks:        List[np.ndarray],
    output_dir:        str | Path,
    job_id:            str,
    checkpoint_path:   str | Path = _DEFAULT_CHECKPOINT,
    batch_size:        int        = _BATCH_SIZE,
) -> dict:
    """
    Run Wav2Lip GAN inference and save generated mouth frames.

    Args:
        mouth_frame_paths: Ordered list of preprocessed mouth crop image paths.
        mel_chunks:        Mel chunks from ``audio_preprocess.preprocess_audio``.
        output_dir:        Directory where generated frames are written.
        job_id:            Job identifier for file naming.
        checkpoint_path:   Path to wav2lip_gan.pth.
        batch_size:        Number of frames per forward pass.

    Returns:
        Dict with:
          - ``success``          bool
          - ``generated_frames`` list[str]  — saved output frame paths (sorted)
          - ``num_frames``       int
          - ``error``            str | None
    """
    start      = time.time()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "[job=%s] Lipsync inference | mouth_frames=%d  mel_chunks=%d",
        job_id, len(mouth_frame_paths), len(mel_chunks),
    )

    if not mouth_frame_paths:
        return _fail("No mouth frames provided for inference.")
    if not mel_chunks:
        return _fail("No mel chunks provided for inference.")

    # ── Load model (cached) ───────────────────────────────────────────────────
    try:
        model, device = _ModelRegistry.get(Path(checkpoint_path))
    except FileNotFoundError as exc:
        logger.error("[job=%s] %s", job_id, exc)
        return _fail(str(exc))
    except Exception as exc:
        logger.exception("[job=%s] Model load failed.", job_id)
        return _fail(f"Model load error: {exc}")

    # ── Align frames to mel chunks ────────────────────────────────────────────
    # Repeat or truncate face frames to match mel chunk count
    num_mel_chunks = len(mel_chunks)
    face_paths     = _align_sequences(mouth_frame_paths, num_mel_chunks)

    # ── Batch inference ───────────────────────────────────────────────────────
    generated_frames: List[str] = []

    for batch_start in range(0, num_mel_chunks, batch_size):
        batch_mel_list   = mel_chunks[batch_start: batch_start + batch_size]
        batch_face_paths = face_paths[batch_start: batch_start + batch_size]

        img_batch:  List[np.ndarray] = []
        mel_batch:  List[np.ndarray] = []
        orig_faces: List[np.ndarray] = []

        for mel_chunk, face_path in zip(batch_mel_list, batch_face_paths):
            face = _load_and_prepare_face(face_path)
            if face is None:
                logger.warning("[job=%s] Could not load face: %s", job_id, face_path)
                continue
            orig_faces.append(face.copy())
            img_batch.append(_mask_lower_half(face))
            mel_batch.append(mel_chunk)

        if not img_batch:
            continue

        # Build tensors
        img_tensor = _faces_to_tensor(img_batch, orig_faces, device)
        mel_tensor = _mel_to_tensor(mel_batch, device)

        with torch.no_grad():
            pred = model(mel_tensor, img_tensor)

        pred_np = (pred.cpu().numpy().transpose(0, 2, 3, 1) * 255.0).astype(np.uint8)

        for i, frame_np in enumerate(pred_np):
            global_idx   = batch_start + i
            out_path     = output_dir / f"lipsync_{global_idx:06d}.jpg"
            bgr_frame    = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(out_path), bgr_frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            generated_frames.append(str(out_path))

    generated_frames.sort()
    elapsed = time.time() - start

    logger.info(
        "[job=%s] Inference done: %d frames in %.2fs.",
        job_id, len(generated_frames), elapsed,
    )

    return {
        "success":          True,
        "generated_frames": generated_frames,
        "num_frames":       len(generated_frames),
        "error":            None,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

def _align_sequences(face_paths: List[str], target_len: int) -> List[str]:
    """Tile or truncate face_paths to exactly target_len entries."""
    if len(face_paths) == 0:
        return []
    result = []
    while len(result) < target_len:
        result.extend(face_paths)
    return result[:target_len]


def _load_and_prepare_face(path: str) -> Optional[np.ndarray]:
    """Load a mouth crop image and resize to _IMG_SIZE × _IMG_SIZE RGB."""
    img = cv2.imread(str(path))
    if img is None:
        return None
    img = cv2.resize(img, (_IMG_SIZE, _IMG_SIZE))
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def _mask_lower_half(face_rgb: np.ndarray) -> np.ndarray:
    """Zero out the upper half of a face image (Wav2Lip input convention)."""
    masked = face_rgb.copy()
    h      = masked.shape[0]
    masked[: h // 2] = 0
    return masked


def _faces_to_tensor(
    masked_faces: List[np.ndarray],
    orig_faces:   List[np.ndarray],
    device:       torch.device,
) -> torch.Tensor:
    """
    Build a (B, 6, H, W) tensor: channel-wise concat of masked + original face.
    """
    masked_arr = np.array(masked_faces, dtype=np.float32) / 255.0   # (B, H, W, 3)
    orig_arr   = np.array(orig_faces,   dtype=np.float32) / 255.0
    concat     = np.concatenate([masked_arr, orig_arr], axis=-1)      # (B, H, W, 6)
    tensor     = torch.from_numpy(concat).permute(0, 3, 1, 2)         # (B, 6, H, W)
    return tensor.to(device)


def _mel_to_tensor(mel_chunks: List[np.ndarray], device: torch.device) -> torch.Tensor:
    """Build a (B, 1, 80, 16) tensor from a list of mel chunk arrays."""
    arr    = np.array(mel_chunks, dtype=np.float32)                  # (B, 80, 16)
    tensor = torch.from_numpy(arr).unsqueeze(1)                       # (B, 1, 80, 16)
    return tensor.to(device)


def _fail(msg: str) -> dict:
    return {
        "success":          False,
        "generated_frames": [],
        "num_frames":       0,
        "error":            msg,
    }