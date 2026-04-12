"""Inpaint API -- partial region redraw with Gemini blend."""
from __future__ import annotations

import asyncio
import time

from vulca.types import InpaintResult


async def ainpaint(
    image: str,
    *,
    region: str,
    instruction: str,
    tradition: str = "default",
    provider: str = "gemini",
    count: int = 4,
    select: int | None = None,
    output: str = "",
    api_key: str = "",
    mock: bool = False,
) -> InpaintResult:
    """Inpaint a region of an artwork (async).

    Args:
        image: Path to the image file.
        region: NL description ("fix the sky") or coordinates ("0,0,100,35").
        instruction: What to change in the region.
        tradition: Cultural tradition for style consistency.
        provider: Image generation provider (e.g. "gemini", "openai").
        count: Number of repaint variants to generate.
        select: Auto-select variant index (0-based). None = return all.
        output: Output path for blended image.
        api_key: API key override.
        mock: Use mock mode (no real API calls).
    """
    from vulca.studio.phases.inpaint import (
        InpaintPhase,
        crop_region,
        is_coordinate_string,
        parse_region_coordinates,
    )

    t0 = time.monotonic()
    phase = InpaintPhase()

    # 1. Parse or detect region
    if is_coordinate_string(region):
        bbox = parse_region_coordinates(region)
    else:
        if mock:
            bbox = {"x": 0, "y": 0, "w": 50, "h": 50}
        else:
            bbox = await phase.detect_region(image, region, api_key=api_key)

    # 2. Crop
    import tempfile

    crop_dir = tempfile.mkdtemp(prefix="vulca-inpaint-")
    crop_path = crop_region(image, bbox, output_dir=crop_dir)

    # 3. Repaint variants
    if mock:
        from pathlib import Path

        from PIL import Image as PILImage

        variants = []
        for i in range(count):
            p = Path(crop_dir) / f"repaint_v{i + 1}.png"
            PILImage.new("RGB", (128, 128), f"#{i * 30 + 50:02x}{i * 20 + 80:02x}FF").save(str(p))
            variants.append(str(p))
    else:
        variants = await phase.repaint(
            image,
            crop_path,
            instruction=instruction,
            tradition=tradition,
            provider=provider,
            count=count,
            output_dir=crop_dir,
            api_key=api_key,
        )

    # 4. Select + Blend
    sel_idx = select if select is not None else 0
    sel_idx = min(sel_idx, len(variants) - 1) if variants else 0

    blended = ""
    if variants:
        if mock:
            from pathlib import Path

            from PIL import Image as PILImage

            blended_path = Path(crop_dir) / "blended.png"
            PILImage.new("RGB", (256, 256), "blue").save(str(blended_path))
            blended = str(blended_path)
        else:
            blended = await phase.blend(
                image,
                variants[sel_idx],
                bbox=bbox,
                output_path=output,
                api_key=api_key,
            )

    elapsed = int((time.monotonic() - t0) * 1000)
    cost = 0.0 if mock else 0.05

    return InpaintResult(
        bbox=bbox,
        variants=variants,
        selected=sel_idx,
        blended=blended,
        original=image,
        instruction=instruction,
        tradition=tradition,
        latency_ms=elapsed,
        cost_usd=cost,
    )


def inpaint(
    image: str,
    *,
    region: str,
    instruction: str,
    tradition: str = "default",
    provider: str = "gemini",
    count: int = 4,
    select: int | None = None,
    output: str = "",
    api_key: str = "",
    mock: bool = False,
) -> InpaintResult:
    """Inpaint a region of an artwork (sync wrapper).

    Args:
        image: Path to the image file.
        region: NL description ("fix the sky") or coordinates ("0,0,100,35").
        instruction: What to change in the region.
        tradition: Cultural tradition for style consistency.
        provider: Image generation provider (e.g. "gemini", "openai").
        count: Number of repaint variants to generate.
        select: Auto-select variant index (0-based). None = return all.
        output: Output path for blended image.
        api_key: API key override.
        mock: Use mock mode (no real API calls).
    """
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(
            ainpaint(
                image,
                region=region,
                instruction=instruction,
                tradition=tradition,
                provider=provider,
                count=count,
                select=select,
                output=output,
                api_key=api_key,
                mock=mock,
            )
        )
    finally:
        loop.close()
