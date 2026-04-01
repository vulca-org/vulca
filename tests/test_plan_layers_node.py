"""Tests for PlanLayersNode — VLM-based layer structure planning."""
import pytest
from vulca.pipeline.node import NodeContext
from vulca.pipeline.nodes.plan_layers import PlanLayersNode
from vulca.layers.types import LayerInfo


def _make_ctx(**overrides):
    ctx = NodeContext(intent="水墨山水", tradition="chinese_xieyi")
    for k, v in overrides.items():
        ctx.set(k, v)
    return ctx


class TestPlanLayersNode:
    @pytest.mark.asyncio
    async def test_plans_layers_from_intent(self):
        node = PlanLayersNode()
        ctx = _make_ctx()
        ctx.provider = "mock"
        result = await node.run(ctx)
        assert "planned_layers" in result
        layers = result["planned_layers"]
        assert isinstance(layers, list)
        assert len(layers) >= 2
        assert all(isinstance(l, LayerInfo) for l in layers)

    @pytest.mark.asyncio
    async def test_uses_manual_layers_if_provided(self):
        node = PlanLayersNode()
        manual = [
            LayerInfo(name="bg", description="bg", z_index=0),
            LayerInfo(name="fg", description="fg", z_index=1),
        ]
        ctx = _make_ctx(planned_layers=manual)
        result = await node.run(ctx)
        assert result["planned_layers"] == manual
        assert result["layer_count"] == 2

    @pytest.mark.asyncio
    async def test_clamps_excessive_layers(self):
        node = PlanLayersNode()
        too_many = [
            LayerInfo(name=f"l{i}", description=f"l{i}", z_index=i)
            for i in range(12)
        ]
        ctx = _make_ctx(planned_layers=too_many)
        result = await node.run(ctx)
        assert result["layer_count"] <= 10

    @pytest.mark.asyncio
    async def test_pads_single_layer(self):
        node = PlanLayersNode()
        single = [LayerInfo(name="only", description="only", z_index=0)]
        ctx = _make_ctx(planned_layers=single)
        result = await node.run(ctx)
        assert result["layer_count"] >= 2
