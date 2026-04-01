"""Tests for LayerGenerateNode — per-layer generation with style consistency."""
import pytest
from vulca.pipeline.node import NodeContext
from vulca.pipeline.nodes.layer_generate import LayerGenerateNode
from vulca.layers.types import LayerInfo, LayerResult


def _make_layers():
    return [
        LayerInfo(name="bg", description="Background", z_index=0, content_type="background"),
        LayerInfo(name="subject", description="Subject", z_index=1, content_type="subject"),
        LayerInfo(name="text", description="Text overlay", z_index=2, content_type="text"),
    ]


def _make_ctx(layers, **overrides):
    ctx = NodeContext(intent="水墨山水", tradition="chinese_xieyi", provider="mock")
    ctx.set("planned_layers", layers)
    for k, v in overrides.items():
        ctx.set(k, v)
    return ctx


class TestLayerGenerateNode:
    @pytest.mark.asyncio
    async def test_generates_all_layers_round1(self):
        node = LayerGenerateNode()
        layers = _make_layers()
        ctx = _make_ctx(layers)
        ctx.round_num = 1
        result = await node.run(ctx)
        assert result["layers_generated"] == 3
        assert result["layers_kept"] == 0
        assert len(result["layer_results"]) == 3
        assert all(isinstance(r, LayerResult) for r in result["layer_results"])

    @pytest.mark.asyncio
    async def test_selective_rerun_round2(self):
        node = LayerGenerateNode()
        layers = _make_layers()
        prev_results = [
            LayerResult(info=layers[0], image_path="/tmp/bg.png"),
            LayerResult(info=layers[1], image_path="/tmp/subject.png"),
            LayerResult(info=layers[2], image_path="/tmp/text.png"),
        ]
        ctx = _make_ctx(layers,
            layer_results=prev_results,
            layer_decisions={"bg": "accept", "subject": "rerun", "text": "accept"},
        )
        ctx.round_num = 2
        result = await node.run(ctx)
        assert result["layers_generated"] == 1
        assert result["layers_kept"] == 2
        assert len(result["layer_results"]) == 3

    @pytest.mark.asyncio
    async def test_results_sorted_by_z_index(self):
        node = LayerGenerateNode()
        layers = _make_layers()
        ctx = _make_ctx(layers)
        ctx.round_num = 1
        result = await node.run(ctx)
        z_indices = [r.info.z_index for r in result["layer_results"]]
        assert z_indices == sorted(z_indices)
