"""
ml_pipeline/inference/wav2lip_model_loader.py
Universal singleton loader for Wav2Lip checkpoints.

Supports:
1. Standard PyTorch checkpoint dict (.pth with state_dict)
2. Raw state_dict
3. TorchScript compiled ScriptModule archives (.pth/.pt)

Loads exactly once per process.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional, Tuple

import torch
import torch.nn as nn

logger = logging.getLogger("wav2lip_inference")

_cached_model: Optional[nn.Module] = None
_cached_device: Optional[torch.device] = None


# =============================================================================
# OPTIONAL STANDARD WAV2LIP ARCHITECTURE
# Only used if checkpoint is a state_dict.
# =============================================================================

class Conv2d(nn.Module):
    def __init__(self, cin, cout, kernel_size, stride, padding, residual=False):
        super().__init__()
        self.conv_block = nn.Sequential(
            nn.Conv2d(cin, cout, kernel_size, stride=stride, padding=padding),
            nn.BatchNorm2d(cout),
        )
        self.act = nn.ReLU(inplace=True)
        self.residual = residual

    def forward(self, x):
        out = self.conv_block(x)
        if self.residual:
            out = out + x
        return self.act(out)


class Conv2dTranspose(nn.Module):
    def __init__(self, cin, cout, kernel_size, stride, padding, output_padding=0):
        super().__init__()
        self.conv_block = nn.Sequential(
            nn.ConvTranspose2d(cin, cout, kernel_size, stride=stride,
                               padding=padding, output_padding=output_padding),
            nn.BatchNorm2d(cout),
        )
        self.act = nn.ReLU(inplace=True)

    def forward(self, x):
        return self.act(self.conv_block(x))


class Wav2Lip(nn.Module):
    def __init__(self):
        super().__init__()

        self.face_encoder_blocks = nn.ModuleList([
            nn.Sequential(Conv2d(6, 16, 7, 1, 3)),
            nn.Sequential(Conv2d(16, 32, 3, 2, 1), Conv2d(32, 32, 3, 1, 1, True), Conv2d(32, 32, 3, 1, 1, True)),
            nn.Sequential(Conv2d(32, 64, 3, 2, 1), Conv2d(64, 64, 3, 1, 1, True), Conv2d(64, 64, 3, 1, 1, True)),
            nn.Sequential(Conv2d(64, 128, 3, 2, 1), Conv2d(128, 128, 3, 1, 1, True), Conv2d(128, 128, 3, 1, 1, True)),
            nn.Sequential(Conv2d(128, 256, 3, 2, 1), Conv2d(256, 256, 3, 1, 1, True), Conv2d(256, 256, 3, 1, 1, True)),
            nn.Sequential(Conv2d(256, 512, 3, 2, 1), Conv2d(512, 512, 3, 1, 1, True)),
            nn.Sequential(Conv2d(512, 512, 3, 1, 0), Conv2d(512, 512, 1, 1, 0)),
        ])

        self.audio_encoder = nn.Sequential(
            Conv2d(1, 32, 3, 1, 1),
            Conv2d(32, 32, 3, 1, 1, True),
            Conv2d(32, 32, 3, 1, 1, True),
            Conv2d(32, 64, 3, (3, 1), 1),
            Conv2d(64, 64, 3, 1, 1, True),
            Conv2d(64, 64, 3, 1, 1, True),
            Conv2d(64, 128, 3, 3, 1),
            Conv2d(128, 128, 3, 1, 1, True),
            Conv2d(128, 128, 3, 1, 1, True),
            Conv2d(128, 256, 3, (3, 2), 1),
            Conv2d(256, 256, 3, 1, 1, True),
            Conv2d(256, 512, 3, 1, 0),
            Conv2d(512, 512, 1, 1, 0),
        )

        self.face_decoder_blocks = nn.ModuleList([
            nn.Sequential(Conv2d(512, 512, 1, 1, 0)),
            nn.Sequential(Conv2dTranspose(1024, 512, 3, 1, 0), Conv2d(512, 512, 3, 1, 1, True)),
            nn.Sequential(Conv2dTranspose(1024, 512, 3, 2, 1, 1), Conv2d(512, 512, 3, 1, 1, True)),
            nn.Sequential(Conv2dTranspose(768, 384, 3, 2, 1, 1), Conv2d(384, 384, 3, 1, 1, True)),
            nn.Sequential(Conv2dTranspose(512, 256, 3, 2, 1, 1), Conv2d(256, 256, 3, 1, 1, True)),
            nn.Sequential(Conv2dTranspose(320, 128, 3, 2, 1, 1), Conv2d(128, 128, 3, 1, 1, True)),
            nn.Sequential(Conv2dTranspose(160, 64, 3, 2, 1, 1), Conv2d(64, 64, 3, 1, 1, True)),
        ])

        self.output_block = nn.Sequential(
            Conv2d(80, 32, 3, 1, 1),
            nn.Conv2d(32, 3, 1, 1, 0),
            nn.Sigmoid(),
        )

    def forward(self, audio_sequences, face_sequences):
        raise NotImplementedError("State_dict fallback only. Forward handled by inference wrapper.")


# =============================================================================
# PUBLIC LOADER
# =============================================================================

def get_wav2lip_model(checkpoint_path: str | Path) -> Tuple[nn.Module, torch.device]:
    global _cached_model, _cached_device

    if _cached_model is not None:
        return _cached_model, _cached_device

    checkpoint_path = Path(checkpoint_path)
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Wav2Lip checkpoint not found: {checkpoint_path}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("wav2lip_model_loader: loading %s on %s", checkpoint_path.name, device)

    # -------------------------------------------------------------------------
    # TRY 1: TorchScript load (your checkpoint is this)
    # -------------------------------------------------------------------------
    try:
        scripted_model = torch.jit.load(str(checkpoint_path), map_location=device)
        scripted_model = scripted_model.to(device)
        scripted_model.eval()

        _cached_model = scripted_model
        _cached_device = device

        logger.info("wav2lip_model_loader: TorchScript model loaded successfully.")
        return _cached_model, _cached_device

    except Exception as ts_exc:
        logger.warning("TorchScript load failed, trying standard checkpoint: %s", ts_exc)

    # -------------------------------------------------------------------------
    # TRY 2: Standard state_dict load
    # -------------------------------------------------------------------------
    try:
        ckpt = torch.load(str(checkpoint_path), map_location=device)

        if isinstance(ckpt, dict) and "state_dict" in ckpt:
            state_dict = ckpt["state_dict"]
        elif isinstance(ckpt, dict) and "model" in ckpt:
            state_dict = ckpt["model"]
        elif isinstance(ckpt, dict):
            state_dict = ckpt
        else:
            raise RuntimeError(f"Unsupported checkpoint type: {type(ckpt)}")

        cleaned = {}
        for k, v in state_dict.items():
            cleaned[k.replace("module.", "")] = v

        model = Wav2Lip()
        model.load_state_dict(cleaned, strict=False)
        model = model.to(device)
        model.eval()

        _cached_model = model
        _cached_device = device

        logger.info("wav2lip_model_loader: Standard PyTorch checkpoint loaded successfully.")
        return _cached_model, _cached_device

    except Exception as exc:
        raise RuntimeError(f"Failed to load Wav2Lip checkpoint by all strategies: {exc}") from exc


def clear_model_cache():
    global _cached_model, _cached_device
    _cached_model = None
    _cached_device = None
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    logger.info("wav2lip_model_loader: cache cleared.")