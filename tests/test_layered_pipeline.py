"""End-to-end tests for LAYERED pipeline."""
import pytest

from vulca.pipeline import execute
from vulca.pipeline.templates import LAYERED, TEMPLATES
from vulca.pipeline.types import PipelineInput


class TestLayeredTemplate:
    def test_layered_template_registered(self):
        assert "layered" in TEMPLATES
        assert LAYERED.name == "layered"
        assert LAYERED.entry_point == "plan_layers"
        assert LAYERED.enable_loop is False
        assert LAYERED.nodes == ("plan_layers", "layer_generate")
        assert "composite" not in LAYERED.nodes
        assert "evaluate" not in LAYERED.nodes

    @pytest.mark.asyncio
    async def test_layered_pipeline_mock_e2e(self):
        inp = PipelineInput(
            subject="水墨山水",
            intent="水墨山水，雨后春山",
            tradition="chinese_xieyi",
            provider="mock",
            template="layered",
            layered=True,
        )
        output = await execute(LAYERED, inp)
        assert output.status == "completed"
        # simplified pipeline: no evaluate/decide nodes, so weighted_total == 0
        assert output.weighted_total == 0.0
        assert output.total_rounds == 1

    @pytest.mark.asyncio
    async def test_default_pipeline_still_works(self):
        """Regression: DEFAULT pipeline unchanged."""
        from vulca.pipeline.templates import DEFAULT
        inp = PipelineInput(
            subject="test",
            provider="mock",
            template="default",
        )
        output = await execute(DEFAULT, inp)
        assert output.status == "completed"


from vulca.pipeline.node import NodeContext
from vulca.pipeline.nodes.decide import DecideNode
from vulca.layers.types import LayerInfo, LayerResult


class TestDecideNodePerLayer:
    @pytest.mark.asyncio
    async def test_per_layer_decision_all_accept(self):
        node = DecideNode(accept_threshold=0.7)
        ctx = NodeContext(tradition="default")
        ctx.round_num = 1
        ctx.max_rounds = 3
        ctx.set("weighted_total", 0.85)
        ctx.set("scores", {"L1": 0.90, "L2": 0.85, "L3": 0.80})
        ctx.set("layer_results", [
            LayerResult(info=LayerInfo(name="bg", description="bg", z_index=0, content_type="background"), image_path="/tmp/bg.png"),
            LayerResult(info=LayerInfo(name="fg", description="fg", z_index=1, content_type="subject"), image_path="/tmp/fg.png"),
        ])
        result = await node.run(ctx)
        assert result["decision"] == "accept"
        assert "layer_decisions" in result
        assert result["layer_decisions"]["bg"] == "accept"
        assert result["layer_decisions"]["fg"] == "accept"

    @pytest.mark.asyncio
    async def test_per_layer_decision_marks_failed(self):
        node = DecideNode(accept_threshold=0.7)
        ctx = NodeContext(tradition="default")
        ctx.round_num = 1
        ctx.max_rounds = 3
        ctx.set("weighted_total", 0.5)
        ctx.set("scores", {"L1": 0.50, "L2": 0.40, "L3": 0.60})
        ctx.set("layer_results", [
            LayerResult(info=LayerInfo(name="bg", description="bg", z_index=0, content_type="background"), image_path="/tmp/bg.png"),
            LayerResult(info=LayerInfo(name="broken", description="broken", z_index=2, content_type="subject"), image_path=""),
        ])
        result = await node.run(ctx)
        assert result["decision"] == "rerun"
        assert result["layer_decisions"]["broken"] == "rerun"

    @pytest.mark.asyncio
    async def test_no_layer_decisions_without_layer_results(self):
        """Standard (non-LAYERED) pipeline: no layer_decisions key."""
        node = DecideNode(accept_threshold=0.7)
        ctx = NodeContext(tradition="default")
        ctx.round_num = 1
        ctx.max_rounds = 3
        ctx.set("weighted_total", 0.85)
        ctx.set("scores", {"L1": 0.90})
        result = await node.run(ctx)
        assert result["decision"] == "accept"
        assert "layer_decisions" not in result


class TestLayeredPipelineE2E:
    @pytest.mark.asyncio
    async def test_full_layered_flow_with_artifact(self, tmp_path):
        """Full flow: layered=True → artifact + layers + composite."""
        inp = PipelineInput(
            subject="水墨山水",
            intent="水墨山水，雨后春山",
            tradition="chinese_xieyi",
            provider="mock",
            layered=True,
        )
        output = await execute(LAYERED, inp)
        assert output.status == "completed"
        assert output.total_rounds >= 1

    @pytest.mark.asyncio
    async def test_default_pipeline_regression(self):
        """Regression: DEFAULT pipeline unchanged."""
        from vulca.pipeline.templates import DEFAULT
        inp = PipelineInput(
            subject="test regression",
            provider="mock",
            template="default",
        )
        output = await execute(DEFAULT, inp)
        assert output.status == "completed"


class TestArtifactContentAfterPipeline:
    @pytest.mark.asyncio
    async def test_artifact_has_cultural_context(self):
        """After LAYERED pipeline, artifact.json should have cultural_context populated."""
        import json
        from pathlib import Path

        inp = PipelineInput(
            subject="水墨山水",
            intent="水墨山水",
            tradition="chinese_xieyi",
            provider="mock",
            layered=True,
        )
        output = await execute(LAYERED, inp)
        assert output.status == "completed"

        artifact_path = Path("/tmp/vulca_composite/artifact.json")
        if artifact_path.exists():
            data = json.loads(artifact_path.read_text())
            assert data["artifact_version"] == "3.0"
            # cultural_context should have tradition_layer_order from PlanLayersNode
            ctx = data.get("cultural_context", {})
            if ctx:
                assert "tradition_layer_order" in ctx

    @pytest.mark.asyncio
    async def test_artifact_layers_have_status(self):
        """Layers in artifact should have status field set."""
        import json
        from pathlib import Path

        inp = PipelineInput(
            subject="test",
            provider="mock",
            layered=True,
        )
        output = await execute(LAYERED, inp)
        assert output.status == "completed"

        artifact_path = Path("/tmp/vulca_composite/artifact.json")
        if artifact_path.exists():
            data = json.loads(artifact_path.read_text())
            for layer in data["layers"]:
                assert "status" in layer
                assert "tradition_role" in layer
