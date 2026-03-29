"""Regenerate unified image from composite — solves cross-layer consistency."""
from __future__ import annotations

import base64
import logging
import os
from pathlib import Path

logger = logging.getLogger("vulca.layers")


def build_regenerate_prompt(*, tradition: str = "default") -> str:
    """Build prompt for regenerating a unified image from a composite reference."""
    parts = [
        "Generate a high-quality, unified artwork based on this reference image.",
        "The reference shows the desired composition, color palette, and style.",
        "Create a fresh, consistent version where lighting, perspective, and style",
        "are perfectly unified across all elements. No visible seams or inconsistencies.",
    ]
    if tradition != "default":
        parts.append(f"Maintain the {tradition.replace('_', ' ')} cultural tradition and technique.")
    parts.append("Output: 1024x1024, publication quality.")
    return "\n".join(parts)


async def regenerate_from_composite(
    composite_path: str,
    *,
    tradition: str = "default",
    provider: str = "gemini",
    api_key: str = "",
    output_path: str = "",
) -> str:
    """Generate a fresh unified image using the composite as reference."""
    from vulca.providers import get_image_provider

    prompt = build_regenerate_prompt(tradition=tradition)
    ref_b64 = base64.b64encode(Path(composite_path).read_bytes()).decode()

    img_provider = get_image_provider(
        provider, api_key=api_key or os.environ.get("GOOGLE_API_KEY", "")
    )

    result = await img_provider.generate(
        prompt,
        tradition=tradition,
        reference_image_b64=ref_b64,
    )

    out = Path(output_path) if output_path else Path(composite_path).parent / "regenerated.jpg"
    out.write_bytes(base64.b64decode(result.image_b64))
    return str(out)
