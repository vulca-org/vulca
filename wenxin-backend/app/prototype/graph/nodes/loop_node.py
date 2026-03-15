"""LoopNode — bounded iteration control node."""

from __future__ import annotations

from typing import Any

from app.prototype.graph.agent_metadata import AgentMetadata
from app.prototype.graph.custom_node import BaseCustomNode, register_custom_node
from app.prototype.orchestrator.events import EventType
from app.prototype.pipeline.port_contract import DataType, PortDirection, PortSpec


@register_custom_node("loop", category="flow")
class LoopNode(BaseCustomNode):
    """Bounded iteration controller."""

    description = "Loop controller with iteration counter and max guard"
    input_ports = [
        PortSpec("critique", DataType.CRITIQUE, PortDirection.INPUT, required=False),
    ]
    output_ports = [
        PortSpec("plan_state", DataType.PLAN_STATE, PortDirection.OUTPUT),
    ]
    metadata_info = AgentMetadata(
        display_name="Loop Controller",
        supports_hitl=False,
        estimated_latency_ms=50,
        input_keys=["current_round", "max_rounds"],
        output_keys=["current_round", "loop_continue"],
        tags=["flow", "loop", "iteration"],
    )

    def __init__(self, max_iterations: int = 3):
        self._max_iterations = max_iterations

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Check iteration count and decide whether to continue."""
        current_round = state.get("current_round", 0)
        max_rounds = min(state.get("max_rounds", self._max_iterations), self._max_iterations)

        should_continue = current_round < max_rounds

        return {
            "loop_continue": should_continue,
            "plan_state": {
                "iteration": current_round,
                "max_iterations": max_rounds,
                "should_continue": should_continue,
            },
            "events": [{
                "event_type": EventType.FLOW_DECISION.value,
                "stage": "loop",
                "round_num": current_round,
                "payload": {
                    "iteration": current_round,
                    "max_iterations": max_rounds,
                    "continue": should_continue,
                },
                "timestamp_ms": 0,
            }],
        }
