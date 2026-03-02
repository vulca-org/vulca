"""Queen Agent — budget-aware decision layer over Critic output.

Decision priority:
1. Early stop: gate_passed AND weighted_total >= early_stop_threshold → ACCEPT
2. Threshold accept: gate_passed AND weighted_total >= accept_threshold → ACCEPT
3. Over rounds: rounds_used >= max_rounds → STOP
4. Over budget: total_cost >= max_cost_usd → STOP
5b. Cross-layer signal: reinterpret targets from signal → RERUN (with preserve)
6. Rerun hint: has rerun_hint AND rounds_used < max_rounds → RERUN
7. Insufficient improvement: delta < min_improvement → STOP
8. Default → RERUN
"""

from __future__ import annotations

import time
from datetime import datetime, timezone

from app.prototype.agents.critic_config import DIMENSIONS
from app.prototype.agents.queen_config import QueenConfig
from app.prototype.agents.queen_types import (
    BudgetState,
    PlanState,
    QueenDecision,
    QueenOutput,
)

__all__ = [
    "QueenAgent",
]


# L-label → dimension ID mapping, derived from canonical DIMENSIONS
_LABEL_TO_DIM = {f"L{i+1}": dim for i, dim in enumerate(DIMENSIONS)}


class QueenAgent:
    """Decide accept / rerun / stop based on Critic output and budget."""

    def __init__(self, config: QueenConfig | None = None) -> None:
        self._config = config or QueenConfig()

    def decide(
        self,
        critique_output_dict: dict,
        plan_state: PlanState,
    ) -> QueenOutput:
        """Evaluate the latest critique and update plan state."""
        t0 = time.monotonic()
        cfg = self._config

        # --- Extract best candidate info from critique output ---
        scored = critique_output_dict.get("scored_candidates", [])
        best_id = critique_output_dict.get("best_candidate_id")
        rerun_hint = critique_output_dict.get("rerun_hint", [])

        best_score = 0.0
        best_gate_passed = False
        for sc in scored:
            if sc.get("candidate_id") == best_id:
                best_score = sc.get("weighted_total", 0.0)
                best_gate_passed = sc.get("gate_passed", False)
                break

        # If no best_id, pick top scorer anyway for comparison
        if not best_id and scored:
            top = scored[0]
            best_score = top.get("weighted_total", 0.0)
            best_gate_passed = top.get("gate_passed", False)

        # --- Update budget ---
        budget = plan_state.budget
        budget.rounds_used += 1
        budget.total_cost_usd += cfg.mock_cost_per_round
        budget.critic_calls += 1
        budget.candidates_generated += len(scored)
        plan_state.current_round = budget.rounds_used

        # Record this round in history
        plan_state.history.append({
            "round": budget.rounds_used,
            "best_score": round(best_score, 4),
            "best_gate_passed": best_gate_passed,
            "best_candidate_id": best_id,
            "rerun_hint": rerun_hint,
            "cost_usd": round(budget.total_cost_usd, 6),
        })

        # --- Decision logic (priority order) ---
        decision = self._decide_action(
            cfg=cfg,
            budget=budget,
            best_score=best_score,
            best_gate_passed=best_gate_passed,
            rerun_hint=rerun_hint,
            plan_state=plan_state,
        )

        # --- Update confirmed/pending dimensions ---
        if decision.action == "accept":
            plan_state.confirmed_dimensions = list(
                set(plan_state.confirmed_dimensions) | set(plan_state.pending_dimensions)
            )
            plan_state.pending_dimensions = []
        elif decision.action == "rerun":
            plan_state.pending_dimensions = decision.rerun_dimensions

        elapsed_ms = int((time.monotonic() - t0) * 1000)

        return QueenOutput(
            task_id=plan_state.task_id,
            decision=decision,
            plan_state=plan_state,
            created_at=datetime.now(timezone.utc).isoformat(),
            latency_ms=elapsed_ms,
            success=True,
            error=None,
        )

    def _decide_action(
        self,
        cfg: QueenConfig,
        budget: BudgetState,
        best_score: float,
        best_gate_passed: bool,
        rerun_hint: list[str],
        plan_state: PlanState,
    ) -> QueenDecision:
        # 1. Early stop
        if best_gate_passed and best_score >= cfg.early_stop_threshold:
            return QueenDecision(
                action="accept",
                reason=f"early stop: weighted_total {best_score:.4f} >= {cfg.early_stop_threshold}",
            )

        # 2. Threshold accept (before over_rounds so max_rounds=1 can still accept)
        if best_gate_passed and best_score >= cfg.accept_threshold:
            return QueenDecision(
                action="accept",
                reason=f"threshold accept: weighted_total {best_score:.4f} >= {cfg.accept_threshold}",
            )

        # 3. Over rounds
        if budget.rounds_used >= cfg.max_rounds:
            return QueenDecision(
                action="stop",
                reason=f"max rounds reached: {budget.rounds_used} >= {cfg.max_rounds}",
            )

        # 4. Over budget
        if budget.total_cost_usd >= cfg.max_cost_usd:
            return QueenDecision(
                action="stop",
                reason=f"budget exhausted: ${budget.total_cost_usd:.4f} >= ${cfg.max_cost_usd:.4f}",
            )

        # 5b. Cross-layer signal driven rerun
        if plan_state.cross_layer_signals and budget.rounds_used < cfg.max_rounds:
            reinterpret_targets = []
            for sig in plan_state.cross_layer_signals:
                if sig.signal_type.value in ("reinterpret", "conflict", "evidence_gap"):
                    if sig.strength >= 0.3:
                        # Map target layer label to dimension ID
                        dim = _LABEL_TO_DIM.get(sig.target_layer, sig.target_layer)
                        if dim not in reinterpret_targets:
                            reinterpret_targets.append(dim)
            if reinterpret_targets:
                # Determine preserve dimensions (everything not being rerun)
                preserve = [d for d in DIMENSIONS if d not in reinterpret_targets]
                # Clear consumed signals
                plan_state.cross_layer_signals = []
                return QueenDecision(
                    action="rerun",
                    rerun_dimensions=reinterpret_targets,
                    preserve_dimensions=preserve,
                    reason=f"cross-layer signal: rerun {reinterpret_targets}",
                )

        # 6. Rerun hint
        if rerun_hint and budget.rounds_used < cfg.max_rounds:
            preserve = [d for d in DIMENSIONS if d not in rerun_hint]
            return QueenDecision(
                action="rerun",
                rerun_dimensions=rerun_hint,
                preserve_dimensions=preserve,
                reason=f"rerun dimensions {rerun_hint} (round {budget.rounds_used}/{cfg.max_rounds})",
            )

        # 7. Insufficient improvement
        if len(plan_state.history) >= 2:
            prev_score = plan_state.history[-2].get("best_score", 0.0)
            delta = best_score - prev_score
            if delta < cfg.min_improvement:
                return QueenDecision(
                    action="stop",
                    reason=f"insufficient improvement: delta {delta:.4f} < {cfg.min_improvement}",
                )

        # 8. Default rerun (no specific targets → no preservation)
        return QueenDecision(
            action="rerun",
            rerun_dimensions=rerun_hint or [],
            reason="default rerun",
        )
