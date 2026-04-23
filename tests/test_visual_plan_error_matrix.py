"""Error matrix + invariants + handoff verbatim contracts for /visual-plan §6/§7/§2."""
from pathlib import Path
import re

SKILL_PATH = Path(__file__).parent.parent / ".claude/skills/visual-plan/SKILL.md"


def _read_skill() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


# --- Err #1 verbatim ---

def test_err1_verbatim_string():
    skill = _read_skill()
    assert "design.md not found or status != resolved" in skill
    assert "Run /visual-spec <slug> first" in skill


# --- Err #2 refuse overwrite ---

def test_err2_refuse_overwrite_terminal_states():
    skill = _read_skill()
    assert re.search(r"already\s+(completed|<status>|\w+)\s+at\s+<?path>?", skill) is not None
    assert "branch with -v2" in skill


# --- Err #3 resume replays jsonl ---

def test_err3_resume_replays_jsonl():
    skill = _read_skill()
    assert re.search(r"Err\s*#?3.*Resume|Resume.*Err\s*#?3", skill, re.DOTALL) is not None
    assert "turns_used" in skill


# --- Err #3 + Err #12 collision fold (Blocker B5 fix) ---

def test_err3_plus_err12_collision_folds_recovery_into_resume():
    skill = _read_skill()
    # Must explicitly state the fold rule
    assert re.search(r"(fold|absorb).*Err\s*#?12|stale.*lockfile.*resume", skill, re.IGNORECASE) is not None


# --- Err #4 frontmatter violation ---

def test_err4_verbatim_string_frontmatter_violation():
    skill = _read_skill()
    assert "design.md frontmatter violation" in skill
    assert "Re-run /visual-spec <slug> to fix" in skill


# --- Err #5 hands off to Err #13 ---

def test_err5_hands_off_to_err13_no_auto_failover():
    skill = _read_skill()
    assert re.search(r"Err\s*#?5.*(hand.*off|hands\s+to)|no\s+auto-failover", skill, re.IGNORECASE) is not None


# --- Err #6 per-iter failed continues ---

def test_err6_per_iter_failed_continues_and_all_fail_becomes_partial():
    skill = _read_skill()
    assert re.search(r"verdict:\s*failed", skill) is not None
    assert re.search(r"(all[_-]?fail|all\s+iters\s+fail).*partial", skill, re.IGNORECASE) is not None


# --- Err #7 verbatim + 3-option branches ---

def test_err7_verbatim_string_and_three_option_branch():
    skill = _read_skill()
    assert "cost budget exceeded" in skill
    # 3 branch outcomes (unified per post-review)
    assert re.search(r"\(a\).*abort", skill, re.IGNORECASE) is not None
    assert re.search(r"\(b\).*extend", skill, re.IGNORECASE) is not None
    assert re.search(r"\(c\).*accept.*remaining", skill, re.IGNORECASE) is not None


# --- Err #8 pixel request decline turn not charged ---

def test_err8_pixel_request_decline_turn_not_charged():
    skill = _read_skill()
    assert "plan layer executes pixels in Phase 3 only" in skill
    assert "Turn NOT charged" in skill or "turn NOT charged" in skill


# --- Err #9 sketch degrade ---

def test_err9_sketch_unreadable_degrades_sketch_integration():
    skill = _read_skill()
    assert re.search(r"sketch.*unreadable|sketch_integration.*ignore", skill) is not None


# --- Err #10 parse fail verbatim ---

def test_err10_parse_fail_verbatim_string():
    skill = _read_skill()
    assert "design.md parse-fail" in skill
    assert re.search(r"Re-run\s+/visual-spec\s+<slug>\s+to\s+regenerate", skill) is not None


# --- Err #11 concurrent lockfile refuse ---

def test_err11_concurrent_lockfile_refuses():
    skill = _read_skill()
    assert re.search(r"currently\s+running\s+\(pid:\s*<pid>", skill) is not None
    assert "Abort the other session" in skill or "abort the other session" in skill


# --- Err #12 stale lock writes Notes (not stderr) ---

def test_err12_stale_lock_writes_notes_not_stderr():
    """Per Ruling D fix: stderr was wrong channel; must use Notes + handoff suffix."""
    skill = _read_skill()
    assert "[stale-lock-recovery]" in skill
    # Ensure stderr is NOT the channel
    assert "stderr" not in skill.lower() or re.search(r"NOT\s+stderr|no\s+stderr", skill) is not None


# --- Err #13 cross-class 3 options ---

def test_err13_cross_class_prompt_three_option_outcomes():
    skill = _read_skill()
    assert "cross-class switch" in skill
    # Options a/b/c for cross-class
    assert re.search(r"Approve\?.*\(a\).*yes", skill, re.DOTALL) is not None


# --- Err #14 sentinel ---

def test_err14_sentinel_cwd_check():
    skill = _read_skill()
    assert "not inside a Vulca checkout" in skill


# --- Err #15 schema_version unrecognized ---

def test_err15_schema_version_unrecognized_refuses():
    skill = _read_skill()
    assert "schema_version" in skill
    assert re.search(r"not\s+recognized|upgrade\s+/visual-spec", skill) is not None


# --- Err #16 design hash drift ---

def test_err16_design_hash_drift_aborts_at_iter():
    skill = _read_skill()
    assert re.search(r"design\.md\s+mutated\s+mid-session|Err\s*#?16", skill) is not None
    assert "[design-drift]" in skill
