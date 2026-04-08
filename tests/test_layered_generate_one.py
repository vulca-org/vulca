import asyncio
import base64
import io
from pathlib import Path

import numpy as np
from PIL import Image

from vulca.layers.keying import CanvasSpec
from vulca.layers.keying.luminance import LuminanceKeying
from vulca.layers.layered_cache import LayerCache
from vulca.layers.layered_generate import LayerOutcome, generate_one_layer
from vulca.layers.layered_prompt import TraditionAnchor
from vulca.layers.types import LayerInfo


class _FakeProvider:
    def __init__(self):
        self.calls = 0
        self.id = "fake"
        self.model = "fake-1"

    async def generate(self, *, prompt, raw_prompt=False, reference_image_b64=None, **kw):
        self.calls += 1
        img = Image.new("RGB", (32, 32), (255, 255, 255))
        for y in range(8, 24):
            for x in range(8, 24):
                img.putpixel((x, y), (40, 40, 40))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return type("R", (), {"image_b64": base64.b64encode(buf.getvalue()).decode()})()


def _layer():
    return LayerInfo(
        name="远山",
        description="distant ink mountains",
        z_index=1,
        content_type="subject",
        tradition_role="远景淡墨",
        regeneration_prompt="distant misty mountains in light ink",
    )


def _anchor():
    return TraditionAnchor(
        canvas_color_hex="#ffffff",
        canvas_description="pure white rice paper",
        style_keywords="水墨, 飞白",
    )


def test_generate_one_layer_produces_rgba(tmp_path):
    provider = _FakeProvider()
    cache = LayerCache(tmp_path, enabled=True)
    out = asyncio.run(generate_one_layer(
        layer=_layer(),
        anchor=_anchor(),
        canvas=CanvasSpec.from_hex("#ffffff"),
        keying=LuminanceKeying(),
        provider=provider,
        sibling_roles=["中景", "题款"],
        output_dir=str(tmp_path),
        position="center",
        coverage="20-30%",
        cache=cache,
    ))
    assert isinstance(out, LayerOutcome)
    assert out.ok
    assert Path(out.rgba_path).exists()
    img = Image.open(out.rgba_path)
    assert img.mode == "RGBA"
    a = np.array(img)[:, :, 3]
    assert a[16, 16] > 200
    assert a[0, 0] < 30


def test_cache_hit_skips_provider(tmp_path):
    provider = _FakeProvider()
    cache = LayerCache(tmp_path, enabled=True)
    layer = _layer()
    asyncio.run(generate_one_layer(
        layer=layer, anchor=_anchor(), canvas=CanvasSpec.from_hex("#ffffff"),
        keying=LuminanceKeying(), provider=provider, sibling_roles=[],
        output_dir=str(tmp_path), position="center", coverage="20-30%", cache=cache,
    ))
    assert provider.calls == 1
    out = asyncio.run(generate_one_layer(
        layer=layer, anchor=_anchor(), canvas=CanvasSpec.from_hex("#ffffff"),
        keying=LuminanceKeying(), provider=provider, sibling_roles=[],
        output_dir=str(tmp_path), position="center", coverage="20-30%", cache=cache,
    ))
    assert provider.calls == 1
    assert out.cache_hit
