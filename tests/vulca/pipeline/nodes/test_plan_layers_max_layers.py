"""Phase 0 Task 0 rework: plan_layers must respect ctx.max_layers up to 20."""
import asyncio
from unittest.mock import AsyncMock

import pytest
from PIL import Image

from vulca.layers.types import LayerInfo
from vulca.pipeline.node import NodeContext
from vulca.pipeline.nodes.plan_layers import PlanLayersNode


def _make_layers(n: int) -> list[LayerInfo]:
    return [
        LayerInfo(name=f"l{i}", description="", z_index=i, content_type="subject")
        for i in range(n)
    ]


def _run(ctx: NodeContext) -> dict:
    return asyncio.run(PlanLayersNode().run(ctx))


def test_plan_layers_keeps_12_when_max_layers_is_20():
    ctx = NodeContext(subject="x", tradition="default")
    ctx.set("max_layers", 20)
    ctx.set("planned_layers", _make_layers(12))
    out = _run(ctx)
    assert out["layer_count"] == 12


def test_plan_layers_keeps_20_when_max_layers_is_20():
    ctx = NodeContext(subject="x", tradition="default")
    ctx.set("max_layers", 20)
    ctx.set("planned_layers", _make_layers(20))
    out = _run(ctx)
    assert out["layer_count"] == 20


def test_plan_layers_clamps_above_max_layers():
    ctx = NodeContext(subject="x", tradition="default")
    ctx.set("max_layers", 12)
    ctx.set("planned_layers", _make_layers(18))
    out = _run(ctx)
    assert out["layer_count"] == 12


def test_plan_layers_defaults_to_legacy_cap_when_unset():
    """If ctx has no max_layers (old callers), keep legacy default of 10."""
    ctx = NodeContext(subject="x", tradition="default")
    ctx.set("planned_layers", _make_layers(15))
    out = _run(ctx)
    assert out["layer_count"] == 10


def test_plan_layers_existing_source_mock_provider_skips_litellm(tmp_path, monkeypatch):
    source = tmp_path / "source.png"
    Image.new("RGB", (6, 4), (120, 160, 200)).save(source)

    import vulca.layers.analyze as analyze_mod

    monkeypatch.setattr(
        analyze_mod.litellm,
        "acompletion",
        AsyncMock(side_effect=AssertionError("mock provider called LiteLLM")),
    )

    ctx = NodeContext(subject="x", tradition="default", provider="mock")
    ctx.set("source_image_b64", "AAAA")
    ctx.set("source_image_path", str(source))

    out = _run(ctx)

    assert out["layer_count"] == 2
    assert [layer.name for layer in out["planned_layers"]] == ["background", "foreground"]
