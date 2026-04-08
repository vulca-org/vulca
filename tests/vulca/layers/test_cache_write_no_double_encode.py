"""v0.13.2 P2: fresh-generate path saves PNG exactly once (no PIL double encode)."""
from __future__ import annotations

import asyncio
import base64
import io
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from vulca.layers.keying import CanvasSpec
from vulca.layers.keying.luminance import LuminanceKeying
from vulca.layers.layered_cache import LayerCache
from vulca.layers.layered_generate import generate_one_layer
from vulca.layers.layered_prompt import TraditionAnchor
from vulca.layers.types import LayerInfo


def _png_bytes() -> bytes:
    img = Image.new("RGB", (32, 32), (128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class _R:
    def __init__(self, b):
        self.image_b64 = base64.b64encode(b).decode()


class _Prov:
    id = "fake"
    model = "v1"

    def __init__(self, png: bytes):
        self._png = png

    async def generate(self, *, prompt, raw_prompt=False, **kwargs):
        return _R(self._png)


def _layer() -> LayerInfo:
    return LayerInfo(name="layer1", description="t", z_index=0, content_type="subject")


def _anchor() -> TraditionAnchor:
    return TraditionAnchor(
        canvas_color_hex="#ffffff",
        canvas_description="white canvas",
        style_keywords="",
    )


def test_fresh_generate_calls_pil_save_once(tmp_path: Path):
    """Fresh generation must save PNG exactly once. Cache write should
    re-read disk bytes instead of re-encoding via PIL."""
    cache = LayerCache(tmp_path)
    # Pre-compute provider bytes outside the patch so the provider's own
    # PIL encode isn't counted.
    png = _png_bytes()
    save_calls: list = []
    real_save = Image.Image.save

    def counting_save(self, *args, **kwargs):
        save_calls.append((args, kwargs))
        return real_save(self, *args, **kwargs)

    with patch.object(Image.Image, "save", counting_save):
        asyncio.run(generate_one_layer(
            layer=_layer(), anchor=_anchor(),
            canvas=CanvasSpec(color=(255, 255, 255)),
            keying=LuminanceKeying(),
            provider=_Prov(png),
            sibling_roles=["layer1"],
            output_dir=str(tmp_path),
            cache=cache,
            width=32, height=32,
        ))

    assert len(save_calls) == 1, f"expected 1 save call, got {len(save_calls)}"


def test_cache_round_trip_byte_equivalent(tmp_path: Path):
    """After fresh generate, cached bytes equal disk bytes."""
    cache = LayerCache(tmp_path)
    png = _png_bytes()
    asyncio.run(generate_one_layer(
        layer=_layer(), anchor=_anchor(),
        canvas=CanvasSpec(color=(255, 255, 255)),
        keying=LuminanceKeying(),
        provider=_Prov(png),
        sibling_roles=["layer1"],
        output_dir=str(tmp_path),
        cache=cache,
        width=32, height=32,
    ))

    out_path = tmp_path / "layer1.png"
    assert out_path.exists()
    disk_bytes = out_path.read_bytes()

    cache_dir = tmp_path / ".layered_cache"
    cached_pngs = list(cache_dir.glob("*.png"))
    assert len(cached_pngs) == 1
    cached_bytes = cached_pngs[0].read_bytes()

    assert disk_bytes == cached_bytes
