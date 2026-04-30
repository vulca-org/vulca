import asyncio
import base64
import io
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from vulca.layers.manifest import load_manifest, write_manifest
from vulca.layers.types import LayerInfo
from vulca.providers.base import ImageEditCapabilities


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _png_b64(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


class RecordingEditProvider:
    capabilities = frozenset({"raw_rgba"})

    def __init__(self):
        self.calls = []
        self.model = "gpt-image-2"

    def edit_capabilities(self):
        return ImageEditCapabilities(
            supports_edits=True,
            requires_mask_for_edits=True,
            supports_masked_edits=True,
            supports_unmasked_edits=False,
            supports_quality=True,
        )

    async def inpaint_with_mask(self, *, image_path, mask_path, prompt, **kwargs):
        with Image.open(image_path) as probe:
            size = probe.size
        self.calls.append(
            {
                "image_path": image_path,
                "mask_path": mask_path,
                "size": size,
                "prompt": prompt,
            }
        )
        return type(
            "Result",
            (),
            {
                "image_b64": _png_b64(Image.new("RGB", size, (242, 240, 224))),
                "mime": "image/png",
                "metadata": {},
            },
        )()

    async def generate(self, prompt, **kwargs):
        raise AssertionError("refinement route must use masked edits")


def _stage_broad_flower_layer(tmp_path: Path):
    size = (240, 180)
    source = Image.new("RGB", size, (35, 92, 43))
    draw = ImageDraw.Draw(source)
    for box in ((46, 48, 65, 67), (112, 78, 132, 98), (178, 42, 199, 63)):
        draw.ellipse(box, fill=(238, 235, 220))
        cx = (box[0] + box[2]) // 2
        cy = (box[1] + box[3]) // 2
        draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=(218, 172, 54))

    alpha = Image.new("L", size, 0)
    ImageDraw.Draw(alpha).rectangle((28, 25, 215, 122), fill=255)
    Image.merge("RGBA", (*source.split(), alpha)).save(tmp_path / "flowers.png")
    source.save(tmp_path / "source.png")

    write_manifest(
        [
            LayerInfo(
                name="flowers",
                description="wildflower cluster on hedge",
                z_index=1,
                content_type="subject",
            )
        ],
        output_dir=str(tmp_path),
        width=size[0],
        height=size[1],
        source_image="source.png",
    )
    return load_manifest(str(tmp_path))


def test_refined_flower_layer_uses_one_masked_edit_per_child(tmp_path, monkeypatch):
    from vulca.layers import redraw as redraw_module
    import vulca.providers as providers_mod

    provider = RecordingEditProvider()
    monkeypatch.setattr(
        providers_mod, "get_image_provider", lambda name, api_key="": provider
    )
    artwork = _stage_broad_flower_layer(tmp_path)
    parent_alpha = Image.open(tmp_path / "flowers.png").convert("RGBA").split()[-1]
    parent_area = int(np.asarray(parent_alpha).astype(bool).sum())

    result = _run(
        redraw_module.redraw_layer(
            artwork,
            layer_name="flowers",
            instruction="small bright white wildflowers with warm yellow centers",
            provider="openai",
            artwork_dir=str(tmp_path),
            route="auto",
            preserve_alpha=True,
        )
    )

    out_alpha = Image.open(result.image_path).convert("RGBA").split()[-1]
    out_area = int(np.asarray(out_alpha).astype(bool).sum())
    advisory = getattr(result, "redraw_advisory", {})

    assert len(provider.calls) >= 3
    assert out_area < parent_area
    assert advisory["refinement_applied"] is True
    assert advisory["refinement_reason"] == "target_evidence_components"
    assert advisory["refinement_strategy"] == "bright_small_subject"
    assert advisory["refined_child_count"] >= 3
    assert advisory["mask_granularity_score"] >= 3
