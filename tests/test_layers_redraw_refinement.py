import asyncio
import base64
import io
import json
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

    def __init__(self, output_rgb=(242, 240, 224)):
        self.calls = []
        self.model = "gpt-image-2"
        self.output_rgb = output_rgb

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
            input_img = probe.convert("RGB")
            size = input_img.size
            input_arr = np.asarray(input_img)
            non_cream_pixels = int(
                np.any(input_arr != np.array((252, 248, 240)), axis=2).sum()
            )
        with Image.open(mask_path) as mask_probe:
            mask_alpha = mask_probe.convert("RGBA").split()[-1]
            mask_arr = np.asarray(mask_alpha)
            edit_pixels = int((mask_arr == 0).sum())
            preserve_pixels = int((mask_arr == 255).sum())
        self.calls.append(
            {
                "image_path": image_path,
                "mask_path": mask_path,
                "size": size,
                "prompt": prompt,
                "non_cream_pixels": non_cream_pixels,
                "edit_pixels": edit_pixels,
                "preserve_pixels": preserve_pixels,
            }
        )
        return type(
            "Result",
            (),
            {
                "image_b64": _png_b64(Image.new("RGB", size, self.output_rgb)),
                "mime": "image/png",
                "metadata": {
                    "cost_usd": 0.0123,
                    "usage": {
                        "input_tokens": 100,
                        "output_tokens": 200,
                    },
                },
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
    assert advisory["refinement_source_context_used"] is True
    assert advisory["refinement_edit_matte"] == "flower_evidence"


def test_refined_flower_layer_uses_source_crop_square_padding(tmp_path, monkeypatch):
    from vulca.layers import redraw as redraw_module
    import vulca.providers as providers_mod

    provider = RecordingEditProvider()
    monkeypatch.setattr(
        providers_mod, "get_image_provider", lambda name, api_key="": provider
    )
    artwork = _stage_broad_flower_layer(tmp_path)

    _run(
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

    assert provider.calls
    first = provider.calls[0]
    assert first["size"] == (1024, 1024)
    assert first["non_cream_pixels"] > first["edit_pixels"]
    assert first["edit_pixels"] > 0
    assert first["preserve_pixels"] > 0


def test_refined_flower_layer_outputs_flower_edit_matte_not_child_context(
    tmp_path, monkeypatch
):
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

    assert out_area < parent_area * 0.5
    assert out_area <= sum(call["edit_pixels"] for call in provider.calls)


def test_refined_flower_layer_suppresses_black_generated_artifacts(
    tmp_path, monkeypatch
):
    from vulca.layers import redraw as redraw_module
    import vulca.providers as providers_mod

    provider = RecordingEditProvider(output_rgb=(0, 0, 0))
    monkeypatch.setattr(
        providers_mod, "get_image_provider", lambda name, api_key="": provider
    )
    artwork = _stage_broad_flower_layer(tmp_path)

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

    out = Image.open(result.image_path).convert("RGBA")
    arr = np.asarray(out)
    visible = arr[:, :, 3] > 0
    dark_visible = (
        visible
        & (arr[:, :, 0] < 20)
        & (arr[:, :, 1] < 20)
        & (arr[:, :, 2] < 20)
    )

    assert not dark_visible.any()


def test_refined_flower_layer_suppresses_generated_hedge_fill_inside_matte(
    tmp_path, monkeypatch
):
    from vulca.layers import redraw as redraw_module
    import vulca.providers as providers_mod

    provider = RecordingEditProvider(output_rgb=(35, 92, 43))
    monkeypatch.setattr(
        providers_mod, "get_image_provider", lambda name, api_key="": provider
    )
    artwork = _stage_broad_flower_layer(tmp_path)

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

    out = Image.open(result.image_path).convert("RGBA")
    arr = np.asarray(out)
    visible = arr[:, :, 3] > 0
    green_fill = (
        visible
        & (arr[:, :, 0] < 70)
        & (arr[:, :, 1] > 70)
        & (arr[:, :, 2] < 70)
    )

    assert not green_fill.any()


def test_flower_edit_matte_removes_isolated_bright_specks():
    from vulca.layers import redraw as redraw_module

    source = Image.new("RGB", (80, 60), (35, 92, 43))
    draw = ImageDraw.Draw(source)
    draw.ellipse((28, 22, 43, 37), fill=(238, 235, 220))
    draw.ellipse((34, 28, 38, 32), fill=(218, 172, 54))
    for xy in ((6, 6), (72, 9), (12, 52)):
        source.putpixel(xy, (245, 244, 232))

    child_alpha = Image.new("L", source.size, 255)

    matte = redraw_module._build_flower_edit_matte(source, child_alpha)
    arr = np.asarray(matte)

    assert arr[30, 36] > 0
    assert arr[6, 6] == 0
    assert arr[9, 72] == 0
    assert arr[52, 12] == 0


def test_refined_flower_layer_writes_child_artifacts_and_summary(
    tmp_path, monkeypatch
):
    from vulca.layers import redraw as redraw_module
    import vulca.providers as providers_mod

    provider = RecordingEditProvider()
    monkeypatch.setattr(
        providers_mod, "get_image_provider", lambda name, api_key="": provider
    )
    artwork = _stage_broad_flower_layer(tmp_path)
    artifact_dir = tmp_path / "redraw_artifacts"

    _run(
        redraw_module.redraw_layer(
            artwork,
            layer_name="flowers",
            instruction="small bright white wildflowers with warm yellow centers",
            provider="openai",
            artwork_dir=str(tmp_path),
            route="auto",
            preserve_alpha=True,
            debug_artifact_dir=str(artifact_dir),
        )
    )

    summary_path = artifact_dir / "summary.json"
    assert summary_path.exists()
    summary = json.loads(summary_path.read_text())
    assert summary["status"] == "completed"
    assert summary["child_count"] >= 3
    assert summary["total_cost_usd"] > 0
    assert summary["failures"] == []

    first = summary["calls"][0]
    assert first["status"] == "completed"
    assert first["cost_usd"] == 0.0123
    assert first["usage"] == {"input_tokens": 100, "output_tokens": 200}
    for key in ("input_path", "mask_path", "raw_path", "patch_path", "pasteback_path"):
        assert Path(first[key]).exists()
