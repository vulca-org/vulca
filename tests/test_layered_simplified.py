"""Tests for simplified LAYERED pipeline — 2 nodes, agent orchestrates composition."""
import pytest

from vulca.pipeline import execute
from vulca.pipeline.templates import LAYERED, TEMPLATES
from vulca.pipeline.types import PipelineInput


class TestLayeredSimplified:
    def test_layered_has_two_nodes(self):
        assert LAYERED.nodes == ("plan_layers", "layer_generate")

    def test_layered_no_loop(self):
        assert LAYERED.enable_loop is False

    def test_layered_no_composite_node(self):
        assert "composite" not in LAYERED.nodes
        assert "evaluate" not in LAYERED.nodes
        assert "decide" not in LAYERED.nodes

    def test_layered_entry_point(self):
        assert LAYERED.entry_point == "plan_layers"

    @pytest.mark.asyncio
    async def test_layered_returns_layers_no_composite(self):
        inp = PipelineInput(
            subject="test",
            intent="test layered",
            tradition="chinese_xieyi",
            provider="mock",
            layered=True,
        )
        output = await execute(LAYERED, inp)
        assert output.status == "completed"
        assert output.total_rounds == 1
        assert output.weighted_total == 0.0


class TestMCPDocstrings:
    def test_create_artwork_layered_docstring(self):
        from vulca.mcp_server import create_artwork
        doc = create_artwork.__doc__ or ""
        assert "layer" in doc.lower()
        assert "agent" in doc.lower() or "review" in doc.lower()

    def test_layers_composite_docstring(self):
        from vulca.mcp_server import layers_composite
        doc = layers_composite.__doc__ or ""
        assert "review" in doc.lower() or "adjust" in doc.lower()

    def test_layers_redraw_docstring(self):
        from vulca.mcp_server import layers_redraw
        doc = layers_redraw.__doc__ or ""
        assert "position" in doc.lower() or "scale" in doc.lower()
