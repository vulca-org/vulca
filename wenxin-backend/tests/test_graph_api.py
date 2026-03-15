"""Tests for the graph execution REST API endpoints."""
from app.prototype.api.schemas import (
    ExecuteGraphRequest,
    ExecuteGraphResponse,
    GraphValidateRequest,
    GraphValidateResponse,
    NodeRuntimeToggleResponse,
)


def test_execute_graph_request_schema():
    """ExecuteGraphRequest should validate correctly."""
    req = ExecuteGraphRequest(subject="A serene mountain landscape")
    assert req.tradition == "default"
    assert req.template == "default"
    assert req.max_rounds == 3


def test_execute_graph_response_schema():
    resp = ExecuteGraphResponse(task_id="test-123", success=True)
    assert resp.error is None
    assert resp.events == []


def test_graph_validate_request_schema():
    req = GraphValidateRequest(
        nodes=["scout", "draft", "critic"],
        edges=[("scout", "draft"), ("draft", "critic")],
    )
    assert req.check_ports is True


def test_node_runtime_toggle_response():
    resp = NodeRuntimeToggleResponse(node_name="scout", state="muted", value=True)
    assert resp.node_name == "scout"
    assert resp.value is True
