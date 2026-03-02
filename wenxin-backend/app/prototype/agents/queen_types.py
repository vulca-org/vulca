"""Queen Agent data types — BudgetState, PlanState, QueenDecision, QueenOutput."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.prototype.agents.layer_state import (
    CrossLayerSignal,
    IntentCardV2,
    LayerState,
    LocalRerunRequest,
    init_layer_states,
)

__all__ = [
    "BudgetState",
    "PlanState",
    "QueenDecision",
    "QueenOutput",
]


@dataclass
class BudgetState:
    """Tracks cumulative resource usage for a single task."""

    rounds_used: int = 0
    total_cost_usd: float = 0.0
    candidates_generated: int = 0
    critic_calls: int = 0
    llm_calls: int = 0          # v2: track LLM Agent invocations
    tool_calls: int = 0         # v2: track tool executions within Agents

    def to_dict(self) -> dict:
        return {
            "rounds_used": self.rounds_used,
            "total_cost_usd": round(self.total_cost_usd, 6),
            "candidates_generated": self.candidates_generated,
            "critic_calls": self.critic_calls,
            "llm_calls": self.llm_calls,
            "tool_calls": self.tool_calls,
        }


@dataclass
class PlanState:
    """Tracks the multi-round evaluation state for a single task."""

    task_id: str
    current_round: int = 0
    confirmed_dimensions: list[str] = field(default_factory=list)
    pending_dimensions: list[str] = field(default_factory=list)
    budget: BudgetState = field(default_factory=BudgetState)
    history: list[dict] = field(default_factory=list)
    # HITL fields
    human_locked_dimensions: list[str] = field(default_factory=list)
    human_override_history: list[dict] = field(default_factory=list)

    # --- v2: L1-L5 dynamic state ---
    layer_states: dict[str, LayerState] = field(default_factory=init_layer_states)
    intent_card: IntentCardV2 | None = None
    cross_layer_signals: list[CrossLayerSignal] = field(default_factory=list)
    local_rerun_request: LocalRerunRequest | None = None

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "current_round": self.current_round,
            "confirmed_dimensions": self.confirmed_dimensions,
            "pending_dimensions": self.pending_dimensions,
            "budget": self.budget.to_dict(),
            "history": self.history,
            "human_locked_dimensions": self.human_locked_dimensions,
            "human_override_history": self.human_override_history,
            "layer_states": {k: v.to_dict() for k, v in self.layer_states.items()},
            "intent_card": self.intent_card.to_dict() if self.intent_card else None,
            "cross_layer_signals": [s.to_dict() for s in self.cross_layer_signals],
            "local_rerun_request": (
                self.local_rerun_request.to_dict()
                if self.local_rerun_request else None
            ),
        }


@dataclass
class QueenDecision:
    """A single decision emitted by the Queen Agent.

    v2 adds rerun_local distinction and expected_gain_per_cost.
    """

    action: str  # "accept" | "rerun" | "stop" (orchestrator may upgrade to "rerun_local")
    rerun_dimensions: list[str] = field(default_factory=list)
    preserve_dimensions: list[str] = field(default_factory=list)   # v2: layers to protect
    reason: str = ""
    expected_gain_per_cost: float = 0.0  # v2: cost-effectiveness estimate

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "rerun_dimensions": self.rerun_dimensions,
            "preserve_dimensions": self.preserve_dimensions,
            "reason": self.reason,
            "expected_gain_per_cost": round(self.expected_gain_per_cost, 4),
        }


@dataclass
class QueenOutput:
    """Output of the Queen Agent."""

    task_id: str
    decision: QueenDecision = field(default_factory=lambda: QueenDecision(action="stop"))
    plan_state: PlanState = field(default_factory=lambda: PlanState(task_id=""))
    created_at: str = ""
    latency_ms: int = 0
    success: bool = True
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "decision": self.decision.to_dict(),
            "plan_state": self.plan_state.to_dict(),
            "created_at": self.created_at,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "error": self.error,
        }
