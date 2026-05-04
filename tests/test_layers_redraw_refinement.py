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


class StaticRawEditProvider(RecordingEditProvider):
    def __init__(self, output):
        super().__init__()
        self.output = output.convert("RGBA")

    async def inpaint_with_mask(self, *, image_path, mask_path, prompt, **kwargs):
        with Image.open(image_path) as probe:
            size = probe.size
        with Image.open(mask_path) as mask_probe:
            mask_alpha = mask_probe.convert("RGBA").split()[-1]
            mask_arr = np.asarray(mask_alpha)
        self.calls.append(
            {
                "image_path": image_path,
                "mask_path": mask_path,
                "size": size,
                "prompt": prompt,
                "edit_pixels": int((mask_arr == 0).sum()),
                "preserve_pixels": int((mask_arr == 255).sum()),
            }
        )
        raw = self.output.resize(size, Image.Resampling.NEAREST)
        return type(
            "Result",
            (),
            {
                "image_b64": _png_b64(raw),
                "mime": "image/png",
                "metadata": {"cost_usd": 0.0123, "usage": {}},
            },
        )()


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


def _stage_broad_leaf_texture_layer(tmp_path: Path):
    size = (240, 180)
    source = Image.new("RGB", size, (72, 116, 58))
    draw = ImageDraw.Draw(source)
    for x in range(18, 220, 18):
        for y in range(16, 150, 16):
            draw.ellipse((x - 6, y - 4, x + 7, y + 5), fill=(92, 134, 62))
    alpha = Image.new("L", size, 0)
    ImageDraw.Draw(alpha).rectangle((12, 10, 228, 160), fill=255)
    Image.merge("RGBA", (*source.split(), alpha)).save(tmp_path / "hedge.png")
    source.save(tmp_path / "source.png")

    write_manifest(
        [
            LayerInfo(
                name="hedge",
                description="leafy hedge texture",
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
    assert advisory["refinement_strategy"] == "small_botanical_subject_replacement"
    assert advisory["refined_child_count"] >= 3
    assert advisory["mask_granularity_score"] >= 3
    assert advisory["refinement_source_context_used"] is True
    assert advisory["refinement_edit_matte"] == "small_botanical_evidence"
    assert advisory["refinement_replacement_matte"] == "small_botanical_removal"
    assert advisory["refinement_composition"] == (
        "small_botanical_evidence_paint_cover"
    )


def test_refined_flower_layer_honors_max_refinement_children(tmp_path, monkeypatch):
    from vulca.layers import redraw as redraw_module
    import vulca.providers as providers_mod

    provider = RecordingEditProvider()
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
            max_refinement_children=2,
        )
    )

    advisory = getattr(result, "redraw_advisory", {})

    assert len(provider.calls) == 2
    assert advisory["refined_child_count"] == 2
    assert advisory["max_refinement_children"] == 2


def test_refined_flower_layer_stops_at_redraw_cost_cap(tmp_path, monkeypatch):
    from vulca.layers import redraw as redraw_module
    import vulca.providers as providers_mod

    provider = RecordingEditProvider()
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
            max_redraw_cost_usd=0.0123,
        )
    )

    advisory = getattr(result, "redraw_advisory", {})

    assert len(provider.calls) == 1
    assert advisory["redraw_cost_cap_reached"] is True
    assert advisory["redraw_cost_cap_usd"] == 0.0123
    assert advisory["redraw_estimated_cost_usd"] == 0.0123
    assert advisory["refined_child_count"] == 1


def test_auto_redraw_skips_broad_leaf_texture_risk(tmp_path, monkeypatch):
    from vulca.layers import redraw as redraw_module
    import vulca.providers as providers_mod

    provider = RecordingEditProvider(output_rgb=(18, 58, 20))
    monkeypatch.setattr(
        providers_mod, "get_image_provider", lambda name, api_key="": provider
    )
    artwork = _stage_broad_leaf_texture_layer(tmp_path)

    result = _run(
        redraw_module.redraw_layer(
            artwork,
            layer_name="hedge",
            instruction="redraw leaf highlights as hand-painted botanical texture",
            provider="openai",
            artwork_dir=str(tmp_path),
            route="auto",
            preserve_alpha=True,
        )
    )

    advisory = getattr(result, "redraw_advisory", {})
    original = Image.open(tmp_path / "hedge.png").convert("RGBA")
    output = Image.open(result.image_path).convert("RGBA")

    assert provider.calls == []
    assert np.array_equal(np.asarray(output), np.asarray(original))
    assert advisory["redraw_skipped"] is True
    assert advisory["redraw_skip_reason"] == "broad_texture_repaint_risk"
    assert advisory["quality_gate_passed"] is False
    assert "broad_texture_repaint_risk" in advisory["quality_failures"]


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


def test_refined_flower_layer_drops_pure_hedge_generated_fill(
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

    assert not visible.any()


def test_refined_flower_layer_suppresses_olive_generated_fill_inside_matte(
    tmp_path, monkeypatch
):
    from vulca.layers import redraw as redraw_module
    import vulca.providers as providers_mod

    provider = RecordingEditProvider(output_rgb=(95, 120, 65))
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

    out_alpha = Image.open(result.image_path).convert("RGBA").split()[-1]
    out = Image.open(result.image_path).convert("RGBA")
    arr = np.asarray(out)
    visible = np.asarray(out_alpha).astype(bool)
    olive_fill = (
        visible
        & (arr[:, :, 0] > 80)
        & (arr[:, :, 0] < 120)
        & (arr[:, :, 1] > 105)
        & (arr[:, :, 1] < 135)
        & (arr[:, :, 2] > 50)
        & (arr[:, :, 2] < 80)
    )

    assert not olive_fill.any()


def test_flower_output_alpha_removes_green_fill_adjacent_to_petals():
    from vulca.layers import redraw as redraw_module

    patch = Image.new("RGB", (20, 20), (95, 120, 65))
    patch.putpixel((10, 10), (238, 235, 220))
    patch.putpixel((11, 10), (218, 172, 54))
    matte = Image.new("L", patch.size, 255)

    alpha = redraw_module._build_flower_output_alpha(patch, matte)
    arr = np.asarray(alpha)

    assert arr[10, 10] > 0
    assert arr[10, 11] > 0
    assert arr[10, 12] == 0


def test_flower_output_alpha_removes_neutral_olive_halo_adjacent_to_petals():
    from vulca.layers import redraw as redraw_module

    patch = Image.new("RGB", (20, 20), (30, 82, 38))
    patch.putpixel((10, 10), (238, 235, 220))
    patch.putpixel((11, 10), (218, 172, 54))
    patch.putpixel((12, 10), (105, 100, 65))
    matte = Image.new("L", patch.size, 255)

    alpha = redraw_module._build_flower_output_alpha(patch, matte)
    arr = np.asarray(alpha)

    assert arr[10, 10] > 0
    assert arr[10, 11] > 0
    assert arr[10, 12] == 0


def test_yellow_flower_output_alpha_rejects_gray_and_olive_scene_context():
    from vulca.layers import redraw as redraw_module

    patch = Image.new("RGB", (24, 18), (88, 116, 64))
    patch.putpixel((8, 9), (232, 190, 42))
    patch.putpixel((9, 9), (238, 206, 72))
    patch.putpixel((10, 9), (218, 218, 204))
    patch.putpixel((11, 9), (128, 138, 96))
    patch.putpixel((12, 9), (236, 235, 226))
    matte = Image.new("L", patch.size, 255)

    alpha = redraw_module._build_flower_output_alpha(
        patch,
        matte,
        target_palette="yellow",
    )
    arr = np.asarray(alpha)

    assert arr[9, 8] > 0
    assert arr[9, 9] > 0
    assert arr[9, 10] == 0
    assert arr[9, 11] == 0
    assert arr[9, 12] == 0


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


def test_flower_edit_matte_keeps_dense_clusters_organic():
    from vulca.layers import redraw as redraw_module

    source = Image.new("RGB", (220, 150), (35, 92, 43))
    draw = ImageDraw.Draw(source)
    for x in range(60, 170, 24):
        for y in range(42, 112, 22):
            draw.ellipse((x - 8, y - 7, x + 8, y + 7), fill=(238, 235, 220))
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(218, 172, 54))
    for y in range(42, 112, 22):
        draw.line((60, y, 168, y), fill=(238, 235, 220), width=1)

    child_alpha = Image.new("L", source.size, 0)
    ImageDraw.Draw(child_alpha).rectangle((38, 25, 190, 130), fill=255)

    matte = redraw_module._build_flower_edit_matte(source, child_alpha)
    arr = np.asarray(matte) > 8
    ys, xs = np.where(arr)
    bbox_area = int((xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1))
    fill_ratio = float(arr.sum()) / float(bbox_area)

    assert fill_ratio < 0.75


def test_flower_removal_matte_expands_to_cover_old_flower_residue():
    from vulca.layers import redraw as redraw_module

    source = Image.new("RGB", (80, 60), (35, 92, 43))
    draw = ImageDraw.Draw(source)
    draw.ellipse((32, 22, 47, 37), fill=(238, 235, 220))
    draw.ellipse((38, 28, 42, 32), fill=(218, 172, 54))
    residue_xy = (23, 30)
    source.putpixel(residue_xy, (156, 154, 132))

    child_alpha = Image.new("L", source.size, 0)
    ImageDraw.Draw(child_alpha).rectangle((22, 16, 55, 44), fill=255)

    edit_matte = redraw_module._build_flower_edit_matte(source, child_alpha)
    removal_matte = redraw_module._build_flower_removal_matte(
        source,
        child_alpha,
        edit_matte,
    )
    edit_arr = np.asarray(edit_matte)
    removal_arr = np.asarray(removal_matte)

    assert edit_arr[residue_xy[1], residue_xy[0]] == 0
    assert removal_arr[residue_xy[1], residue_xy[0]] > 0


def test_source_context_generation_uses_edit_matte_not_broad_removal_matte():
    from vulca.layers import redraw as redraw_module

    provider = RecordingEditProvider(output_rgb=(242, 240, 224))
    source = Image.new("RGB", (64, 64), (35, 92, 43))
    edit_matte = Image.new("L", source.size, 0)
    ImageDraw.Draw(edit_matte).ellipse((27, 27, 37, 37), fill=255)
    removal_matte = Image.new("L", source.size, 0)
    ImageDraw.Draw(removal_matte).rectangle((10, 10, 54, 54), fill=255)

    crop_out, _result = _run(
        redraw_module._redraw_source_context_with_edit_matte(
            source_crop=source,
            edit_matte=edit_matte,
            removal_matte=removal_matte,
            instruction="paint small white wildflowers",
            provider_inst=provider,
            tradition="default",
            target_description="wildflower cluster on hedge",
        )
    )

    output_alpha_px = int(
        (np.asarray(crop_out.convert("RGBA").split()[-1]) > 0).sum()
    )

    assert provider.calls[0]["edit_pixels"] < 260_000
    assert output_alpha_px < 900


def test_source_context_generation_expands_organic_matte_without_filling_removal():
    from vulca.layers import redraw as redraw_module

    provider = RecordingEditProvider(output_rgb=(242, 240, 224))
    source = Image.new("RGB", (64, 64), (35, 92, 43))
    edit_matte = Image.new("L", source.size, 0)
    draw = ImageDraw.Draw(edit_matte)
    draw.ellipse((17, 24, 27, 34), fill=255)
    draw.ellipse((36, 25, 46, 35), fill=255)
    removal_matte = Image.new("L", source.size, 0)
    ImageDraw.Draw(removal_matte).rectangle((10, 10, 54, 54), fill=255)

    crop_out, _result = _run(
        redraw_module._redraw_source_context_with_edit_matte(
            source_crop=source,
            edit_matte=edit_matte,
            removal_matte=removal_matte,
            instruction="paint small white wildflowers",
            provider_inst=provider,
            tradition="default",
            target_description="wildflower cluster on hedge",
        )
    )

    output_alpha_px = int(
        (np.asarray(crop_out.convert("RGBA").split()[-1]) > 0).sum()
    )

    assert 90_000 < provider.calls[0]["edit_pixels"] < 360_000
    assert 350 < output_alpha_px < 1400


def test_source_context_generation_uses_micro_botanical_prompt():
    from vulca.layers import redraw as redraw_module

    provider = RecordingEditProvider(output_rgb=(232, 190, 42))
    source = Image.new("RGB", (64, 64), (35, 92, 43))
    edit_matte = Image.new("L", source.size, 0)
    ImageDraw.Draw(edit_matte).ellipse((27, 27, 37, 37), fill=255)

    _run(
        redraw_module._redraw_source_context_with_edit_matte(
            source_crop=source,
            edit_matte=edit_matte,
            instruction=(
                "Preserve grass stems, hedge leaves, white flowers, guardrail, "
                "sky, vehicles, source lighting, and spatial depth. Make the "
                "yellow dandelion and buttercup flower heads feel hand-painted "
                "with warm centers and varied spacing."
            ),
            provider_inst=provider,
            tradition="default",
            target_description="roadside dandelion heads beside vehicles",
            target_palette="yellow",
        )
    )

    prompt = provider.calls[0]["prompt"].lower()

    assert "only the transparent mask pixels" in prompt
    assert "yellow dandelion" in prompt
    assert "flower head" in prompt
    assert "hand-painted" in prompt
    assert "guardrail" not in prompt
    assert "vehicle" not in prompt
    assert "sky" not in prompt
    assert "roadside" not in prompt


def test_source_context_generation_prompts_child_count_and_scale():
    from vulca.layers import redraw as redraw_module

    provider = RecordingEditProvider(output_rgb=(232, 190, 42))
    source = Image.new("RGB", (72, 72), (35, 92, 43))
    edit_matte = Image.new("L", source.size, 0)
    draw = ImageDraw.Draw(edit_matte)
    draw.ellipse((16, 28, 28, 40), fill=255)
    draw.ellipse((44, 29, 56, 41), fill=255)

    _run(
        redraw_module._redraw_source_context_with_edit_matte(
            source_crop=source,
            edit_matte=edit_matte,
            instruction="paint yellow dandelion and buttercup flower heads",
            provider_inst=provider,
            tradition="default",
            target_description="dandelion heads in grass",
            target_palette="yellow",
        )
    )

    prompt = provider.calls[0]["prompt"].lower()

    assert "exactly 2" in prompt
    assert "do not add extra" in prompt
    assert "match the original head size" in prompt


def test_source_context_generation_rejects_raw_scene_thumbnail():
    from vulca.layers import redraw as redraw_module

    raw_scene = Image.new("RGBA", (1024, 1024), (54, 126, 220, 255))
    draw = ImageDraw.Draw(raw_scene)
    draw.rectangle((0, 540, 1024, 1024), fill=(78, 118, 58, 255))
    draw.rectangle((160, 650, 880, 760), fill=(155, 160, 158, 255))
    draw.rectangle((250, 455, 760, 620), fill=(170, 24, 35, 255))
    draw.ellipse((480, 480, 544, 544), fill=(232, 190, 42, 255))
    for x in range(340, 700, 60):
        draw.ellipse((x, 720, x + 28, 748), fill=(232, 190, 42, 255))
    provider = StaticRawEditProvider(raw_scene)

    source = Image.new("RGB", (72, 72), (35, 92, 43))
    edit_matte = Image.new("L", source.size, 0)
    ImageDraw.Draw(edit_matte).ellipse((25, 25, 47, 47), fill=255)

    crop_out, _result = _run(
        redraw_module._redraw_source_context_with_edit_matte(
            source_crop=source,
            edit_matte=edit_matte,
            instruction="paint yellow dandelion and buttercup flower heads",
            provider_inst=provider,
            tradition="default",
            target_description="dandelion heads in grass",
            target_palette="yellow",
        )
    )

    alpha_px = int((np.asarray(crop_out.convert("RGBA").split()[-1]) > 0).sum())

    assert alpha_px == 0


def test_refined_flower_replacement_covers_old_source_flower_residue(
    tmp_path, monkeypatch
):
    from vulca.layers import redraw as redraw_module
    import vulca.providers as providers_mod

    provider = RecordingEditProvider(output_rgb=(242, 240, 224))
    monkeypatch.setattr(
        providers_mod, "get_image_provider", lambda name, api_key="": provider
    )
    artwork = _stage_broad_flower_layer(tmp_path)
    source_path = tmp_path / "source.png"
    source = Image.open(source_path).convert("RGB")
    residue_xy = (42, 58)
    source.putpixel(residue_xy, (156, 154, 132))
    source.save(source_path)

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

    layer = Image.open(result.image_path).convert("RGBA")
    source_rgba = Image.open(source_path).convert("RGBA")
    source_rgba.alpha_composite(layer)
    after = source_rgba.convert("RGB")

    assert layer.getpixel(residue_xy)[3] > 0
    assert after.getpixel(residue_xy) != (156, 154, 132)


def test_flower_replacement_patch_does_not_expose_cleared_background():
    from vulca.layers import redraw as redraw_module

    source = Image.new("RGB", (50, 40), (35, 92, 43))
    old_flower_xy = (20, 20)
    hedge_xy = (30, 20)
    ImageDraw.Draw(source).ellipse((18, 18, 22, 22), fill=(238, 235, 220))

    cleared = Image.new("RGB", source.size, (78, 91, 44))
    removal_matte = Image.new("L", source.size, 0)
    ImageDraw.Draw(removal_matte).rectangle((10, 10, 38, 30), fill=255)
    generated = Image.new("RGBA", source.size, (0, 0, 0, 0))

    patch = redraw_module._compose_flower_replacement_patch(
        source,
        cleared,
        generated,
        removal_matte,
    )

    assert patch.getpixel(old_flower_xy)[3] == 0
    assert patch.getpixel(hedge_xy)[3] == 0


def test_flower_replacement_patch_uses_nearby_generated_paint_for_old_flowers():
    from vulca.layers import redraw as redraw_module

    source = Image.new("RGB", (50, 40), (35, 92, 43))
    old_flower_xy = (20, 20)
    ImageDraw.Draw(source).ellipse((18, 18, 22, 22), fill=(238, 235, 220))

    cleared = Image.new("RGB", source.size, (95, 120, 65))
    removal_matte = Image.new("L", source.size, 0)
    ImageDraw.Draw(removal_matte).ellipse((16, 16, 24, 24), fill=255)
    generated = Image.new("RGBA", source.size, (0, 0, 0, 0))
    generated.putpixel((25, 20), (242, 240, 224, 255))
    generated.putpixel((26, 20), (218, 172, 54, 255))

    patch = redraw_module._compose_flower_replacement_patch(
        source,
        cleared,
        generated,
        removal_matte,
    )

    old_pixel = patch.getpixel(old_flower_xy)

    assert old_pixel[3] > 0
    assert old_pixel[:3] != (95, 120, 65)
    assert old_pixel[0] > 170


def test_flower_replacement_patch_does_not_propagate_generated_green_halo():
    from vulca.layers import redraw as redraw_module

    source = Image.new("RGB", (50, 40), (35, 92, 43))
    old_flower_xy = (20, 20)
    ImageDraw.Draw(source).ellipse((18, 18, 22, 22), fill=(238, 235, 220))

    cleared = Image.new("RGB", source.size, (95, 120, 65))
    removal_matte = Image.new("L", source.size, 0)
    ImageDraw.Draw(removal_matte).ellipse((16, 16, 24, 24), fill=255)
    generated = Image.new("RGBA", source.size, (0, 0, 0, 0))
    generated.putpixel((19, 20), (70, 110, 45, 255))
    generated.putpixel((25, 20), (242, 240, 224, 255))
    generated.putpixel((26, 20), (218, 172, 54, 255))

    patch = redraw_module._compose_flower_replacement_patch(
        source,
        cleared,
        generated,
        removal_matte,
    )

    old_pixel = patch.getpixel(old_flower_xy)

    assert old_pixel[3] > 0
    assert old_pixel[0] > 170
    assert old_pixel[1] > 140
    assert old_pixel[2] > 100


def test_yellow_replacement_patch_uses_yellow_paint_not_scene_context():
    from vulca.layers import redraw as redraw_module

    source = Image.new("RGB", (50, 40), (35, 92, 43))
    old_flower_xy = (20, 20)
    ImageDraw.Draw(source).ellipse((18, 18, 22, 22), fill=(232, 190, 42))

    cleared = Image.new("RGB", source.size, (95, 120, 65))
    removal_matte = Image.new("L", source.size, 0)
    ImageDraw.Draw(removal_matte).ellipse((16, 16, 24, 24), fill=255)
    generated = Image.new("RGBA", source.size, (0, 0, 0, 0))
    generated.putpixel((19, 20), (94, 122, 67, 255))
    generated.putpixel((25, 20), (232, 190, 42, 255))
    generated.putpixel((26, 20), (218, 218, 204, 255))

    patch = redraw_module._compose_flower_replacement_patch(
        source,
        cleared,
        generated,
        removal_matte,
        target_palette="yellow",
    )

    old_pixel = patch.getpixel(old_flower_xy)

    assert old_pixel[3] > 0
    assert old_pixel[0] > 180
    assert old_pixel[1] > 140
    assert old_pixel[2] < 120


def test_yellow_replacement_patch_does_not_expand_across_whole_old_head():
    from vulca.layers import redraw as redraw_module

    source = Image.new("RGB", (60, 40), (35, 92, 43))
    old_flower_xy = (20, 20)
    ImageDraw.Draw(source).ellipse((16, 16, 28, 24), fill=(232, 190, 42))

    cleared = Image.new("RGB", source.size, (95, 120, 65))
    removal_matte = Image.new("L", source.size, 0)
    ImageDraw.Draw(removal_matte).ellipse((14, 14, 30, 26), fill=255)
    generated = Image.new("RGBA", source.size, (0, 0, 0, 0))
    generated.putpixel((30, 20), (232, 190, 42, 255))

    patch = redraw_module._compose_flower_replacement_patch(
        source,
        cleared,
        generated,
        removal_matte,
        target_palette="yellow",
    )

    assert patch.getpixel(old_flower_xy)[3] == 0
    assert patch.getpixel((30, 20))[3] > 0


def test_flower_replacement_patch_does_not_fill_distant_old_flowers():
    from vulca.layers import redraw as redraw_module

    source = Image.new("RGB", (80, 40), (35, 92, 43))
    old_flower_xy = (20, 20)
    ImageDraw.Draw(source).ellipse((18, 18, 22, 22), fill=(238, 235, 220))

    cleared = Image.new("RGB", source.size, (95, 120, 65))
    removal_matte = Image.new("L", source.size, 0)
    ImageDraw.Draw(removal_matte).ellipse((16, 16, 24, 24), fill=255)
    generated = Image.new("RGBA", source.size, (0, 0, 0, 0))
    generated.putpixel((60, 20), (242, 240, 224, 255))
    generated.putpixel((61, 20), (218, 172, 54, 255))

    patch = redraw_module._compose_flower_replacement_patch(
        source,
        cleared,
        generated,
        removal_matte,
    )

    assert patch.getpixel(old_flower_xy)[3] == 0


def test_clear_source_crop_uses_surrounding_texture_not_single_fill():
    from vulca.layers import redraw as redraw_module

    source = Image.new("RGB", (40, 24), (35, 92, 43))
    for x in range(40):
        for y in range(24):
            source.putpixel((x, y), (25 + x, 82 + (y % 5), 38 + (x % 7)))
    ImageDraw.Draw(source).ellipse((14, 8, 25, 17), fill=(238, 235, 220))

    removal_matte = Image.new("L", source.size, 0)
    ImageDraw.Draw(removal_matte).rectangle((10, 5, 30, 20), fill=255)

    cleared = redraw_module._clear_source_crop_with_matte(source, removal_matte)
    cleared_arr = np.asarray(cleared)
    remove_arr = np.asarray(removal_matte) > 0
    filled_colors = {
        tuple(pixel)
        for pixel in cleared_arr[remove_arr].reshape(-1, 3)
    }

    assert len(filled_colors) > 8


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
    for key in (
        "source_crop_path",
        "removal_matte_path",
        "cleared_crop_path",
        "input_path",
        "mask_path",
        "raw_path",
        "patch_path",
        "pasteback_path",
    ):
        assert Path(first[key]).exists()

    assert Path(summary["final_source_pasteback_path"]).exists()
    source_pasteback = Image.open(summary["final_source_pasteback_path"]).convert(
        "RGBA"
    )
    assert source_pasteback.size == (240, 180)
