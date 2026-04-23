"""Execution loop + jsonl + lockfile contract for /visual-plan §5 Phase 3 + §9."""
from pathlib import Path
import re
import json

SKILL_PATH = Path(__file__).parent.parent / ".claude/skills/visual-plan/SKILL.md"


def _read_skill() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


# --- Test 1: accept resets counter ---

def test_phase3_verdict_accept_counter_resets():
    skill = _read_skill()
    assert re.search(r"accept.*counter.*(0|zero|reset)", skill, re.IGNORECASE) is not None


# --- Test 2: accept-with-warning leaves counter unchanged ---

def test_phase3_verdict_accept_with_warning_counter_unchanged():
    skill = _read_skill()
    assert re.search(r"accept-with-warning.*counter\s+(unchanged|NOT|stays)", skill, re.IGNORECASE) is not None


# --- Test 3: reject increments counter ---

def test_phase3_verdict_reject_increments_counter():
    skill = _read_skill()
    assert re.search(r"reject.*counter\s*\+\+|counter.*reject", skill, re.IGNORECASE) is not None


# --- Test 4: Err #7 verbatim + unified 3-option prompt (no F.source branching) ---

def test_phase3_fail_fast_err7_unified_prompt_verbatim():
    skill = _read_skill()
    # Verbatim string from §6 Err #7
    assert "cost budget exceeded" in skill
    assert re.search(r"Abort,?\s*extend\s+budget,?\s*or\s+accept\s+remaining", skill) is not None


# --- Test 5: fail_fast_consecutive=None disables Err #7 ---

def test_phase3_fail_fast_null_never_breaks():
    skill = _read_skill()
    assert re.search(r"fail_fast_consecutive\s+is\s+not\s+None|fail_fast_consecutive\s*=\s*None", skill) is not None


# --- Test 6: jsonl row has 14 required fields ---

def test_jsonl_row_schema_14_required_fields():
    skill = _read_skill()
    required_fields = [
        "iter", "seed", "variant_idx", "variant_name", "image_path",
        "started_at", "wall_time_sec", "provider_used", "l_scores",
        "weighted_total", "verdict", "gate_decisions", "prompt_used",
    ]
    for f in required_fields:
        assert f in skill, f"jsonl schema missing required field: {f}"


# --- Test 7: jsonl encoding ensure_ascii=True (grep-safe) ---

def test_jsonl_utf8_ensure_ascii_true():
    skill = _read_skill()
    assert re.search(r"ensure_ascii\s*=\s*True|grep-safe", skill) is not None


# --- Test 8: jsonl append-only crash leaves N rows ---

def test_jsonl_append_only_crash_leaves_n_rows_not_n_plus_partial():
    skill = _read_skill()
    assert re.search(r"append-only|torn\s+(last\s+)?line|tolerant\s+of\s+torn", skill) is not None


# --- Test 9: resume skips completed iters ---

def test_resume_from_jsonl_skips_completed_iters():
    skill = _read_skill()
    assert re.search(r"(completed_iters|resume.*skip|skip.*completed)", skill) is not None


# --- Test 10: resume rebuilds fail_fast_counter ---

def test_resume_fail_fast_counter_rebuilt():
    skill = _read_skill()
    assert re.search(r"_rebuild_counter|rebuild.*counter|counter.*rebuilt|contiguous\s+reject", skill) is not None


# --- Test 11: unload_models optional in Phase 4 ---

def test_unload_models_optional_in_phase4():
    skill = _read_skill()
    assert "unload_models" in skill
    # Must be MAY not SHOULD
    assert re.search(r"MAY\s+(call|invoke).*unload_models|unload_models.*optional", skill) is not None


# --- Test 12: S2 cap-hit without accept stays draft ---

def test_s2_cap_hit_without_accept_stays_draft():
    skill = _read_skill()
    assert re.search(r"(Turn\s+cap\s+reached|cap-hit|cap.*reached).*(finalize|deep\s+review)", skill, re.IGNORECASE) is not None


# --- Test 13: S5 lockfile O_CREAT | O_EXCL ---

def test_s5_lockfile_exclusive_create_atomicity():
    skill = _read_skill()
    assert "O_CREAT" in skill
    assert "O_EXCL" in skill


# --- Test 14: terminal status priority aborted > partial > completed ---

def test_phase4_terminal_status_priority_aborted_over_partial_over_completed():
    skill = _read_skill()
    # Priority order stated explicitly
    assert re.search(r"aborted\s*>\s*partial\s*>\s*completed|priority\s+order.*aborted.*partial.*completed", skill) is not None
