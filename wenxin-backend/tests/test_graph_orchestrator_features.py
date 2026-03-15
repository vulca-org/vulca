"""Tests for GraphOrchestrator feature parity additions."""
import warnings
import pytest

# Check if langgraph is available (it's an optional dep not in base requirements)
langgraph_available = True
try:
    import langgraph  # noqa: F401
except ImportError:
    langgraph_available = False

skip_no_langgraph = pytest.mark.skipif(
    not langgraph_available,
    reason="langgraph not installed in this environment",
)


@skip_no_langgraph
def test_get_orchestrator_default_is_graph():
    """Default orchestrator should now be GraphOrchestrator."""
    from app.prototype.orchestrator import get_orchestrator
    orch = get_orchestrator()
    from app.prototype.graph.graph_orchestrator import GraphOrchestrator
    assert isinstance(orch, GraphOrchestrator)


def test_get_orchestrator_pipeline_warns():
    """Using mode='pipeline' should emit deprecation warning."""
    from app.prototype.orchestrator import get_orchestrator
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        orch = get_orchestrator(mode="pipeline")
        from app.prototype.orchestrator.orchestrator import PipelineOrchestrator
        assert isinstance(orch, PipelineOrchestrator)
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "deprecated" in str(w[0].message).lower()


def test_get_orchestrator_invalid_mode_raises():
    """Unknown mode should raise ValueError."""
    from app.prototype.orchestrator import get_orchestrator
    with pytest.raises(ValueError, match="Unknown orchestrator mode"):
        get_orchestrator(mode="nonexistent")


@skip_no_langgraph
def test_graph_orchestrator_has_run_sync():
    """GraphOrchestrator should have run_sync method."""
    from app.prototype.graph.graph_orchestrator import GraphOrchestrator
    orch = GraphOrchestrator()
    assert hasattr(orch, "run_sync")
    assert callable(orch.run_sync)


@skip_no_langgraph
def test_graph_orchestrator_skill_hook_params():
    """GraphOrchestrator should accept skill_hook params."""
    from app.prototype.graph.graph_orchestrator import GraphOrchestrator
    orch = GraphOrchestrator(
        enable_skill_hook=True,
        skill_hook_names=["enhance", "colorize"],
    )
    assert orch._enable_skill_hook is True
    assert orch._skill_hook_names == ["enhance", "colorize"]
