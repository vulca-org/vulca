import asyncio
import base64
import io

from PIL import Image

from vulca.layers.keying import CanvasSpec
from vulca.layers.layered_generate import LayeredResult, layered_generate
from vulca.layers.layered_prompt import TraditionAnchor
from vulca.layers.types import LayerInfo


class _CountingProvider:
    def __init__(self, fail_for_role=None):
        self.calls = 0
        self.id = "fake"
        self.model = "fake-1"
        self.fail_for_role = fail_for_role

    async def generate(self, *, prompt, raw_prompt=False, **kw):
        self.calls += 1
        if self.fail_for_role and self.fail_for_role in prompt:
            raise RuntimeError("simulated failure")
        img = Image.new("RGB", (32, 32), (255, 255, 255))
        for y in range(8, 24):
            for x in range(8, 24):
                img.putpixel((x, y), (40, 40, 40))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return type("R", (), {"image_b64": base64.b64encode(buf.getvalue()).decode()})()


def _plan():
    return [
        LayerInfo(name="bg", description="paper", z_index=0, content_type="background", tradition_role="纸"),
        LayerInfo(name="far", description="far mountains", z_index=1, content_type="subject", tradition_role="远景淡墨", regeneration_prompt="distant mountains"),
        LayerInfo(name="mid", description="mid scenery", z_index=2, content_type="subject", tradition_role="中景", regeneration_prompt="mid scenery"),
    ]


def _anchor():
    return TraditionAnchor("#ffffff", "white rice paper", "水墨")


def test_layered_generate_all_succeed(tmp_path):
    provider = _CountingProvider()
    res = asyncio.run(layered_generate(
        plan=_plan(),
        tradition_anchor=_anchor(),
        canvas=CanvasSpec.from_hex("#ffffff"),
        key_strategy_name="luminance",
        provider=provider,
        output_dir=str(tmp_path),
        positions={"bg": "full canvas", "far": "upper 30%", "mid": "center"},
        coverages={"bg": "100%", "far": "20-30%", "mid": "20-30%"},
        parallelism=2,
    ))
    assert isinstance(res, LayeredResult)
    assert res.is_complete
    assert len(res.layers) == 3
    assert provider.calls == 3


def test_layered_generate_partial_failure(tmp_path):
    # Match the mid layer's USER INTENT (regeneration_prompt) — sibling exclusion
    # lists include "中景" in every other layer's prompt, so we need a string that
    # only appears in the mid layer's own prompt.
    provider = _CountingProvider(fail_for_role="mid scenery")
    res = asyncio.run(layered_generate(
        plan=_plan(),
        tradition_anchor=_anchor(),
        canvas=CanvasSpec.from_hex("#ffffff"),
        key_strategy_name="luminance",
        provider=provider,
        output_dir=str(tmp_path),
        positions={"bg": "full canvas", "far": "upper 30%", "mid": "center"},
        coverages={"bg": "100%", "far": "20-30%", "mid": "20-30%"},
        parallelism=2,
    ))
    assert not res.is_complete
    assert res.is_usable
    assert len(res.failed) == 1
    assert res.failed[0].role == "中景"


def test_cache_hit_on_second_run(tmp_path):
    provider = _CountingProvider()
    args = dict(
        plan=_plan(),
        tradition_anchor=_anchor(),
        canvas=CanvasSpec.from_hex("#ffffff"),
        key_strategy_name="luminance",
        provider=provider,
        output_dir=str(tmp_path),
        positions={"bg": "full canvas", "far": "upper 30%", "mid": "center"},
        coverages={"bg": "100%", "far": "20-30%", "mid": "20-30%"},
        parallelism=2,
        cache_enabled=True,
    )
    asyncio.run(layered_generate(**args))
    assert provider.calls == 3
    asyncio.run(layered_generate(**args))
    assert provider.calls == 3
