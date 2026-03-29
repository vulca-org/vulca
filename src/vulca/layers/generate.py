"""Per-layer generation — generate each layer independently with appropriate background."""
from __future__ import annotations

import base64
import logging
from pathlib import Path

from PIL import Image

from vulca.layers.types import LayerInfo, LayerResult
from vulca.layers.split import chromakey_white, chromakey_black

logger = logging.getLogger("vulca.layers")

_BG_MAP = {"normal": "white", "screen": "black", "multiply": "gray"}


def infer_bg_color(blend_mode: str) -> str:
    """Infer generation background color from blend mode."""
    return _BG_MAP.get(blend_mode, "white")


def build_layer_prompt(info: LayerInfo, *, tradition: str = "default", style_ref: str = "") -> str:
    """Build prompt for generating a single layer."""
    bg = info.bg_color
    parts = [
        f"Generate ONLY [{info.description}] isolated on a solid {bg} background.",
        f"This is one layer of a layered artwork composition.",
        f"The element should be cleanly separated from the background with no bleeding.",
    ]
    if tradition != "default":
        parts.append(f"Style/tradition: {tradition.replace('_', ' ')}")
    if style_ref:
        parts.append("Match the style, color palette, and lighting of the provided reference image exactly.")
    parts.append("Output: 1024x1024 image, no text or watermarks.")
    return "\n".join(parts)


async def generate_layer(
    info: LayerInfo,
    *,
    tradition: str = "default",
    reference_image: str = "",
    provider: str = "gemini",
    api_key: str = "",
    output_dir: str = "",
) -> LayerResult:
    """Generate a single layer image with appropriate background, then chromakey."""
    import os
    from vulca.providers import get_image_provider

    prompt = build_layer_prompt(info, tradition=tradition, style_ref=reference_image)
    ref_b64 = ""
    if reference_image and Path(reference_image).exists():
        ref_b64 = base64.b64encode(Path(reference_image).read_bytes()).decode()

    img_provider = get_image_provider(provider, api_key=api_key or os.environ.get("GOOGLE_API_KEY", ""))

    result = await img_provider.generate(
        prompt,
        tradition=tradition,
        reference_image_b64=ref_b64,
    )

    out_dir = Path(output_dir) if output_dir else Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save raw generation
    raw_path = out_dir / f"{info.name}_raw.png"
    raw_bytes = base64.b64decode(result.image_b64)
    raw_path.write_bytes(raw_bytes)

    # Chromakey based on bg_color
    raw_img = Image.open(str(raw_path))
    if info.bg_color == "white":
        alpha_img = chromakey_white(raw_img)
    elif info.bg_color == "black":
        alpha_img = chromakey_black(raw_img)
    else:
        alpha_img = raw_img.convert("RGBA")

    final_path = out_dir / f"{info.name}.png"
    alpha_img.save(str(final_path))

    return LayerResult(info=info, image_path=str(final_path))
