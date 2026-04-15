"""Shared helpers for EVF-SAM experimental scripts.

Encapsulates the vendored /tmp/EVF-SAM path shim, SAM/BEiT-3 preprocessing,
model loading, and alpha-mask → red-background preview compositing. Used by
evfsam_showcase.py, evfsam_tile_longscroll.py.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
from torchvision.transforms.functional import InterpolationMode


_EVFSAM_PATH = os.environ.get("EVFSAM_PATH", "/tmp/EVF-SAM")


def ensure_evfsam_on_path() -> None:
    """Put vendored EVF-SAM on sys.path once. Idempotent."""
    if _EVFSAM_PATH not in sys.path:
        sys.path.insert(0, _EVFSAM_PATH)


_SAM_MEAN = torch.tensor([123.675, 116.28, 103.53]).view(-1, 1, 1)
_SAM_STD = torch.tensor([58.395, 57.12, 57.375]).view(-1, 1, 1)


def sam_preprocess(img_np: np.ndarray, img_size: int = 1024):
    """Normalize + resize + pad-to-square for SAM image encoder."""
    ensure_evfsam_on_path()
    from model.segment_anything.utils.transforms import ResizeLongestSide
    x = ResizeLongestSide(img_size).apply_image(img_np)
    h, w = resize_shape = x.shape[:2]
    x = torch.from_numpy(x).permute(2, 0, 1).contiguous()
    x = (x - _SAM_MEAN) / _SAM_STD
    x = F.pad(x, (0, img_size - w, 0, img_size - h))
    return x, resize_shape


def beit3_preprocess(img_np: np.ndarray, img_size: int = 224) -> torch.Tensor:
    """Normalize + resize for BEiT-3 text-vision encoder."""
    tf = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((img_size, img_size), interpolation=InterpolationMode.BICUBIC, antialias=True),
        transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)),
    ])
    return tf(img_np)


def load_evfsam(device: str, model_id: str = "YxZhang/evf-sam"):
    """Load EVF-SAM tokenizer and model onto the given device. Returns (tokenizer, model)."""
    ensure_evfsam_on_path()
    from transformers import AutoTokenizer
    from model.evf_sam import EvfSamModel

    print(f"Loading {model_id} on {device}...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side="right", use_fast=False)
    model = EvfSamModel.from_pretrained(model_id, low_cpu_mem_usage=True, torch_dtype=torch.float32)
    model = model.to(device).eval()
    print(f"Model loaded in {time.time()-t0:.1f}s")
    return tokenizer, model


def imread_rgb(path: Path) -> np.ndarray:
    """Read BGR image, convert to RGB. Raises if file is missing or unreadable."""
    arr = cv2.imread(str(path))
    if arr is None:
        raise FileNotFoundError(f"Cannot read image: {path}")
    return cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)


def compose_red_bg(rgba_arr: np.ndarray) -> np.ndarray:
    """Replace transparent pixels with solid red, keep opaque ones. Input RGBA uint8."""
    mb = rgba_arr[:, :, 3] > 10
    red = np.full_like(rgba_arr, [255, 0, 0, 255])
    return np.where(mb[..., None], rgba_arr, red)


def save_layer_with_preview(
    mask_binary: np.ndarray,
    r_ch, g_ch, b_ch,
    out_dir: Path,
    name: str,
) -> Image.Image:
    """Save layer PNG (RGBA with mask as alpha) + red-bg preview.

    Args:
        mask_binary: uint8 array with values 0 or 255.
        r_ch, g_ch, b_ch: PIL L-mode channels from the source image.
        out_dir: output directory.
        name: layer name (used for filenames).

    Returns the RGBA layer Image (so caller can reuse it).
    """
    mask_pil = Image.fromarray(mask_binary, mode="L")
    layer = Image.merge("RGBA", (r_ch, g_ch, b_ch, mask_pil))
    layer.save(str(out_dir / f"{name}.png"))

    arr = np.array(layer)
    Image.fromarray(compose_red_bg(arr)).save(str(out_dir / f"{name}_on_red.png"))
    return layer
