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


def test_call_provider_passes_reference():
    """_call_provider passes reference_image_b64 through to provider.generate."""
    from vulca.layers.layered_generate import _call_provider

    provider = _RecordingProvider()
    ref = base64.b64encode(b"fake-ref").decode()
    asyncio.run(_call_provider(provider, "test prompt", reference_image_b64=ref))
    assert len(provider.calls) == 1
    assert provider.calls[0].get("reference_image_b64") == ref


def test_call_provider_no_reference():
    """_call_provider with empty reference still works (backward compat)."""
    from vulca.layers.layered_generate import _call_provider

    provider = _RecordingProvider()
    asyncio.run(_call_provider(provider, "test prompt"))
    assert len(provider.calls) == 1
    assert provider.calls[0].get("reference_image_b64", "") == ""


def test_call_provider_with_retry_passes_reference():
    """reference_image_b64 flows through retry helper to _call_provider."""
    from vulca.layers.layered_generate import _call_provider_with_retry

    provider = _RecordingProvider()
    ref = base64.b64encode(b"fake-ref").decode()
    rgb_bytes, attempts = asyncio.run(
        _call_provider_with_retry(provider, "test prompt", "test_layer",
                                  reference_image_b64=ref)
    )
    assert attempts == 1
    assert len(rgb_bytes) > 0
    assert provider.calls[0].get("reference_image_b64") == ref


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


def test_generate_one_layer_passes_reference(tmp_path):
    """generate_one_layer passes reference_image_b64 through to provider."""
    provider = _RecordingProvider()
    ref = base64.b64encode(_make_rgb_png()).decode()
    out = asyncio.run(generate_one_layer(
        layer=LayerInfo(name="test", description="test", z_index=0,
                        content_type="subject", tradition_role="test"),
        anchor=_anchor(),
        canvas=CanvasSpec.from_hex("#ffffff"),
        keying=LuminanceKeying(),
        provider=provider,
        sibling_roles=[],
        output_dir=str(tmp_path),
        reference_image_b64=ref,
    ))
    assert out.ok
    assert provider.calls[0].get("reference_image_b64") == ref


def test_raw_rgb_bytes_none_on_cache_hit(tmp_path):
    """raw_rgb_bytes is None on cache hit (cache stores keyed RGBA only)."""
    provider = _RecordingProvider()
    cache = LayerCache(tmp_path, enabled=True)
    layer = LayerInfo(name="test", description="test", z_index=0,
                      content_type="subject", tradition_role="test")
    kw = dict(
        layer=layer, anchor=_anchor(), canvas=CanvasSpec.from_hex("#ffffff"),
        keying=LuminanceKeying(), provider=provider, sibling_roles=[],
        output_dir=str(tmp_path), cache=cache,
    )
    out1 = asyncio.run(generate_one_layer(**kw))
    assert out1.raw_rgb_bytes is not None

    out2 = asyncio.run(generate_one_layer(**kw))
    assert out2.cache_hit
    assert out2.raw_rgb_bytes is None


def test_first_layer_serial_then_parallel(tmp_path):
    """plan[0] generates before plan[1:]; plan[1:] runs in parallel."""
    call_order = []

    # Match on USER INTENT content (description/regeneration_prompt) which
    # is unique per layer, unlike tradition_role which leaks into sibling
    # negative lists.
    class _OrderProvider:
        id = "fake"
        model = "fake-1"

        async def generate(self, *, prompt, raw_prompt=False, **kw):
            for tag in ["[USER INTENT]\npaper", "[USER INTENT]\ndistant mountains",
                        "[USER INTENT]\nmid scenery"]:
                if tag in prompt:
                    call_order.append(tag.split("\n")[1])
                    break
            else:
                call_order.append("unknown")
            png_bytes = _make_rgb_png()
            return type("R", (), {"image_b64": base64.b64encode(png_bytes).decode()})()

    provider = _OrderProvider()
    res = asyncio.run(layered_generate(**_gen_args(tmp_path, provider)))
    assert call_order[0] == "paper", f"Expected first call to be bg (paper), got {call_order}"
    assert res.is_complete
    assert len(res.layers) == 3


def test_style_ref_passed_to_remaining_layers(tmp_path):
    """After plan[0] completes, remaining layers receive its output as reference_image_b64."""
    provider = _RecordingProvider()
    res = asyncio.run(layered_generate(**_gen_args(tmp_path, provider)))
    assert res.is_complete
    first_call = provider.calls[0]
    assert first_call.get("reference_image_b64", "") == ""
    for call in provider.calls[1:]:
        ref = call.get("reference_image_b64", "")
        assert ref != "", f"Expected reference for subsequent layer, got empty"
        decoded = base64.b64decode(ref)
        img = Image.open(io.BytesIO(decoded))
        assert img.size[0] > 0


def test_user_reference_passed_to_first_layer(tmp_path):
    """When user provides reference, plan[0] receives it as reference_image_b64."""
    provider = _RecordingProvider()
    user_ref = base64.b64encode(_make_rgb_png(color=(200, 100, 50))).decode()
    res = asyncio.run(layered_generate(
        **_gen_args(tmp_path, provider, reference_image_b64=user_ref)
    ))
    assert res.is_complete
    first_call = provider.calls[0]
    assert first_call.get("reference_image_b64") == user_ref


def test_user_reference_chains_through_first_layer(tmp_path):
    """User ref → plan[0] → plan[0] output → plan[1:] reference (full chain)."""
    provider = _RecordingProvider()
    user_ref = base64.b64encode(_make_rgb_png(color=(200, 100, 50))).decode()
    res = asyncio.run(layered_generate(
        **_gen_args(tmp_path, provider, reference_image_b64=user_ref)
    ))
    assert res.is_complete
    assert provider.calls[0].get("reference_image_b64") == user_ref
    for call in provider.calls[1:]:
        ref = call.get("reference_image_b64", "")
        assert ref != ""
        assert ref != user_ref  # style_ref is first layer's output, not user's original


def test_first_layer_failure_degrades_gracefully(tmp_path):
    """plan[0] fails → remaining layers generate without reference (style_ref = "")."""

    class _FailFirstProvider:
        """Fails the first call, succeeds on subsequent calls."""
        id = "fake"
        model = "fake-1"

        def __init__(self):
            self.calls: list[dict] = []
            self._call_count = 0

        async def generate(self, *, prompt, raw_prompt=False, **kw):
            self.calls.append({"prompt": prompt, "raw_prompt": raw_prompt, **kw})
            self._call_count += 1
            if self._call_count <= 3:  # 3 retries for the first layer
                raise RuntimeError("simulated first-layer failure")
            png_bytes = _make_rgb_png()
            return type("R", (), {"image_b64": base64.b64encode(png_bytes).decode()})()

    provider = _FailFirstProvider()
    res = asyncio.run(layered_generate(**_gen_args(tmp_path, provider)))
    assert len(res.failed) >= 1
    assert any(f.role == "纸" for f in res.failed)
    for call in provider.calls[3:]:  # calls after the first layer's retries
        ref = call.get("reference_image_b64", "")
        assert ref == "", "Expected no reference after first layer failure"


def test_no_user_reference_still_derives_style_ref(tmp_path):
    """No user ref → first layer generates without reference, its output becomes style_ref."""
    provider = _RecordingProvider()
    res = asyncio.run(layered_generate(**_gen_args(tmp_path, provider)))
    assert res.is_complete
    assert provider.calls[0].get("reference_image_b64", "") == ""
    for call in provider.calls[1:]:
        assert call.get("reference_image_b64", "") != ""


def test_single_layer_plan_no_gather(tmp_path):
    """Single-layer plan generates directly, no style_ref derivation needed."""
    provider = _RecordingProvider()
    single = [LayerInfo(name="bg", description="paper", z_index=0,
                        content_type="background", tradition_role="纸")]
    res = asyncio.run(layered_generate(
        **_gen_args(tmp_path, provider, plan=single)
    ))
    assert res.is_complete
    assert len(res.layers) == 1
    assert len(provider.calls) == 1


def test_style_ref_uses_raw_rgb_not_keyed_rgba(tmp_path):
    """style_ref is derived from raw RGB bytes, not the keyed RGBA output."""
    provider = _RecordingProvider()
    res = asyncio.run(layered_generate(**_gen_args(tmp_path, provider)))
    assert res.is_complete
    ref_b64 = provider.calls[1].get("reference_image_b64", "")
    assert ref_b64 != ""
    ref_bytes = base64.b64decode(ref_b64)
    ref_img = Image.open(io.BytesIO(ref_bytes))
    assert ref_img.mode == "RGB", f"Expected RGB style_ref, got {ref_img.mode}"
