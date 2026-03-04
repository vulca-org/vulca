"""QueenNode — LangGraph wrapper for the QueenAgent.

Makes accept/rerun/stop decisions based on Critic scores and budget state.
This node also emits the DECISION_MADE event consumed by the frontend.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from app.prototype.graph.base_agent import BaseAgent
from app.prototype.graph.registry import AgentRegistry
from app.prototype.orchestrator.events import EventType

logger = logging.getLogger(__name__)


@AgentRegistry.register("queen")
class QueenNode(BaseAgent):
    name = "queen"
    description = "Accept/rerun/stop decision based on critic scores and budget"

    try:
        from app.prototype.graph.agent_metadata import AgentMetadata
        metadata_info = AgentMetadata(
            display_name="Decision Queen",
            supports_hitl=True,
            estimated_latency_ms=100,
            input_keys=["task_id", "current_round", "max_rounds", "critique_output", "critique_history", "total_cost_usd", "candidates_generated"],
            output_keys=["queen_decision", "queen_output", "queen_history", "plan_state", "final_decision", "best_candidate_id"],
            tags=["decision", "budget", "loop-control"],
        )
    except ImportError:
        metadata_info = None

    def __init__(self, queen_config: dict | None = None):
        self._queen_config_dict = queen_config or {}

    def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        from app.prototype.agents.queen_agent import QueenAgent
        from app.prototype.agents.queen_config import QueenConfig
        from app.prototype.agents.queen_types import PlanState

        t0 = time.monotonic()
        task_id = state["task_id"]
        current_round = state.get("current_round", 1)
        max_rounds = state.get("max_rounds", 3)

        # Reconstruct QueenConfig
        cfg_kwargs = {}
        if "accept_threshold" in self._queen_config_dict:
            cfg_kwargs["accept_threshold"] = self._queen_config_dict["accept_threshold"]
        if "early_stop_threshold" in self._queen_config_dict:
            cfg_kwargs["early_stop_threshold"] = self._queen_config_dict["early_stop_threshold"]
        if "max_rounds" in self._queen_config_dict:
            cfg_kwargs["max_rounds"] = self._queen_config_dict["max_rounds"]
        else:
            cfg_kwargs["max_rounds"] = max_rounds
        q_cfg = QueenConfig(**cfg_kwargs)

        queen = QueenAgent(config=q_cfg)

        # Build PlanState from current state
        plan_state = PlanState(task_id=task_id)
        plan_state.current_round = current_round
        plan_state.budget.rounds_used = current_round
        plan_state.budget.total_cost_usd = state.get("total_cost_usd", 0.0)
        plan_state.budget.candidates_generated = state.get("candidates_generated", 0)

        # Use critique history for score progression
        critique_history = state.get("critique_history", [])
        if len(critique_history) >= 2:
            plan_state.history = critique_history[:-1]

        critique_dict = state.get("critique_output") or {}
        queen_output = queen.decide(critique_dict, plan_state)
        queen_ms = int((time.monotonic() - t0) * 1000)

        decision = queen_output.decision
        queen_dict = queen_output.to_dict()

        # Accumulate queen history
        queen_history = list(state.get("queen_history", []))
        queen_history.append(queen_dict)

        # Budget state for event payload
        budget_state = {
            "rounds_used": current_round,
            "max_rounds": max_rounds,
            "total_cost_usd": round(state.get("total_cost_usd", 0.0), 6),
            "candidates_generated": state.get("candidates_generated", 0),
        }

        events = [
            _make_event(EventType.STAGE_STARTED, "queen", current_round, 0),
            _make_event(EventType.STAGE_COMPLETED, "queen", current_round, queen_ms, {
                "latency_ms": queen_ms,
            }),
            _make_event(EventType.DECISION_MADE, "queen", current_round, queen_ms, {
                "action": decision.action,
                "reason": decision.reason,
                "rerun_dimensions": decision.rerun_dimensions,
                "preserve_dimensions": getattr(decision, "preserve_dimensions", []),
                "round": current_round,
                "latency_ms": queen_ms,
                "budget_state": budget_state,
            }),
        ]

        # Determine best_candidate_id from critique
        best_candidate_id = critique_dict.get("best_candidate_id")

        return {
            "queen_decision": decision.to_dict(),
            "queen_output": queen_dict,
            "queen_history": queen_history,
            "plan_state": plan_state.to_dict(),
            "final_decision": decision.action,
            "best_candidate_id": best_candidate_id,
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
