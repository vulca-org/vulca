"""v0.13.2 P2: _apply_alpha must assert shape match, not silently resize."""
from __future__ import annotations

import io

import numpy as np
import pytest
from PIL import Image

from vulca.layers.layered_generate import _apply_alpha


def _png_bytes(w: int, h: int) -> bytes:
    img = Image.new("RGB", (w, h), (128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_apply_alpha_matching_shape_ok():
    rgb = _png_bytes(8, 8)
    alpha = np.ones((8, 8), dtype=np.float32)
    out = _apply_alpha(rgb, alpha)
    assert out.size == (8, 8)
    assert out.mode == "RGBA"


def test_apply_alpha_shape_mismatch_raises():
    rgb = _png_bytes(8, 8)
    alpha = np.ones((4, 4), dtype=np.float32)
    with pytest.raises(AssertionError, match="alpha shape"):
        _apply_alpha(rgb, alpha)


def test_assertion_propagates_through_orchestration(tmp_path, monkeypatch):
    """AssertionError from _apply_alpha must NOT be swallowed by _run's
    blanket except. Programmer bugs should surface loudly."""
    import asyncio
    import base64
    import io as _io

    from PIL import Image as _Image

    from vulca.layers import layered_generate as lg
    from vulca.layers.keying import CanvasSpec
    from vulca.layers.layered_prompt import TraditionAnchor
    from vulca.layers.types import LayerInfo

    class _BadKeying:
        def extract_alpha(self, rgb, canvas):
            # Deliberately wrong shape — triggers the _apply_alpha assert.
            return np.ones((4, 4), dtype=np.float32)

    class _FakeProvider:
        id = "fake"
        model = "fake-1"

        async def generate(self, *, prompt, raw_prompt=False, **kw):
            img = _Image.new("RGB", (32, 32), (200, 200, 200))
            buf = _io.BytesIO()
            img.save(buf, format="PNG")
            return type("R", (), {"image_b64": base64.b64encode(buf.getvalue()).decode()})()

    monkeypatch.setattr(lg, "get_keying_strategy", lambda _name: _BadKeying())

    plan = [
        LayerInfo(
            name="bg",
            description="paper",
            z_index=0,
            content_type="background",
            tradition_role="纸",
        ),
    ]
    anchor = TraditionAnchor("#ffffff", "white rice paper", "水墨")

    with pytest.raises(AssertionError, match="alpha shape"):
        asyncio.run(
            lg.layered_generate(
                plan=plan,
                tradition_anchor=anchor,
                canvas=CanvasSpec.from_hex("#ffffff"),
                key_strategy_name="luminance",
                provider=_FakeProvider(),
                output_dir=str(tmp_path),
                positions={"bg": "full canvas"},
                coverages={"bg": "100%"},
                parallelism=1,
                cache_enabled=False,
            )
        )
