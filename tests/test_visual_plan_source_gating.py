"""Source-gating + verdict-tree contract for /visual-plan §8.

All tests assert SKILL.md text contracts for the locked decision (d):
- F assumed → single Phase-2 summary prompt (a/b/c)
- D2 thresholds assumed → passive soft-gate downgrade
- all-zero sentinel → accept-with-warning
"""
from pathlib import Path
import re

SKILL_PATH = Path(__file__).parent.parent / ".claude/skills/visual-plan/SKILL.md"


def _read_skill() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


# --- Test 1: assumed D2 → soft gate_class ---

def test_gating_assumed_d2_becomes_soft():
    skill = _read_skill()
    assert re.search(r"source.*assumed.*soft|assumed\s*→\s*soft|gate_class:\s*soft", skill) is not None
    assert "gate_class" in skill


# --- Test 2: measured D2 → hard gate_class ---

def test_gating_measured_d2_becomes_hard():
    skill = _read_skill()
    assert re.search(r"measured.*hard|measured\s*→\s*hard", skill) is not None


# --- Test 3: user_elevated stays in plan.md, never touches design.md ---

def test_gating_user_elevated_hard_no_design_mutation():
    """Decision #10 post-review (b): user_elevated persists ONLY in plan.md."""
    skill = _read_skill()
    assert "user_elevated" in skill
    # Must explicitly state design.md is NOT mutated
    assert re.search(r"NEVER\s+write.*design\.md|never\s+back-written\s+to\s+design\.md|design\.md\s+untouched|design\.md\s+immutable", skill) is not None


# --- Test 4: F-summary prompt triggered on assumed ---

def test_f_summary_prompt_triggered_on_assumed():
    skill = _read_skill()
    assert "F budget is assumed" in skill or "assumed budget" in skill.lower()


# --- Test 5: F-summary prompt skipped on measured ---

def test_f_summary_prompt_skipped_on_measured():
    """If F is measured/derived, prompt NOT emitted."""
    skill = _read_skill()
    assert re.search(r"(triggered when|fires when|fired when).*assumed", skill) is not None


# --- Test 6: F-summary reply (a) accept keeps assumed flag ---

def test_f_summary_reply_accept_keeps_assumed_flag():
    skill = _read_skill()
    assert re.search(r"user_ack_assumed_budget|ack.*assumed|accept.*assumed", skill) is not None


# --- Test 7: F-summary reply (b) override updates value ---

def test_f_summary_reply_override_updates_value():
    skill = _read_skill()
    assert re.search(r"override\s+<?[a-z_]+>?|source:\s*user-confirmed", skill) is not None


# --- Test 8: F-summary reply (c) skip-budget-check nulls fail_fast ---

def test_f_summary_reply_skip_nulls_fail_fast():
    skill = _read_skill()
    assert re.search(r"skip-budget-check|fail_fast_consecutive\s*=\s*None|fail_fast\s+disabled", skill) is not None


# --- Test 9: verdict hard fail → reject ---

def test_verdict_hard_fail_reject():
    skill = _read_skill()
    # Verdict tree documented
    assert "hard_fails" in skill
    assert re.search(r"reject|return\s+[\"']reject[\"']", skill) is not None


# --- Test 10: verdict soft fail → accept-with-warning, counter unchanged ---

def test_verdict_soft_fail_accept_with_warning_counter_unchanged():
    skill = _read_skill()
    assert "accept-with-warning" in skill
    assert re.search(r"counter\s+(unchanged|NOT\s+bump|stays|preserved)", skill) is not None


# --- Test 11: all-zero scores sentinel → evaluate-suspect + accept-with-warning ---

def test_verdict_all_zero_flags_evaluate_suspect():
    skill = _read_skill()
    assert "[evaluate-suspect]" in skill
    assert re.search(r"all[_-]?zero|all.*L_N.*<\s*0\.01|all\s+five.*<\s*0\.01", skill) is not None
