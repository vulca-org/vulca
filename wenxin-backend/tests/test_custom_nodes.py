"""Tests for custom node registration and execution."""
from app.prototype.graph.registry import AgentRegistry
import app.prototype.graph.nodes  # noqa: F401 — trigger registrations


def test_skill_node_registered():
    """SkillNode should be registered in AgentRegistry."""
    agent_cls = AgentRegistry.get("skill")
    assert agent_cls is not None
    assert agent_cls.category == "skill"


def test_gate_node_registered():
    """GateNode should be registered."""
    agent_cls = AgentRegistry.get("gate")
    assert agent_cls is not None
    assert agent_cls.category == "flow"


def test_loop_node_registered():
    """LoopNode should be registered."""
    agent_cls = AgentRegistry.get("loop")
    assert agent_cls is not None
    assert agent_cls.category == "flow"


def test_gate_node_execute():
    """GateNode should evaluate threshold correctly."""
    gate = AgentRegistry.get("gate")(threshold=0.5)
    state = {
        "critique_output": {
            "scores": [{"weighted_score": 0.8}],
        },
        "current_round": 1,
    }
    result = gate.execute(state)
    assert result["gate_decision"]["passed"] is True


def test_gate_node_fails_threshold():
    gate = AgentRegistry.get("gate")(threshold=0.9)
    state = {
        "critique_output": {
            "scores": [{"weighted_score": 0.5}],
        },
        "current_round": 1,
    }
    result = gate.execute(state)
    assert result["gate_decision"]["passed"] is False


def test_loop_node_execute():
    """LoopNode should control iteration."""
    loop = AgentRegistry.get("loop")(max_iterations=3)
    state = {"current_round": 1, "max_rounds": 3}
    result = loop.execute(state)
    assert result["loop_continue"] is True

    state["current_round"] = 3
    result = loop.execute(state)
    assert result["loop_continue"] is False


def test_list_by_category():
    """list_by_category should filter correctly."""
    flow_agents = AgentRegistry.list_by_category("flow")
    assert "gate" in flow_agents
    assert "loop" in flow_agents


def test_skill_node_execute():
    """SkillNode should run without crashing even if skill not found."""
    skill = AgentRegistry.get("skill")(skill_name="nonexistent")
    state = {"task_id": "test", "subject": "test", "cultural_tradition": "default", "current_round": 0}
    result = skill.execute(state)
    assert "skill_results" in result
    assert "events" in result
