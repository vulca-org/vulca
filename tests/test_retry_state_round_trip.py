"""P0.2 + P0.3 — retry must round-trip spatial anchor + canvas dimensions.

Codex review found two retry-state-loss bugs in v0.13.0:

P0.2: `retry_layers` never passed position/coverage back into
`layered_generate`, because `LayerInfo` carried those as dunder-private
attrs (`_position`, `_coverage`) instead of first-class fields. After
`load_manifest` the info objects lost the attrs entirely, so retry ran
with the weaker default spatial block in `layered_prompt.py` AND got a
different cache key than the original run.

P0.3: `retry_layers` never threaded `manifest["width"]`/`height"]` into
`layered_generate`, so non-default-size artifacts silently retried with
0x0 cache keys and wrong output dimensions.

These tests spy on the layered_generate call to assert every retry
preserves both the spatial anchoring AND the canvas dimensions.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from vulca.layers.manifest import write_manifest
from vulca.layers.retry import retry_layers
from vulca.layers.types import LayerInfo


def _write_artifact(tmp_path: Path, *, width: int, height: int,
                    position: str, coverage: str) -> Path:
    adir = tmp_path / "art"
    adir.mkdir()
    layers = [LayerInfo(
        name="mist", description="distant mist", z_index=0,
        content_type="atmosphere", position=position, coverage=coverage,
    )]
    write_manifest(
        layers, output_dir=str(adir), width=width, height=height,
        generation_path="a", layerability="native", partial=True,
        layer_extras={layers[0].id: {"source": "a", "status": "failed",
                                      "reason": "generation_failed"}},
    )
    return adir


def test_retry_threads_canvas_dimensions_from_manifest(tmp_path, monkeypatch):
    """P0.3: non-default-size artifacts must retry at the manifest's
    width/height, not the layered_generate default of 0×0."""
    adir = _write_artifact(tmp_path, width=768, height=1024,
                           position="upper third", coverage="20%")

    captured: list[dict] = []

    async def fake_layered_generate(**kwargs):
        captured.append(kwargs)
        from vulca.layers.layered_generate import LayeredResult
        return LayeredResult(layers=[], failed=[])

    from vulca.layers import retry as retry_mod
    monkeypatch.setattr(retry_mod, "layered_generate", fake_layered_generate)

    asyncio.run(retry_layers(
        str(adir), tradition_name="chinese_xieyi", all_failed=True,
        provider=AsyncMock(),
    ))

    assert captured, "layered_generate was not called"
    call = captured[0]
    assert call["width"] == 768, f"expected width=768, got {call.get('width')}"
    assert call["height"] == 1024, f"expected height=1024, got {call.get('height')}"


def test_retry_threads_position_and_coverage_from_manifest(tmp_path, monkeypatch):
    """P0.2: retry must preserve each layer's position/coverage so the
    anchored prompt builder produces the same prompt (and the same cache
    key) as the original run."""
    adir = _write_artifact(tmp_path, width=1024, height=1024,
                           position="upper portion, background",
                           coverage="15-25%")

    captured: list[dict] = []

    async def fake_layered_generate(**kwargs):
        captured.append(kwargs)
        from vulca.layers.layered_generate import LayeredResult
        return LayeredResult(layers=[], failed=[])

    from vulca.layers import retry as retry_mod
    monkeypatch.setattr(retry_mod, "layered_generate", fake_layered_generate)

    asyncio.run(retry_layers(
        str(adir), tradition_name="chinese_xieyi", all_failed=True,
        provider=AsyncMock(),
    ))

    call = captured[0]
    positions = call.get("positions") or {}
    coverages = call.get("coverages") or {}
    assert positions.get("mist") == "upper portion, background", (
        f"expected position to round-trip from manifest, got {positions!r}"
    )
    assert coverages.get("mist") == "15-25%", (
        f"expected coverage to round-trip from manifest, got {coverages!r}"
    )
