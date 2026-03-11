"""DraftNode — LangGraph wrapper for the DraftAgent.

Generates candidate images based on Scout evidence and cultural routing.
Handles seed progression across rounds and cost tracking.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from app.prototype.graph.base_agent import BaseAgent
from app.prototype.graph.registry import AgentRegistry
from app.prototype.orchestrator.events import EventType

logger = logging.getLogger(__name__)


@AgentRegistry.register("draft")
class DraftNode(BaseAgent):
    name = "draft"
    description = "Generate candidate images via configured provider (mock/NB2)"

    try:
        from app.prototype.graph.agent_metadata import AgentMetadata
        metadata_info = AgentMetadata(
            display_name="Image Drafter",
            supports_hitl=True,
            estimated_latency_ms=15000,
            input_keys=["task_id", "subject", "cultural_tradition", "scout_output", "evidence_pack"],
            output_keys=["draft_output", "current_round", "candidates_generated", "total_cost_usd", "draft_history"],
            tags=["generation", "image"],
        )
    except ImportError:
        metadata_info = None

    def __init__(self, draft_config: dict | None = None):
        self._draft_config_dict = draft_config or {}

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        from app.prototype.agents.draft_agent import DraftAgent
        from app.prototype.agents.draft_config import DraftConfig
        from app.prototype.agents.draft_types import DraftInput

        t0 = time.monotonic()
        task_id = state["task_id"]
        subject = state["subject"]
        tradition = state["cultural_tradition"]
        evidence_dict = state.get("scout_output") or {}
        current_round = state.get("current_round", 0) + 1
        evidence_pack_dict = state.get("evidence_pack")

        # Reconstruct DraftConfig, applying round-specific seed
        cfg_dict = dict(self._draft_config_dict)
        base_seed = cfg_dict.pop("seed_base", 42)
        cfg_dict["seed_base"] = base_seed + (current_round - 1) * 100
        d_cfg = DraftConfig(**cfg_dict)

        media_type = state.get("media_type", "image")

        draft_agent = DraftAgent(config=d_cfg)
        draft_input = DraftInput(
            task_id=task_id,
            subject=subject,
            cultural_tradition=tradition,
            evidence=evidence_dict,
            config=d_cfg,
            media_type=media_type,
        )

        # Reconstruct EvidencePack if available
        evidence_pack = None
        if evidence_pack_dict:
            try:
                from app.prototype.tools.evidence_pack import EvidencePack
                evidence_pack = EvidencePack.from_dict(evidence_pack_dict)
            except Exception:
                pass

        draft_output = draft_agent.run(draft_input, evidence_pack=evidence_pack)
        draft_candidates = [c.to_dict() for c in draft_output.candidates]
        # Convert absolute image paths to web-accessible /static/ URLs
        for dc in draft_candidates:
            if dc.get("image_path"):
                dc["image_path"] = _to_static_url(dc["image_path"])
        draft_ms = int((time.monotonic() - t0) * 1000)

        n_new = len(draft_candidates)
        prev_generated = state.get("candidates_generated", 0)
        prev_cost = state.get("total_cost_usd", 0.0)

        # Cost tracking
        provider = d_cfg.provider
        cost_per_image = {
            "nb2": 0.067,
            "mock": 0.0,
        }.get(provider, 0.0)
        new_cost = n_new * cost_per_image

        # Emit sub-stage events if sub-stage results are present
        sub_stage_events: list[dict] = []
        sub_stage_results_dicts = draft_output.sub_stage_results or []
        for ssr in sub_stage_results_dicts:
            if isinstance(ssr, dict):
                sub_stage_events.append(
                    _make_event(EventType.SUBSTAGE_STARTED, "draft", current_round, 0, {
                        "sub_stage_name": ssr.get("stage_name", ""),
                    })
                )
                # Extract artifact data for frontend display
                artifact = ssr.get("artifact") or {}
                completed_payload: dict = {
                    "sub_stage_name": ssr.get("stage_name", ""),
                    "status": ssr.get("status", ""),
                    "duration_ms": ssr.get("duration_ms", 0),
                    "error": ssr.get("error"),
                }
                if isinstance(artifact, dict):
                    if artifact.get("data"):
                        completed_payload["data"] = str(artifact["data"])[:1000]
                    if artifact.get("image_path"):
                        completed_payload["image_path"] = _to_static_url(artifact["image_path"])
                    if artifact.get("artifact_type"):
                        completed_payload["artifact_type"] = artifact["artifact_type"]
                sub_stage_events.append(
                    _make_event(EventType.SUBSTAGE_COMPLETED, "draft", current_round, ssr.get("duration_ms", 0), completed_payload)
                )

        events = [
            _make_event(EventType.STAGE_STARTED, "draft", current_round, 0),
            *sub_stage_events,
            _make_event(EventType.STAGE_COMPLETED, "draft", current_round, draft_ms, {
                "latency_ms": draft_ms,
                "n_candidates": n_new,
                "candidates": draft_candidates,
                "sub_stage_results": sub_stage_results_dicts,
            }),
        ]

        # Accumulate draft history
        draft_history = list(state.get("draft_history", []))
        draft_history.append({
            "round": current_round,
            "candidates": draft_candidates,
            "latency_ms": draft_ms,
        })

        return {
            "draft_output": {
                "candidates": draft_candidates,
                "latency_ms": draft_ms,
                "model_ref": draft_output.model_ref,
                "sub_stage_results": sub_stage_results_dicts,
            },
            "current_round": current_round,
            "candidates_generated": prev_generated + n_new,
            "total_cost_usd": prev_cost + new_cost,
            "draft_history": draft_history,
            "sub_stage_results": sub_stage_results_dicts,
            "events": events,
        }


def _to_static_url(abs_path: str) -> str:
    """Convert an absolute filesystem path to a web-accessible /static/ URL.

    Looks for 'checkpoints/substages/' or 'checkpoints/draft/' in the path and
    maps it to /static/prototype/substages/... or /static/prototype/draft/...
    """
    if not abs_path:
        return ""
    for segment, prefix in [
        ("checkpoints/substages/", "/static/prototype/substages/"),
        ("checkpoints/draft/", "/static/prototype/draft/"),
    ]:
        idx = abs_path.find(segment)
        if idx != -1:
            return prefix + abs_path[idx + len(segment):]
    # Fallback: return as-is (may already be a relative URL)
    return abs_path


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
