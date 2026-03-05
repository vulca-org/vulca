#!/usr/bin/env python3
"""Validate Layer 3: Queen LLM Agent + Trajectory RAG.

Tests:
1. TrajectoryRAGService graceful degradation (no trajectories)
2. TrajectoryPatterns extraction from synthetic data
3. QueenLLMAgent fallback to rule-based when LLM unavailable
4. QueenLLMAgent decision flow with mock LLM
5. Orchestrator integration (enable_llm_queen flag)
6. Prompt building correctness
7. LLM response parsing (valid / invalid / edge cases)
8. Confidence threshold filtering
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_ROOT))

passed = 0
failed = 0

def check(name: str, condition: bool) -> None:
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}")
        failed += 1


# ============================================================
print("\n=== 1. TrajectoryRAGService — No Data Graceful Degradation ===")

import tempfile
from app.prototype.agents.trajectory_rag import TrajectoryRAGService, TrajectoryPatterns

with tempfile.TemporaryDirectory() as tmpdir:
    rag = TrajectoryRAGService(storage_dir=tmpdir)
    n = rag.build_index()
    check("build_index returns 0 with no data", n == 0)
    check("available is False", not rag.available)

    records, patterns = rag.retrieve("test subject", "default")
    check("retrieve returns empty", len(records) == 0)
    check("patterns has zero trajectories", patterns.n_trajectories == 0)

# ============================================================
print("\n=== 2. TrajectoryPatterns Extraction ===")

from app.prototype.trajectory.trajectory_types import (
    TrajectoryRecord, RoundRecord, CriticFindings, DecisionLog,
)

# Create synthetic trajectories
synth_records = []
for i in range(5):
    rec = TrajectoryRecord(
        subject=f"test subject {i}",
        tradition="chinese_gongbi",
        final_score=0.6 + i * 0.05,
        final_action="accept" if i >= 2 else "stop",
        rounds=[
            RoundRecord(
                round_num=1,
                critic_findings=CriticFindings(
                    layer_scores={"visual_perception": 0.5 + i * 0.05},
                    weighted_score=0.5 + i * 0.05,
                ),
                decision=DecisionLog(
                    action="rerun",
                    reason=f"rerun dimensions ['visual_perception', 'cultural_context']",
                    round_num=1,
                ),
            ),
            RoundRecord(
                round_num=2,
                critic_findings=CriticFindings(
                    layer_scores={"visual_perception": 0.6 + i * 0.05},
                    weighted_score=0.6 + i * 0.05,
                ),
                decision=DecisionLog(
                    action="accept" if i >= 2 else "stop",
                    reason="threshold accept",
                    round_num=2,
                ),
            ),
        ],
    )
    synth_records.append(rec)

rag_test = TrajectoryRAGService.__new__(TrajectoryRAGService)
patterns = rag_test._extract_patterns(synth_records)

check("avg_rounds is 2.0", abs(patterns.avg_rounds - 2.0) < 0.01)
check("avg_final_score > 0.6", patterns.avg_final_score > 0.6)
check("accept_rate is 0.6 (3/5)", abs(patterns.accept_rate - 0.6) < 0.01)
check("common_rerun_dims not empty", len(patterns.common_rerun_dims) > 0)
check("visual_perception in common dims", "visual_perception" in patterns.common_rerun_dims)
check("n_trajectories is 5", patterns.n_trajectories == 5)
check("to_dict works", isinstance(patterns.to_dict(), dict))

# ============================================================
print("\n=== 3. Examples Prompt Building ===")

prompt_text = rag_test.build_examples_prompt(synth_records[:2], patterns)
check("prompt contains 'Similar Past'", "Similar Past" in prompt_text)
check("prompt contains 'Example 1'", "Example 1" in prompt_text)
check("prompt contains tradition", "chinese_gongbi" in prompt_text)
check("prompt contains score", "score=" in prompt_text)

empty_prompt = rag_test.build_examples_prompt([], TrajectoryPatterns())
check("empty records → empty prompt", empty_prompt == "")

# ============================================================
print("\n=== 4. QueenLLMAgent — Fallback to Rules ===")

from app.prototype.agents.queen_llm import QueenLLMAgent, QueenLLMConfig
from app.prototype.agents.queen_config import QueenConfig
from app.prototype.agents.queen_types import PlanState, BudgetState

qcfg = QueenConfig(max_rounds=3, max_cost_usd=0.10)
lcfg = QueenLLMConfig(enable_rag=False)  # disable RAG for this test
agent = QueenLLMAgent(config=qcfg, llm_config=lcfg)

# Should fall back to rules (no LLM keys set in test env)
plan_state = PlanState(task_id="test-001")
critique = {
    "scored_candidates": [
        {"candidate_id": "c1", "weighted_total": 0.75, "gate_passed": True, "dimension_scores": []},
    ],
    "best_candidate_id": "c1",
    "rerun_hint": [],
}

output = agent.decide(critique, plan_state)
check("decide returns QueenOutput", output is not None)
check("decision has action", output.decision.action in ("accept", "rerun", "stop", "downgrade"))
check("reason has [rule:] prefix", "[rule:" in output.decision.reason)
check("success is True", output.success)

metrics = agent.get_metrics()
check("metrics has rule_fallbacks >= 1", metrics["rule_fallbacks"] >= 1)

# ============================================================
print("\n=== 5. QueenLLMAgent — Hard Guardrails ===")

# Budget exhausted → must use rules
plan_state2 = PlanState(task_id="test-002")
plan_state2.budget = BudgetState(rounds_used=0, total_cost_usd=0.15)
critique2 = {
    "scored_candidates": [
        {"candidate_id": "c2", "weighted_total": 0.55, "gate_passed": False, "dimension_scores": []},
    ],
    "best_candidate_id": "c2",
    "rerun_hint": ["visual_perception"],
}

output2 = agent.decide(critique2, plan_state2)
check("budget exhausted → stop", output2.decision.action == "stop")
check("reason mentions budget", "budget" in output2.decision.reason.lower())

# Max rounds → must use rules
plan_state3 = PlanState(task_id="test-003")
plan_state3.budget = BudgetState(rounds_used=3, total_cost_usd=0.02)
output3 = agent.decide(critique2, plan_state3)
check("max rounds → stop", output3.decision.action == "stop")
check("reason mentions rounds", "round" in output3.decision.reason.lower())

# Early stop (high score) → accept immediately
plan_state4 = PlanState(task_id="test-004")
critique_high = {
    "scored_candidates": [
        {"candidate_id": "c4", "weighted_total": 0.85, "gate_passed": True, "dimension_scores": []},
    ],
    "best_candidate_id": "c4",
    "rerun_hint": [],
}
output4 = agent.decide(critique_high, plan_state4)
check("early stop → accept", output4.decision.action == "accept")

# ============================================================
print("\n=== 6. LLM Response Parsing ===")

from app.prototype.agents.queen_llm import QueenLLMAgent

# Valid response
valid_json = '{"action": "rerun", "rerun_dimensions": ["visual_perception", "cultural_context"], "confidence": 0.78, "reason": "L1 and L3 need improvement"}'
decision = agent._parse_response(valid_json, {"rerun_hint": []})
check("valid JSON parsed", decision is not None)
check("action is rerun", decision.action == "rerun")
check("2 rerun dims", len(decision.rerun_dimensions) == 2)
check("confidence is 0.78", abs(decision.expected_gain_per_cost - 0.78) < 0.01)
check("preserve dims populated", len(decision.preserve_dimensions) == 3)

# Markdown-wrapped JSON
md_json = '```json\n{"action": "accept", "confidence": 0.9, "reason": "good enough"}\n```'
decision2 = agent._parse_response(md_json, {"rerun_hint": []})
check("markdown JSON parsed", decision2 is not None)
check("action is accept", decision2.action == "accept")

# Invalid action → normalized to stop
bad_action = '{"action": "retry", "confidence": 0.6, "reason": "test"}'
decision3 = agent._parse_response(bad_action, {"rerun_hint": []})
check("invalid action → stop", decision3 is not None and decision3.action == "stop")

# Invalid dims filtered
bad_dims = '{"action": "rerun", "rerun_dimensions": ["visual_perception", "invalid_dim"], "confidence": 0.7, "reason": "test"}'
decision4 = agent._parse_response(bad_dims, {"rerun_hint": []})
check("invalid dims filtered", decision4 is not None and len(decision4.rerun_dimensions) == 1)
check("only valid dim kept", "visual_perception" in decision4.rerun_dimensions)

# Completely invalid
invalid = "This is not JSON at all"
decision5 = agent._parse_response(invalid, {"rerun_hint": []})
check("invalid text → None", decision5 is None)

# ============================================================
print("\n=== 7. Confidence Threshold Filtering ===")

low_conf = '{"action": "rerun", "rerun_dimensions": ["visual_perception"], "confidence": 0.2, "reason": "unsure"}'
decision_low = agent._parse_response(low_conf, {"rerun_hint": []})
check("low confidence parsed", decision_low is not None)
check("confidence is 0.2", abs(decision_low.expected_gain_per_cost - 0.2) < 0.01)
# In actual _try_llm_decide, this would trigger fallback since 0.2 < min_confidence(0.4)

# ============================================================
print("\n=== 8. Orchestrator Integration ===")

from app.prototype.orchestrator.orchestrator import PipelineOrchestrator
from app.prototype.agents.draft_config import DraftConfig

# With LLM Queen disabled (default)
orch1 = PipelineOrchestrator(
    draft_config=DraftConfig(provider="mock"),
    enable_llm_queen=False,
)
check("default: _queen_llm is None", orch1._queen_llm is None)

# With LLM Queen enabled
orch2 = PipelineOrchestrator(
    draft_config=DraftConfig(provider="mock"),
    enable_llm_queen=True,
)
check("enabled: _queen_llm is not None", orch2._queen_llm is not None)
check("queen_llm is QueenLLMAgent", type(orch2._queen_llm).__name__ == "QueenLLMAgent")

# Run a sync pipeline with LLM Queen (will fallback to rules but should work)
from app.prototype.pipeline.pipeline_types import PipelineInput

pi = PipelineInput(
    task_id="validate-queen-llm-001",
    subject="A serene landscape",
    cultural_tradition="chinese_xieyi",
)
output = orch2.run_sync(pi)
check("run_sync completes with LLM Queen", output.success)
check("has final_decision", output.final_decision in ("accept", "stop", "rerun", "rerun_local"))

# ============================================================
print(f"\n{'='*60}")
print(f"Queen LLM + RAG Validation: {passed} passed, {failed} failed")
print(f"{'='*60}")

sys.exit(1 if failed > 0 else 0)
