import asyncio
import base64
import io
from pathlib import Path

import numpy as np
from PIL import Image

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
                "image_b64": _png_b64(Image.new("RGB", size, (240, 240, 210))),
                "mime": "image/png",
                "metadata": {},
            },
        )()

    async def generate(self, prompt, **kwargs):
        raise AssertionError("sparse crop route must not call maskless generate")


def _stage(tmp_path: Path, boxes):
    size = (1000, 1000)
    alpha = Image.new("L", size, 0)
    for x, y, w, h in boxes:
        alpha.paste(Image.new("L", (w, h), 255), (x, y))
    rgb = Image.new("RGB", size, (120, 80, 60))
    Image.merge("RGBA", (*rgb.split(), alpha)).save(tmp_path / "fg.png")
    Image.new("RGB", size, (100, 100, 100)).save(tmp_path / "source.png")
    write_manifest(
        [
            LayerInfo(
                name="fg",
                description="foreground",
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


def test_sparse_single_uses_one_bbox_crop(tmp_path, monkeypatch):
    from vulca.layers import redraw as redraw_module
    import vulca.providers as providers_mod

    provider = RecordingEditProvider()
    monkeypatch.setattr(
        providers_mod, "get_image_provider", lambda name, api_key="": provider
    )
    artwork = _stage(tmp_path, [(440, 440, 80, 80)])

    result = _run(
        redraw_module.redraw_layer(
            artwork,
            layer_name="fg",
            instruction="make it cleaner",
            provider="openai",
            artwork_dir=str(tmp_path),
            route="auto",
            preserve_alpha=True,
        )
    )

    assert len(provider.calls) == 1
    assert provider.calls[0]["size"][0] < 1000
    assert provider.calls[0]["size"][1] < 1000
    out = Image.open(result.image_path).convert("RGBA")
    assert out.size == (1000, 1000)
    assert np.array_equal(
        np.array(out.split()[-1]),
        np.array(Image.open(tmp_path / "fg.png").convert("RGBA").split()[-1]),
    )


def test_sparse_multi_uses_one_call_per_component(tmp_path, monkeypatch):
    from vulca.layers import redraw as redraw_module
    import vulca.providers as providers_mod

    provider = RecordingEditProvider()
    monkeypatch.setattr(
        providers_mod, "get_image_provider", lambda name, api_key="": provider
    )
    artwork = _stage(
        tmp_path,
        [(50, 50, 80, 80), (460, 60, 80, 80), (850, 70, 80, 80)],
    )

    _run(
        redraw_module.redraw_layer(
            artwork,
            layer_name="fg",
            instruction="make each instance cleaner",
            provider="openai",
            artwork_dir=str(tmp_path),
            route="auto",
            preserve_alpha=True,
        )
    )

    assert len(provider.calls) == 3
    assert all(call["size"][0] < 500 for call in provider.calls)


def test_forced_img2img_reports_full_canvas_advisory(tmp_path, monkeypatch):
    from vulca.layers import redraw as redraw_module
    import vulca.providers as providers_mod

    provider = RecordingEditProvider()
    monkeypatch.setattr(
        providers_mod, "get_image_provider", lambda name, api_key="": provider
    )
    artwork = _stage(tmp_path, [(440, 440, 80, 80)])

    result = _run(
        redraw_module.redraw_layer(
            artwork,
            layer_name="fg",
            instruction="make it cleaner",
            provider="openai",
            artwork_dir=str(tmp_path),
            route="img2img",
            preserve_alpha=True,
        )
    )

    advisory = getattr(result, "redraw_advisory", {})
    assert advisory["route_chosen"] == "img2img"
    assert advisory["redraw_route"] == "dense_full_canvas"
