"""v0.14 Defense 3: style reference and cross-layer consistency tests."""
import asyncio
import base64
import io

import numpy as np
from PIL import Image

from vulca.layers.keying import CanvasSpec
from vulca.layers.keying.luminance import LuminanceKeying
from vulca.layers.layered_cache import LayerCache
from vulca.layers.layered_generate import LayerOutcome, generate_one_layer, layered_generate
from vulca.layers.layered_prompt import TraditionAnchor
from vulca.layers.types import LayerInfo


def _make_rgb_png(color=(255, 255, 255), subject_color=(40, 40, 40), size=32) -> bytes:
    """Create a test PNG with a subject block on a background."""
    img = Image.new("RGB", (size, size), color)
    for y in range(8, 24):
        for x in range(8, 24):
            img.putpixel((x, y), subject_color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class _RecordingProvider:
    """Provider that records every call's kwargs for assertion."""

    def __init__(self, fail_layers=None):
        self.calls: list[dict] = []
        self.id = "fake"
        self.model = "fake-1"
        self._fail_layers = fail_layers or set()

    async def generate(self, *, prompt, raw_prompt=False, **kw):
        self.calls.append({"prompt": prompt, "raw_prompt": raw_prompt, **kw})
        for name in self._fail_layers:
            if name in prompt:
                raise RuntimeError(f"simulated failure for {name}")
        png_bytes = _make_rgb_png()
        return type("R", (), {"image_b64": base64.b64encode(png_bytes).decode()})()


def _anchor():
    return TraditionAnchor("#ffffff", "white rice paper", "水墨")


def _plan_3():
    return [
        LayerInfo(name="bg", description="paper", z_index=0,
                  content_type="background", tradition_role="纸"),
        LayerInfo(name="far", description="far mountains", z_index=1,
                  content_type="subject", tradition_role="远景淡墨",
                  regeneration_prompt="distant mountains"),
        LayerInfo(name="mid", description="mid scenery", z_index=2,
                  content_type="subject", tradition_role="中景",
                  regeneration_prompt="mid scenery"),
    ]


def _gen_args(tmp_path, provider, plan=None, reference_image_b64=""):
    return dict(
        plan=plan or _plan_3(),
        tradition_anchor=_anchor(),
        canvas=CanvasSpec.from_hex("#ffffff"),
        key_strategy_name="luminance",
        provider=provider,
        output_dir=str(tmp_path),
        positions={"bg": "full canvas", "far": "upper 30%", "mid": "center"},
        coverages={"bg": "100%", "far": "20-30%", "mid": "20-30%"},
        parallelism=2,
        reference_image_b64=reference_image_b64,
    )


def test_raw_rgb_bytes_populated_on_fresh_generation(tmp_path):
    """LayerOutcome.raw_rgb_bytes is populated on fresh generation (not cache hit)."""
    provider = _RecordingProvider()
    cache = LayerCache(tmp_path, enabled=True)
    out = asyncio.run(generate_one_layer(
        layer=LayerInfo(name="test", description="test layer", z_index=0,
                        content_type="subject", tradition_role="test"),
        anchor=_anchor(),
        canvas=CanvasSpec.from_hex("#ffffff"),
        keying=LuminanceKeying(),
        provider=provider,
        sibling_roles=[],
        output_dir=str(tmp_path),
        cache=cache,
    ))
    assert out.ok
    assert out.raw_rgb_bytes is not None
    assert len(out.raw_rgb_bytes) > 0
    # Verify it's valid PNG
    img = Image.open(io.BytesIO(out.raw_rgb_bytes))
    assert img.size[0] > 0
