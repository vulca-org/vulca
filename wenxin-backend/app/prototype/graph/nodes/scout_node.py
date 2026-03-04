"""ScoutNode — LangGraph wrapper for the Scout evidence gathering stage.

Scout has no independent agent class; it uses ScoutService directly.
This node encapsulates the gather_evidence + build_evidence_pack flow
from the orchestrator into a standalone graph node.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from app.prototype.graph.base_agent import BaseAgent
from app.prototype.graph.registry import AgentRegistry
from app.prototype.orchestrator.events import EventType

logger = logging.getLogger(__name__)


@AgentRegistry.register("scout")
class ScoutNode(BaseAgent):
    name = "scout"
    description = "Gather cultural evidence from VULCA-Bench, terminology dictionaries, and taboo rules"

    try:
        from app.prototype.graph.agent_metadata import AgentMetadata
        metadata_info = AgentMetadata(
            display_name="Cultural Scout",
            supports_hitl=True,
            estimated_latency_ms=2000,
            input_keys=["task_id", "subject", "cultural_tradition"],
            output_keys=["scout_output", "evidence_pack"],
            tags=["evidence", "retrieval"],
        )
    except ImportError:
        metadata_info = None

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        from app.prototype.tools.scout_service import ScoutService

        t0 = time.monotonic()
        task_id = state["task_id"]
        subject = state["subject"]
        tradition = state["cultural_tradition"]

        scout_svc = ScoutService()
        evidence = scout_svc.gather_evidence(
            subject=subject,
            cultural_tradition=tradition,
        )
        evidence_dict = evidence.to_dict()
        evidence_dict["evidence_coverage"] = scout_svc.compute_evidence_coverage(evidence)

        # Build structured EvidencePack for downstream Draft enrichment
        evidence_pack_obj = scout_svc.build_evidence_pack(
            subject=subject,
            tradition=tradition,
            evidence=evidence,
        )
        evidence_dict["evidence_pack"] = evidence_pack_obj.to_dict()

        scout_ms = int((time.monotonic() - t0) * 1000)

        # Emit events
        events = [
            _make_event(EventType.STAGE_STARTED, "scout", 0, 0),
            _make_event(EventType.STAGE_COMPLETED, "scout", 0, scout_ms, {
                "latency_ms": scout_ms,
                "evidence": evidence_dict,
            }),
        ]

        return {
            "scout_output": evidence_dict,
            "evidence_pack": evidence_pack_obj.to_dict(),
            "events": events,
        }


def _make_event(
    event_type: EventType,
    stage: str,
    round_num: int,
    timestamp_ms: int,
    payload: dict | None = None,
) -> dict:
    """Create a serializable event dict matching PipelineEvent.to_dict() format."""
    return {
        "event_type": event_type.value,
        "stage": stage,
        "round_num": round_num,
        "payload": payload or {},
        "timestamp_ms": timestamp_ms,
    }
