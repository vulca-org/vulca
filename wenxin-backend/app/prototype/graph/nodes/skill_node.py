"""SkillNode — executes a skill from the marketplace via pipeline_hook."""

from __future__ import annotations

from typing import Any

from app.prototype.graph.agent_metadata import AgentMetadata
from app.prototype.graph.custom_node import BaseCustomNode, register_custom_node
from app.prototype.graph.registry import AgentRegistry
from app.prototype.pipeline.port_contract import DataType, PortDirection, PortSpec


@register_custom_node("skill", category="skill")
class SkillNode(BaseCustomNode):
    """Execute a skill from the marketplace."""

    description = "Execute a marketplace skill via pipeline_hook"
    input_ports = [
        PortSpec("pipeline_input", DataType.PIPELINE_INPUT, PortDirection.INPUT),
        PortSpec("skill_results", DataType.SKILL_RESULTS, PortDirection.INPUT, required=False),
    ]
    output_ports = [
        PortSpec("skill_results", DataType.SKILL_RESULTS, PortDirection.OUTPUT),
    ]
    metadata_info = AgentMetadata(
        display_name="Skill Runner",
        supports_hitl=False,
        estimated_latency_ms=3000,
        input_keys=["task_id", "subject", "cultural_tradition"],
        output_keys=["skill_results"],
        tags=["skill", "marketplace"],
    )

    def __init__(self, skill_name: str = "", skill_config: dict | None = None):
        self._skill_name = skill_name
        self._skill_config = skill_config or {}

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Execute the skill and return results."""
        import time
        from app.prototype.orchestrator.events import EventType

        task_id = state.get("task_id", "")
        t0 = time.monotonic()

        events = [
            {
                "event_type": EventType.SKILL_STARTED.value,
                "stage": "skill",
                "round_num": state.get("current_round", 0),
                "payload": {"skill_name": self._skill_name},
                "timestamp_ms": 0,
            }
        ]

        # Try to run the skill via pipeline_hook
        results = []
        try:
            from app.prototype.skills.executor import execute_skill
            result = execute_skill(
                self._skill_name,
                subject=state.get("subject", ""),
                tradition=state.get("cultural_tradition", "default"),
                config=self._skill_config,
            )
            if result:
                results = [result] if isinstance(result, dict) else list(result)
        except (ImportError, Exception) as e:
            results = [{"error": str(e), "skill_name": self._skill_name}]

        elapsed_ms = int((time.monotonic() - t0) * 1000)
        events.append({
            "event_type": EventType.SKILL_COMPLETED.value,
            "stage": "skill",
            "round_num": state.get("current_round", 0),
            "payload": {
                "skill_name": self._skill_name,
                "results_count": len(results),
                "duration_ms": elapsed_ms,
            },
            "timestamp_ms": elapsed_ms,
        })

        # Merge with existing skill_results
        existing = state.get("skill_results") or []
        if isinstance(existing, list):
            results = existing + results

        return {"skill_results": results, "events": events}
