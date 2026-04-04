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


class TestPromptPositionInjection:
    def test_prompt_includes_position_fallback_for_text(self):
        node = LayerGenerateNode()
        info = LayerInfo(name="calligraphy", description="Calligraphy text", z_index=4, content_type="text")
        ctx = NodeContext(intent="test", tradition="chinese_xieyi", provider="mock")
        ctx.set("planned_layers", [info])
        prompt = node._build_prompt(info, ctx)
        assert "corner" in prompt.lower() or "5-10%" in prompt or "small" in prompt.lower()

    def test_prompt_includes_position_fallback_for_atmosphere(self):
        node = LayerGenerateNode()
        info = LayerInfo(name="mountains", description="Distant mountains", z_index=1, content_type="atmosphere")
        ctx = NodeContext(intent="test", tradition="chinese_xieyi", provider="mock")
        ctx.set("planned_layers", [info])
        prompt = node._build_prompt(info, ctx)
        assert "upper" in prompt.lower() or "15-25%" in prompt

    def test_no_position_fallback_for_background(self):
        node = LayerGenerateNode()
        info = LayerInfo(name="paper", description="Paper", z_index=0, content_type="background")
        ctx = NodeContext(intent="test", tradition="chinese_xieyi", provider="mock")
        ctx.set("planned_layers", [info])
        prompt = node._build_prompt(info, ctx)
        assert "corner" not in prompt.lower()

    def test_no_fallback_when_prompt_has_position(self):
        node = LayerGenerateNode()
        info = LayerInfo(
            name="trees",
            description="Trees in the lower 20% of canvas",
            z_index=2,
            content_type="subject",
            regeneration_prompt="Pine trees in the lower 20% of canvas, covering about 15%",
        )
        ctx = NodeContext(intent="test", tradition="chinese_xieyi", provider="mock")
        ctx.set("planned_layers", [info])
        prompt = node._build_prompt(info, ctx)
        # Should NOT have default position since regeneration_prompt already has position
        assert prompt.count("Position:") == 0


class TestBackgroundPromptSafety:
    def test_background_prompt_is_texture_only(self):
        """Background prompt must override VLM plan and force texture-only."""
        node = LayerGenerateNode()
        info = LayerInfo(
            name="paper", description="Rice paper base", z_index=0,
            content_type="background",
            regeneration_prompt="Rice paper with distant mountain silhouettes and a small hut",
        )
        ctx = NodeContext(intent="水墨山水", tradition="chinese_xieyi", provider="mock")
        ctx.set("planned_layers", [info])
        prompt = node._build_prompt(info, ctx)
        # VLM contamination ("silhouettes", "small hut") must NOT appear
        assert "silhouettes" not in prompt.lower()
        assert "small hut" not in prompt.lower()
        # Must contain texture keywords
        assert "texture" in prompt.lower()

    def test_background_prompt_no_scene_exclusion(self):
        """Background prompt should say 'no mountains, no trees' etc."""
        node = LayerGenerateNode()
        info = LayerInfo(name="bg", description="bg", z_index=0, content_type="background")
        ctx = NodeContext(intent="test", tradition="chinese_xieyi", provider="mock")
        ctx.set("planned_layers", [info])
        prompt = node._build_prompt(info, ctx)
        assert "no mountains" in prompt.lower() or "no scene" in prompt.lower()
