"""Paste an edited layer back into a foreign source image (open-loop edit).

This is the glue verb for the canonical Vulca workflow
"decompose source → edit one layer → composite back into source preserving
everything else". It is intentionally distinct from ``layers_composite``,
which flattens a manifest stack into a closed-loop Vulca artwork.

Pure PIL — no provider calls, deterministic, fast.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

BlendMode = Literal["alpha", "feathered", "hard"]


def paste_back(
    source_image: str,
    layer_image: str,
    *,
    mask_path: str = "",
    output_path: str = "",
    blend_mode: BlendMode = "alpha",
    feather_px: int = 2,
) -> dict:
    """Composite ``layer_image`` onto ``source_image`` using a mask.

    Args:
        source_image: Original RGB image (e.g. iter0.png).
        layer_image: Edited layer RGBA (e.g. gongbi_lanterns.png). Its alpha
            channel is used as the default mask.
        mask_path: Optional override mask. If empty, layer_image's alpha is
            used.
        output_path: Default ``<source_dir>/<source_stem>_with_<layer_stem>.png``.
        blend_mode: ``"alpha"`` (use mask as-is) | ``"feathered"`` (Gaussian
            blur of feather_px) | ``"hard"`` (binary threshold at 127).
        feather_px: Gaussian blur radius for feathered mode.

    Returns:
        ``{"output_path": str, "blend_mode": str}``.
    """
    from PIL import Image, ImageFilter

    src_p = Path(source_image)
    layer_p = Path(layer_image)
    if not src_p.exists():
        raise FileNotFoundError(f"source_image not found: {source_image}")
    if not layer_p.exists():
        raise FileNotFoundError(f"layer_image not found: {layer_image}")

    src = Image.open(str(src_p)).convert("RGB")
    layer = Image.open(str(layer_p)).convert("RGBA")

    if src.size != layer.size:
        raise ValueError(
            f"source size {src.size} != layer size {layer.size}; "
            "resize one of them before paste_back"
        )

    if mask_path:
        mask_p = Path(mask_path)
        if not mask_p.exists():
            raise FileNotFoundError(f"mask_path not found: {mask_path}")
        mask = Image.open(str(mask_p)).convert("L")
        if mask.size != src.size:
            raise ValueError(
                f"mask size {mask.size} != source size {src.size}"
            )
    else:
        mask = layer.split()[-1]

    if blend_mode == "alpha":
        applied_mask = mask
    elif blend_mode == "feathered":
        if feather_px < 0:
            raise ValueError(f"feather_px must be >= 0, got {feather_px}")
        applied_mask = mask.filter(ImageFilter.GaussianBlur(feather_px))
    elif blend_mode == "hard":
        applied_mask = mask.point(lambda x: 255 if x > 127 else 0)
    else:
        raise ValueError(
            f"unknown blend_mode={blend_mode!r}; "
            "expected one of alpha, feathered, hard"
        )

    result = Image.composite(layer.convert("RGB"), src, applied_mask)

    if not output_path:
        output_path = str(
            src_p.parent / f"{src_p.stem}_with_{layer_p.stem}.png"
        )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    result.save(output_path, "PNG")

    return {"output_path": output_path, "blend_mode": blend_mode}
