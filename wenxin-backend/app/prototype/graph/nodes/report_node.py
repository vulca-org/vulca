"""ReportNode — formats L1-L5 scores into a human-readable report.

Reads critique_output from state and produces a summary with
traffic-light coloring, dimension breakdown, and risk highlights.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from app.prototype.graph.base_agent import BaseAgent
from app.prototype.graph.registry import AgentRegistry
from app.prototype.orchestrator.events import EventType

logger = logging.getLogger(__name__)

_DIM_LABELS = {
    "L1": "Technique",
    "L2": "Aesthetics",
    "L3": "Cultural Auth.",
    "L4": "Prompt Fidelity",
    "L5": "Cultural Depth",
    "technique": "Technique",
    "aesthetic": "Aesthetics",
    "cultural_authenticity": "Cultural Auth.",
    "prompt_fidelity": "Prompt Fidelity",
    "cultural_depth": "Cultural Depth",
}


@AgentRegistry.register("report")
class ReportNode(BaseAgent):
    name = "report"
    description = "Format evaluation results into human-readable report"

    try:
        from app.prototype.graph.agent_metadata import AgentMetadata

        metadata_info = AgentMetadata(
            display_name="Report Summary",
            supports_hitl=False,
            estimated_latency_ms=50,
            input_keys=["critique_output", "cultural_tradition"],
            output_keys=["report_output"],
            tags=["report", "summary"],
        )
    except ImportError:
        metadata_info = None

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        t0 = time.monotonic()
        current_round = state.get("current_round", 1)
        critique = state.get("critique_output") or {}
        tradition = state.get("cultural_tradition", "unknown")

        scored = critique.get("scored_candidates", [])
        best_id = critique.get("best_candidate_id")

        # Find best candidate
        best: dict[str, Any] | None = None
        for sc in scored:
            if sc.get("candidate_id") == best_id:
                best = sc
                break
        if not best and scored:
            best = max(scored, key=lambda x: x.get("weighted_total", 0))

        dimension_scores: list[dict[str, Any]] = []
        risk_flags: list[str] = []
        weighted_total = 0.0

        if best:
            weighted_total = best.get("weighted_total", 0.0)
            risk_flags = list(best.get("risk_tags", []))
            for ds in best.get("dimension_scores", []):
                dim = ds.get("dimension", "")
                score = ds.get("score", 0.0)
                label = _DIM_LABELS.get(dim, dim)
                dimension_scores.append(
                    {"dimension": dim, "label": label, "score": score}
                )
                if score < 0.70:
                    risk_flags.append(f"{label} low ({score:.2f})")

        # Traffic light summary
        if weighted_total >= 0.85:
            level, summary = "green", "Excellent cultural quality"
        elif weighted_total >= 0.70:
            level, summary = "yellow", "Acceptable with room for improvement"
        else:
            level, summary = "red", "Needs significant revision"

        report_output: dict[str, Any] = {
            "weighted_total": weighted_total,
            "summary": summary,
            "level": level,
            "dimension_scores": dimension_scores,
            "tradition": tradition,
            "risk_flags": list(set(risk_flags)),
            "best_candidate_id": best_id,
        }

        ms = int((time.monotonic() - t0) * 1000)
        events = [
            _make_event(EventType.STAGE_STARTED, "report", current_round, 0),
            _make_event(
                EventType.STAGE_COMPLETED,
                "report",
                current_round,
                ms,
                {"report_output": report_output},
            ),
        ]

        return {"report_output": report_output, "events": events}


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
