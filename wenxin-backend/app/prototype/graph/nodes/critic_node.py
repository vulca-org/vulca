"""CriticNode — LangGraph wrapper for the CriticAgent.

Evaluates draft candidates across L1-L5 dimensions with cultural
weight modulation from the pipeline route.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from app.prototype.graph.base_agent import BaseAgent
from app.prototype.graph.registry import AgentRegistry
from app.prototype.orchestrator.events import EventType

logger = logging.getLogger(__name__)


@AgentRegistry.register("critic")
class CriticNode(BaseAgent):
    name = "critic"
    description = "Score candidates across L1-L5 cultural dimensions"

    try:
        from app.prototype.graph.agent_metadata import AgentMetadata
        metadata_info = AgentMetadata(
            display_name="L1-L5 Critic",
            supports_hitl=True,
            estimated_latency_ms=55000,
            input_keys=["task_id", "subject", "cultural_tradition", "scout_output", "draft_output", "pipeline_route", "critic_config"],
            output_keys=["critique_output", "critique_history"],
            tags=["scoring", "evaluation", "vlm"],
        )
    except ImportError:
        metadata_info = None

    def __init__(
        self,
        enable_agent_critic: bool = False,
        parallel_critic: bool = False,
    ):
        self._enable_agent_critic = enable_agent_critic
        self._parallel_critic = parallel_critic

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        from app.prototype.agents.critic_agent import CriticAgent, build_critique_output
        from app.prototype.agents.critic_config import CriticConfig
        from app.prototype.agents.critic_types import CritiqueInput

        t0 = time.monotonic()
        task_id = state["task_id"]
        subject = state["subject"]
        tradition = state["cultural_tradition"]
        evidence_dict = state.get("scout_output") or {}
        current_round = state.get("current_round", 1)

        # Get candidates from draft output
        draft_out = state.get("draft_output") or {}
        candidates = draft_out.get("candidates", [])

        # Build CriticConfig from route (includes cultural weights)
        route_dict = state.get("pipeline_route") or {}
        critic_cfg_dict = route_dict.get("critic_config") or state.get("critic_config") or {}

        # Reconstruct CriticConfig — only pass known fields
        cfg_kwargs = {}
        if "weights" in critic_cfg_dict:
            cfg_kwargs["weights"] = critic_cfg_dict["weights"]
        if "pass_threshold" in critic_cfg_dict:
            cfg_kwargs["pass_threshold"] = critic_cfg_dict["pass_threshold"]
        if "use_vlm" in critic_cfg_dict:
            cfg_kwargs["use_vlm"] = critic_cfg_dict["use_vlm"]
        critic_cfg = CriticConfig(**cfg_kwargs)

        if self._parallel_critic:
            # Parallel path: score L1-L5 concurrently, shared assembly
            from app.prototype.agents.parallel_scorer import ParallelDimensionScorer
            scorer = ParallelDimensionScorer(max_workers=5)
            critique_output = build_critique_output(
                task_id, candidates, evidence_dict, tradition, subject,
                critic_cfg, scorer.score_all_dimensions, t0,
            )
        elif self._enable_agent_critic:
            # LLM-enhanced path
            try:
                from app.prototype.agents.critic_llm import CriticLLM
                critic = CriticLLM(config=critic_cfg)
            except Exception:
                critic = CriticAgent(config=critic_cfg)
            critique_input = CritiqueInput(
                task_id=task_id, subject=subject,
                cultural_tradition=tradition,
                evidence=evidence_dict, candidates=candidates,
            )
            critique_output = critic.run(critique_input)
        else:
            # Default rule-based path
            critic = CriticAgent(config=critic_cfg)
            critique_input = CritiqueInput(
                task_id=task_id, subject=subject,
                cultural_tradition=tradition,
                evidence=evidence_dict, candidates=candidates,
            )
            critique_output = critic.run(critique_input)

        critique_dict = critique_output.to_dict()
        critic_ms = int((time.monotonic() - t0) * 1000)

        # Accumulate critique history
        critique_history = list(state.get("critique_history", []))
        critique_history.append(critique_dict)

        events = [
            _make_event(EventType.STAGE_STARTED, "critic", current_round, 0),
            _make_event(EventType.STAGE_COMPLETED, "critic", current_round, critic_ms, {
                "latency_ms": critic_ms,
                "critique": critique_dict,
            }),
        ]

        return {
            "critique_output": critique_dict,
            "critique_history": critique_history,
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
