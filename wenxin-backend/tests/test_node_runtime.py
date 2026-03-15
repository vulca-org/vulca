"""Tests for node runtime state management."""
from app.prototype.graph.node_runtime import NodeRuntimeManager, NodeRuntimeState


def test_default_state():
    mgr = NodeRuntimeManager()
    state = mgr.get("scout")
    assert state.muted is False
    assert state.bypassed is False
    assert state.expanded is False


def test_toggle_mute():
    mgr = NodeRuntimeManager()
    result = mgr.toggle_mute("scout")
    assert result is True
    assert mgr.is_muted("scout") is True
    result = mgr.toggle_mute("scout")
    assert result is False


def test_toggle_bypass():
    mgr = NodeRuntimeManager()
    result = mgr.toggle_bypass("draft")
    assert result is True
    assert mgr.is_bypassed("draft") is True


def test_toggle_expand():
    mgr = NodeRuntimeManager()
    result = mgr.toggle_expand("draft")
    assert result is True
    assert mgr.is_expanded("draft") is True


def test_get_all():
    mgr = NodeRuntimeManager()
    mgr.toggle_mute("scout")
    mgr.toggle_bypass("draft")
    all_states = mgr.get_all()
    assert "scout" in all_states
    assert all_states["scout"]["muted"] is True
    assert "draft" in all_states
    assert all_states["draft"]["bypassed"] is True


def test_state_to_dict():
    state = NodeRuntimeState(muted=True, bypassed=False, expanded=True)
    d = state.to_dict()
    assert d == {"muted": True, "bypassed": False, "expanded": True}
