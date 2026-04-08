"""Two-pass VLM mask generation — shared by regenerate mode and LAYERED pipeline.

Pattern: generate content image → ask VLM to produce BW alpha mask → apply mask.
This is the proven approach from LayerGenerateNode, now extracted for reuse.
"""
from __future__ import annotations

import base64
import io
import logging

import numpy as np
from PIL import Image

logger = logging.getLogger("vulca")

VLM_MASK_PROMPT = (
    "Create a black and white alpha mask of this image.\n"
    "White (#FFFFFF) for all visible content and objects.\n"
    "Black (#000000) for empty background areas.\n"
    "Sharp precise edges. No gray gradients except at content boundaries."
)


async def generate_vlm_mask(
    content_b64: str,
    provider_name: str = "gemini",
    api_key: str = "",
    prompt: str = "",
) -> Image.Image | None:
    """Ask VLM to generate a BW alpha mask for the given content image.

    Args:
        content_b64: Base64-encoded content image (PNG bytes).
        provider_name: Image provider to use.
        api_key: API key (empty = env fallback).
        prompt: Custom prompt to override the default VLM_MASK_PROMPT.
            If empty, uses the default prompt.

    Returns:
        Grayscale PIL Image (mode "L") or None on failure.
    """
    from vulca.providers import get_image_provider

    try:
        provider = get_image_provider(provider_name, api_key=api_key)
        result = await provider.generate(
            prompt or VLM_MASK_PROMPT,
            reference_image_b64=content_b64,
            raw_prompt=True,
        )
        mask_b64 = result.image_b64 if hasattr(result, "image_b64") else result
        mask_img = Image.open(io.BytesIO(base64.b64decode(mask_b64)))
        mask_l = mask_img.convert("L")
        # Reject degenerate masks (all same value = no useful segmentation)
        mask_arr = np.array(mask_l)
        if mask_arr.std() < 10:
            logger.warning("VLM mask degenerate (std=%.1f), rejecting", mask_arr.std())
            return None
        return mask_l
    except Exception as exc:
        logger.warning("VLM mask generation failed: %s", exc)
        return None


def apply_vlm_mask(content: Image.Image, mask: Image.Image) -> Image.Image:
    """Apply a VLM-generated grayscale mask as alpha channel.

    Args:
        content: RGBA or RGB content image.
        mask: Grayscale mask (L mode) — white = opaque.

    Returns:
        RGBA image with mask applied as alpha.
    """
    rgba = content.convert("RGBA")
    # Resize mask to match content if needed
    if mask.size != rgba.size:
        mask = mask.resize(rgba.size, Image.LANCZOS)
    # B-path softening: feather + (optional) guided filter + despill so the
    # alpha channel has anti-aliased edges instead of binary 0/255 stair-steps.
    from vulca.layers.matting import soften_mask
    mask_arr = np.array(mask).astype(np.float32) / 255.0
    rgb_arr = np.array(rgba.convert("RGB"))
    soft = soften_mask(mask_arr, rgb_arr, feather_px=2, guided=True, despill=True)
    soft_img = Image.fromarray((soft * 255).astype(np.uint8), mode="L")
    r, g, b, _ = rgba.split()
    return Image.merge("RGBA", (r, g, b, soft_img))
