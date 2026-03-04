"""ArchivistNode — LangGraph wrapper for the ArchivistAgent.

Generates audit artifacts (evidence chain, critique card, params snapshot)
after the pipeline completes.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from app.prototype.graph.base_agent import BaseAgent
from app.prototype.graph.registry import AgentRegistry
from app.prototype.orchestrator.events import EventType

logger = logging.getLogger(__name__)


@AgentRegistry.register("archivist")
class ArchivistNode(BaseAgent):
    name = "archivist"
    description = "Generate audit artifacts and archive pipeline results"

    try:
        from app.prototype.graph.agent_metadata import AgentMetadata
        metadata_info = AgentMetadata(
            display_name="Audit Archivist",
            supports_hitl=False,
            estimated_latency_ms=500,
            input_keys=["task_id", "subject", "cultural_tradition", "scout_output", "critique_history", "queen_history", "final_decision", "best_candidate_id"],
            output_keys=["archivist_output"],
            tags=["archival", "audit"],
        )
    except ImportError:
        metadata_info = None

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        from app.prototype.agents.archivist_agent import ArchivistAgent
        from app.prototype.agents.archivist_types import ArchivistInput

        t0 = time.monotonic()
        task_id = state["task_id"]
        current_round = state.get("current_round", 1)

        # Build pipeline output dict for Archivist
        pipeline_out_dict = {
            "task_id": task_id,
            "final_decision": state.get("final_decision", "stop"),
            "best_candidate_id": state.get("best_candidate_id"),
            "total_rounds": current_round,
            "success": True,
        }

        arch_input = ArchivistInput(
            task_id=task_id,
            subject=state["subject"],
            cultural_tradition=state["cultural_tradition"],
            pipeline_output_dict=pipeline_out_dict,
            scout_evidence_dict=state.get("scout_output") or {},
            critique_dicts=state.get("critique_history", []),
            queen_dicts=state.get("queen_history", []),
            draft_config_dict=state.get("draft_config") or {},
            critic_config_dict=state.get("critic_config") or {},
            queen_config_dict=state.get("queen_config") or {},
        )

        archivist = ArchivistAgent()
        arch_out = archivist.run(arch_input)
        arch_ms = int((time.monotonic() - t0) * 1000)

        events = [
            _make_event(EventType.STAGE_STARTED, "archivist", current_round, 0),
            _make_event(EventType.STAGE_COMPLETED, "archivist", current_round, arch_ms, {
                "success": arch_out.success,
                "evidence_chain_path": arch_out.evidence_chain_path,
                "error": arch_out.error,
            }),
        ]

        return {
            "archivist_output": arch_out.to_dict(),
            "events": events,
        }


def _make_event(
    event_type: EventType,
    stage: str,
    round_num: int,
    timestamp_ms: int,
    payload: dict | None = None,
) -> dict:
    return {
        "event_type": event_type.value,
        "stage": stage,
        "round_num": round_num,
        "payload": payload or {},
        "timestamp_ms": timestamp_ms,
    }
