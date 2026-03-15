"""GateNode — quality gate with conditional routing."""

from __future__ import annotations

from typing import Any

from app.prototype.graph.agent_metadata import AgentMetadata
from app.prototype.graph.custom_node import BaseCustomNode, register_custom_node
from app.prototype.pipeline.port_contract import DataType, PortDirection, PortSpec


@register_custom_node("gate", category="flow")
class GateNode(BaseCustomNode):
    """Quality gate: routes based on score threshold."""

    description = "Quality gate with score-based conditional routing"
    input_ports = [
        PortSpec("critique", DataType.CRITIQUE, PortDirection.INPUT),
    ]
    output_ports = [
        PortSpec("decision", DataType.DECISION, PortDirection.OUTPUT),
    ]
    metadata_info = AgentMetadata(
        display_name="Quality Gate",
        supports_hitl=False,
        estimated_latency_ms=100,
        input_keys=["critique_output"],
        output_keys=["gate_decision"],
        tags=["flow", "gate", "quality"],
    )

    def __init__(self, threshold: float = 0.7, dimension: str = ""):
        self._threshold = threshold
        self._dimension = dimension

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Evaluate gate condition and emit decision."""
        from app.prototype.orchestrator.events import EventType

        critique = state.get("critique_output") or state.get("critique") or {}
        scores = critique.get("scores", [])

        # Find best weighted score
        best_score = 0.0
        for s in scores:
            ws = s.get("weighted_score", 0.0)
            if ws > best_score:
                best_score = ws

        passed = best_score >= self._threshold
        decision = {
            "passed": passed,
            "score": best_score,
            "threshold": self._threshold,
            "dimension": self._dimension,
        }

        events = [{
            "event_type": EventType.FLOW_DECISION.value,
            "stage": "gate",
            "round_num": state.get("current_round", 0),
            "payload": decision,
            "timestamp_ms": 0,
        }]

        return {"gate_decision": decision, "events": events}
