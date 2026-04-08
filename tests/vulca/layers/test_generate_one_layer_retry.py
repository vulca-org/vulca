"""v0.13.2 P2: generate_one_layer in-process retry budget=2 for
provider exceptions (generation_failed only)."""
from __future__ import annotations

import asyncio
import base64
import io
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image

from vulca.layers.keying import CanvasSpec
from vulca.layers.keying.luminance import LuminanceKeying
from vulca.layers.layered_generate import generate_one_layer
from vulca.layers.layered_prompt import TraditionAnchor
from vulca.layers.types import LayerInfo
from vulca.layers.validate import ValidationReport


def _png_bytes(w=32, h=32, color=(200, 200, 200)) -> bytes:
    img = Image.new("RGB", (w, h), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _layer() -> LayerInfo:
    return LayerInfo(
        name="layer1",
        description="test layer",
        z_index=0,
        content_type="subject",
    )


def _anchor() -> TraditionAnchor:
    return TraditionAnchor(
        canvas_color_hex="#ffffff",
        canvas_description="white paper",
        style_keywords="test",
    )


class _Result:
    def __init__(self, b: bytes):
        self.image_b64 = base64.b64encode(b).decode()


class _FakeProvider:
    """Generates predetermined sequence of either bytes or exceptions."""
    id = "fake"
    model = "fake-v1"

    def __init__(self, side_effects):
        self._effects = list(side_effects)
        self.calls = 0

    async def generate(self, *, prompt, raw_prompt=False, **kwargs):
        self.calls += 1
        effect = self._effects.pop(0)
        if isinstance(effect, BaseException):
            raise effect
        return _Result(effect)


def _kwargs(prov, tmp_path: Path) -> dict:
    return dict(
        layer=_layer(), anchor=_anchor(),
        canvas=CanvasSpec(color=(255, 255, 255)),
        keying=LuminanceKeying(),
        provider=prov,
        sibling_roles=["layer1"],
        output_dir=str(tmp_path),
        width=32, height=32,
    )


def test_transient_failure_succeeds_on_second_attempt(tmp_path: Path):
    prov = _FakeProvider([RuntimeError("transient"), _png_bytes()])
    with patch("vulca.layers.layered_generate.asyncio.sleep", new=AsyncMock()):
        outcome = asyncio.run(generate_one_layer(**_kwargs(prov, tmp_path)))
    assert prov.calls == 2
    assert outcome.attempts == 2
    assert outcome.ok is True


def test_persistent_failure_exhausts_three_attempts(tmp_path: Path):
    prov = _FakeProvider([
        RuntimeError("1"), RuntimeError("2"), RuntimeError("3"),
    ])
    with patch("vulca.layers.layered_generate.asyncio.sleep", new=AsyncMock()):
        outcome = asyncio.run(generate_one_layer(**_kwargs(prov, tmp_path)))
    assert prov.calls == 3  # 1 initial + 2 retries
    assert outcome.attempts == 3
    assert outcome.ok is False


def test_validation_failure_is_not_retried(tmp_path: Path):
    bad = ValidationReport(ok=False)
    prov = _FakeProvider([_png_bytes(), _png_bytes(), _png_bytes()])
    with patch(
        "vulca.layers.layered_generate.validate_layer_alpha",
        return_value=bad,
    ), patch("vulca.layers.layered_generate.asyncio.sleep", new=AsyncMock()):
        outcome = asyncio.run(generate_one_layer(**_kwargs(prov, tmp_path)))
    assert prov.calls == 1
    assert outcome.attempts == 1
    assert outcome.ok is False
    assert outcome.validation is not None


def test_assertion_error_in_provider_propagates(tmp_path: Path):
    """Programmer bugs (AssertionError) inside provider must NOT be retried."""
    prov = _FakeProvider([AssertionError("programmer bug"), _png_bytes()])
    with patch("vulca.layers.layered_generate.asyncio.sleep", new=AsyncMock()):
        with pytest.raises(AssertionError, match="programmer bug"):
            asyncio.run(generate_one_layer(**_kwargs(prov, tmp_path)))
    assert prov.calls == 1  # not retried


def test_type_error_in_provider_propagates(tmp_path: Path):
    """TypeError = programmer bug. Must propagate, not retry."""
    prov = _FakeProvider([TypeError("bad arg"), _png_bytes()])
    with patch("vulca.layers.layered_generate.asyncio.sleep", new=AsyncMock()):
        with pytest.raises(TypeError):
            asyncio.run(generate_one_layer(**_kwargs(prov, tmp_path)))
    assert prov.calls == 1


def test_cancelled_error_in_provider_propagates(tmp_path: Path):
    """asyncio.CancelledError is control flow — must NOT be retried."""
    prov = _FakeProvider([asyncio.CancelledError(), _png_bytes()])
    with patch("vulca.layers.layered_generate.asyncio.sleep", new=AsyncMock()):
        with pytest.raises((asyncio.CancelledError, BaseException)):
            asyncio.run(generate_one_layer(**_kwargs(prov, tmp_path)))
    assert prov.calls == 1


def test_full_jitter_backoff(tmp_path: Path):
    """Backoff: random.uniform(0, 0.5 * 2**attempt). attempt=0 -> [0, 0.5);
    attempt=1 -> [0, 1.0). Two retries -> two sleeps with bounds 0.5 then 1.0."""
    prov = _FakeProvider([RuntimeError("1"), RuntimeError("2"), _png_bytes()])
    sleeps: list[float] = []

    async def _record_sleep(seconds):
        sleeps.append(seconds)

    with patch("vulca.layers.layered_generate.random.uniform",
               side_effect=lambda a, b: b * 0.7) as mock_uniform, \
         patch("vulca.layers.layered_generate.asyncio.sleep",
               side_effect=_record_sleep):
        asyncio.run(generate_one_layer(**_kwargs(prov, tmp_path)))

    assert len(sleeps) == 2
    assert sleeps[0] == pytest.approx(0.5 * 0.7)
    assert sleeps[1] == pytest.approx(1.0 * 0.7)
    upper_bounds = [c.args[1] for c in mock_uniform.call_args_list]
    assert upper_bounds == [pytest.approx(0.5), pytest.approx(1.0)]
