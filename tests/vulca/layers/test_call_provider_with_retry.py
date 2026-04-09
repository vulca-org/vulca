"""Tests for the extracted _call_provider_with_retry helper."""
from __future__ import annotations

import asyncio
import base64
import io
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image


def _png_bytes(w=32, h=32, color=(200, 200, 200)) -> bytes:
    img = Image.new("RGB", (w, h), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


class _Result:
    def __init__(self, b: bytes):
        self.image_b64 = base64.b64encode(b).decode()


class _FakeProvider:
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


def test_success_on_first_attempt():
    from vulca.layers.layered_generate import _call_provider_with_retry
    prov = _FakeProvider([_png_bytes()])
    with patch("vulca.layers.layered_generate.asyncio.sleep", new=AsyncMock()):
        rgb_bytes, attempts = asyncio.run(
            _call_provider_with_retry(prov, "test prompt", "layer1")
        )
    assert isinstance(rgb_bytes, bytes)
    assert attempts == 1
    assert prov.calls == 1


def test_success_on_second_attempt():
    from vulca.layers.layered_generate import _call_provider_with_retry
    prov = _FakeProvider([RuntimeError("transient"), _png_bytes()])
    with patch("vulca.layers.layered_generate.asyncio.sleep", new=AsyncMock()):
        rgb_bytes, attempts = asyncio.run(
            _call_provider_with_retry(prov, "test prompt", "layer1")
        )
    assert isinstance(rgb_bytes, bytes)
    assert attempts == 2
    assert prov.calls == 2


def test_exhausted_budget_raises():
    from vulca.layers.layered_generate import _call_provider_with_retry
    prov = _FakeProvider([
        RuntimeError("1"), RuntimeError("2"), RuntimeError("3"),
    ])
    with patch("vulca.layers.layered_generate.asyncio.sleep", new=AsyncMock()):
        with pytest.raises(RuntimeError, match="3"):
            asyncio.run(
                _call_provider_with_retry(prov, "test prompt", "layer1")
            )
    assert prov.calls == 3


def test_assertion_error_propagates_without_retry():
    from vulca.layers.layered_generate import _call_provider_with_retry
    prov = _FakeProvider([AssertionError("bug"), _png_bytes()])
    with patch("vulca.layers.layered_generate.asyncio.sleep", new=AsyncMock()):
        with pytest.raises(AssertionError, match="bug"):
            asyncio.run(
                _call_provider_with_retry(prov, "test prompt", "layer1")
            )
    assert prov.calls == 1


def test_type_error_propagates_without_retry():
    from vulca.layers.layered_generate import _call_provider_with_retry
    prov = _FakeProvider([TypeError("bad arg"), _png_bytes()])
    with patch("vulca.layers.layered_generate.asyncio.sleep", new=AsyncMock()):
        with pytest.raises(TypeError):
            asyncio.run(
                _call_provider_with_retry(prov, "test prompt", "layer1")
            )
    assert prov.calls == 1


def test_cancelled_error_propagates_without_retry():
    from vulca.layers.layered_generate import _call_provider_with_retry
    prov = _FakeProvider([asyncio.CancelledError(), _png_bytes()])
    with patch("vulca.layers.layered_generate.asyncio.sleep", new=AsyncMock()):
        with pytest.raises(asyncio.CancelledError):
            asyncio.run(
                _call_provider_with_retry(prov, "test prompt", "layer1")
            )
    assert prov.calls == 1
