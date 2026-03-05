#!/usr/bin/env python3
"""D7 validation — Queen Agent decision logic.

Usage::

    cd wenxin-backend
    python3 app/prototype/tools/validate_queen.py

Exit code 0 = ALL CHECKS PASSED, 1 = failures detected.
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from app.prototype.agents.queen_agent import QueenAgent  # noqa: E402
from app.prototype.agents.queen_config import QueenConfig  # noqa: E402
from app.prototype.agents.queen_types import (  # noqa: E402
    BudgetState,
    PlanState,
    QueenDecision,
    QueenOutput,
)

# ---------------------------------------------------------------------------
passed = 0
failed = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {label}")
    else:
        failed += 1
        msg = f"  [FAIL] {label}"
        if detail:
            msg += f" — {detail}"
        print(msg)


def _mock_critique(
    weighted_total: float,
    gate_passed: bool,
    rerun_hint: list[str] | None = None,
    n_candidates: int = 4,
) -> dict:
    """Build a minimal CritiqueOutput dict for Queen testing."""
    candidates = []
    for i in range(n_candidates):
        candidates.append({
            "candidate_id": f"draft-test-{i}",
            "weighted_total": weighted_total if i == 0 else weighted_total * 0.9,
            "gate_passed": gate_passed if i == 0 else False,
            "risk_tags": [],
            "rejected_reasons": [] if (gate_passed and i == 0) else ["test"],
        })
    return {
        "task_id": "test",
        "scored_candidates": candidates,
        "best_candidate_id": "draft-test-0" if gate_passed else None,
        "rerun_hint": rerun_hint or [],
        "success": True,
    }


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

def test_case_1_early_stop() -> None:
    """Case 1: High score first round (0.95) → accept (early stop)."""
    print(f"\n{'='*60}")
    print("  Case 1: High score first round → ACCEPT (early stop)")
    print(f"{'='*60}")

    queen = QueenAgent()
    critique = _mock_critique(weighted_total=0.95, gate_passed=True)
    plan = PlanState(task_id="d7-case1")

    out = queen.decide(critique, plan)

    check("decision.action == 'accept'", out.decision.action == "accept")
    check("reason mentions 'early stop'", "early stop" in out.decision.reason)
    check("plan_state.budget.rounds_used == 1", out.plan_state.budget.rounds_used == 1)
    check("success == True", out.success)
    check("to_dict() round-trips", "decision" in out.to_dict())
    check("QueenOutput has task_id", out.task_id == "d7-case1")


def test_case_2_threshold_accept() -> None:
    """Case 2: Medium score first round (0.65) → accept (threshold)."""
    print(f"\n{'='*60}")
    print("  Case 2: Medium score first round → ACCEPT (threshold)")
    print(f"{'='*60}")

    # Need config where 0.65 is above accept but below early_stop
    queen = QueenAgent(config=QueenConfig(
        accept_threshold=0.6,
        early_stop_threshold=0.8,
        mock_cost_per_round=0.01,
    ))
    critique = _mock_critique(weighted_total=0.65, gate_passed=True)
    plan = PlanState(task_id="d7-case2")

    out = queen.decide(critique, plan)

    check("decision.action == 'accept'", out.decision.action == "accept")
    check("reason mentions 'threshold accept'", "threshold accept" in out.decision.reason)
    check("budget cost == 0.01", abs(out.plan_state.budget.total_cost_usd - 0.01) < 1e-9)


def test_case_3_rerun_with_hint() -> None:
    """Case 3: Low score + rerun_hint → rerun."""
    print(f"\n{'='*60}")
    print("  Case 3: Low score + rerun_hint → RERUN")
    print(f"{'='*60}")

    queen = QueenAgent(config=QueenConfig(max_rounds=3))
    critique = _mock_critique(
        weighted_total=0.35,
        gate_passed=False,
        rerun_hint=["cultural_context", "critical_interpretation"],
    )
    plan = PlanState(task_id="d7-case3")

    out = queen.decide(critique, plan)

    check("decision.action == 'rerun'", out.decision.action == "rerun")
    check(
        "rerun_dimensions includes cultural_context",
        "cultural_context" in out.decision.rerun_dimensions,
    )
    check(
        "rerun_dimensions includes critical_interpretation",
        "critical_interpretation" in out.decision.rerun_dimensions,
    )
    check("pending_dimensions updated", len(out.plan_state.pending_dimensions) == 2)


def test_case_4_over_budget() -> None:
    """Case 4: Over budget → stop."""
    print(f"\n{'='*60}")
    print("  Case 4: Over budget → STOP")
    print(f"{'='*60}")

    queen = QueenAgent(config=QueenConfig(max_cost_usd=0.05, mock_cost_per_round=0.03, max_rounds=10))
    critique = _mock_critique(weighted_total=0.35, gate_passed=False)

    # Round 1: cost=0.03 (< 0.05, under budget)
    plan = PlanState(task_id="d7-case4")
    out1 = queen.decide(critique, plan)

    # Round 2: cost=0.06 (>= 0.05, over budget)
    out2 = queen.decide(critique, plan)

    check("round 2: action == 'stop'", out2.decision.action == "stop")
    check("reason mentions 'budget'", "budget" in out2.decision.reason)
    check("total_cost >= max_cost", out2.plan_state.budget.total_cost_usd >= 0.05)


def test_case_5_over_rounds() -> None:
    """Case 5: Over rounds → stop."""
    print(f"\n{'='*60}")
    print("  Case 5: Over rounds → STOP")
    print(f"{'='*60}")

    queen = QueenAgent(config=QueenConfig(max_rounds=2, max_cost_usd=1.0))
    critique = _mock_critique(weighted_total=0.35, gate_passed=False, rerun_hint=["cultural_context"])

    plan = PlanState(task_id="d7-case5")

    # Round 1: should rerun (under max_rounds, has hint)
    out1 = queen.decide(critique, plan)
    check("round 1: action == 'rerun'", out1.decision.action == "rerun")

    # Round 2: rounds_used=2 >= max_rounds=2 → stop
    out2 = queen.decide(critique, plan)
    check("round 2: action == 'stop'", out2.decision.action == "stop")
    check("reason mentions 'max rounds'", "max rounds" in out2.decision.reason)
    check("rounds_used == 2", plan.budget.rounds_used == 2)


def test_case_6_high_cost_rerun() -> None:
    """Case 6: High cost but under max → rerun (downgrade removed in R14)."""
    print(f"\n{'='*60}")
    print("  Case 6: High cost → RERUN (downgrade removed)")
    print(f"{'='*60}")

    queen = QueenAgent(config=QueenConfig(
        max_cost_usd=0.10,
        max_rounds=5,
        mock_cost_per_round=0.02,
    ))
    critique = _mock_critique(weighted_total=0.35, gate_passed=False, rerun_hint=["cultural_context"])

    # Pre-load budget to 0.07 so after +0.02 = 0.09 (under max 0.10)
    plan = PlanState(
        task_id="d7-case6",
        budget=BudgetState(rounds_used=3, total_cost_usd=0.07),
    )

    out = queen.decide(critique, plan)

    # With downgrade removed, Queen should rerun (rerun_hint present, rounds < max)
    check("action == 'rerun'", out.decision.action == "rerun")
    check("rerun_dimensions includes cultural_context", "cultural_context" in out.decision.rerun_dimensions)


def test_case_7_data_contracts() -> None:
    """Case 7: Verify all data contracts and to_dict() methods."""
    print(f"\n{'='*60}")
    print("  Case 7: Data contracts and serialization")
    print(f"{'='*60}")

    # BudgetState
    bs = BudgetState(rounds_used=2, total_cost_usd=0.04, candidates_generated=8, critic_calls=2)
    bs_d = bs.to_dict()
    check("BudgetState.to_dict() has all keys", set(bs_d.keys()) == {
        "rounds_used", "total_cost_usd", "candidates_generated", "critic_calls",
        "llm_calls", "tool_calls",
    })

    # PlanState
    ps = PlanState(task_id="test", budget=bs)
    ps_d = ps.to_dict()
    check("PlanState.to_dict() has all keys", set(ps_d.keys()) == {
        "task_id", "current_round", "confirmed_dimensions", "pending_dimensions", "budget", "history",
        "human_locked_dimensions", "human_override_history",
        "layer_states", "intent_card", "cross_layer_signals", "local_rerun_request",
    })

    # QueenDecision
    qd = QueenDecision(action="rerun", rerun_dimensions=["L3"], reason="test")
    qd_d = qd.to_dict()
    check("QueenDecision.to_dict() has all keys", set(qd_d.keys()) == {
        "action", "rerun_dimensions", "preserve_dimensions",
        "reason", "expected_gain_per_cost",
    })

    # QueenOutput
    qo = QueenOutput(task_id="test", decision=qd, plan_state=ps)
    qo_d = qo.to_dict()
    check("QueenOutput.to_dict() has all keys", set(qo_d.keys()) == {
        "task_id", "decision", "plan_state", "created_at", "latency_ms", "success", "error",
    })

    # JSON round-trip
    import json
    check("QueenOutput JSON round-trips", json.loads(json.dumps(qo_d)) == qo_d)

    # QueenConfig
    from app.prototype.agents.queen_config import QueenConfig
    cfg = QueenConfig()
    cfg_d = cfg.to_dict()
    check("QueenConfig.to_dict() has all keys", set(cfg_d.keys()) == {
        "max_rounds", "max_cost_usd", "accept_threshold", "early_stop_threshold",
        "min_improvement", "mock_cost_per_round",
    })


def test_case_8_history_tracking() -> None:
    """Case 8: Verify history accumulation across rounds."""
    print(f"\n{'='*60}")
    print("  Case 8: History tracking across rounds")
    print(f"{'='*60}")

    queen = QueenAgent(config=QueenConfig(max_rounds=3, max_cost_usd=1.0))
    plan = PlanState(task_id="d7-case8")

    # Round 1: low score, no rerun hint
    crit1 = _mock_critique(weighted_total=0.3, gate_passed=False, rerun_hint=[])
    out1 = queen.decide(crit1, plan)
    check("round 1: history length == 1", len(plan.history) == 1)
    check("round 1: history[0].round == 1", plan.history[0]["round"] == 1)

    # Round 2: slightly better, no rerun hint — improvement 0.02 < 0.05 → stop
    crit2 = _mock_critique(weighted_total=0.32, gate_passed=False, rerun_hint=[])
    out2 = queen.decide(crit2, plan)
    check("round 2: history length == 2", len(plan.history) == 2)
    check("round 2: history[1].round == 2", plan.history[1]["round"] == 2)

    # Round 2 improvement is 0.02 < 0.05 min_improvement → should stop
    check("round 2: stop due to insufficient improvement", out2.decision.action == "stop")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    global passed, failed

    print("=" * 60)
    print("  D7 Queen Agent Validation")
    print("=" * 60)

    test_case_1_early_stop()
    test_case_2_threshold_accept()
    test_case_3_rerun_with_hint()
    test_case_4_over_budget()
    test_case_5_over_rounds()
    test_case_6_downgrade()
    test_case_7_data_contracts()
    test_case_8_history_tracking()

    print(f"\n{'='*60}")
    total = passed + failed
    print(f"  Results: {passed}/{total} checks passed, {failed} failed")
    if failed == 0:
        print("  ALL CHECKS PASSED")
    else:
        print("  SOME CHECKS FAILED")
    print("=" * 60)
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
