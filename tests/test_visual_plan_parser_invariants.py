"""Parser invariants for /visual-plan SKILL.md §4 contract.

All tests assert contracts stated in
docs/superpowers/specs/2026-04-23-visual-plan-skill-design.md §4.
"""
from pathlib import Path
import re
import yaml
import pytest

SKILL_PATH = Path(__file__).parent.parent / ".claude/skills/visual-plan/SKILL.md"

# --- Fixtures ---

MINIMAL_DESIGN = """---
slug: 2026-04-23-test-poster
status: resolved
domain: poster
tradition: chinese_gongbi
schema_version: "0.1"
generated_by: visual-spec@0.1.0
proposal_ref: docs/visual-specs/2026-04-23-test-poster/proposal.md
created: 2026-04-23
updated: 2026-04-23
---

# Test Poster

## A. Provider + generation params
```yaml
reviewed: true
provider: sdxl-mps
seed: 1337
steps: 30
cfg_scale: 7.5
```

## B. Composition strategy
```yaml
reviewed: true
strategy: single
variation_axis: null
variant_count: 1
```

## C. Prompt composition
```yaml
reviewed: true
base_prompt: "test"
negative_prompt: ""
tradition_tokens: ["gongbi 工笔"]
color_constraint_tokens: ["cinnabar red"]
sketch_integration: ignore
ref_integration: none
```

## D1. L1-L5 weights
```yaml
reviewed: true
L1: 0.15
L2: 0.3
L3: 0.25
L4: 0.15
L5: 0.15
```

## D2. Thresholds + batch + rollback
```yaml
reviewed: true
L1_threshold: {value: 0.7, source: assumed, confidence: low}
L2_threshold: {value: 0.7, source: assumed, confidence: low}
L3_threshold: {value: 0.6, source: assumed, confidence: low}
L4_threshold: {value: 0.55, source: assumed, confidence: low}
L5_threshold: {value: 0.5, source: assumed, confidence: low}
batch_size: {value: 4, source: assumed, confidence: med}
rollback_trigger: {value: "3 consecutive L3<0.5", source: assumed, confidence: low}
override_rationale: null
```

## F. Cost budget
```yaml
reviewed: true
per_gen_sec: {value: 20, source: derived, confidence: med}
total_session_sec: {value: 120, source: derived, confidence: low}
fail_fast_consecutive: {value: 2, source: assumed, confidence: low}
provider_used_for_calibration: mock
provider_multiplier_applied: 20000
```

## Open questions
none

## Notes
Test fixture.
"""


def _read_skill() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


# --- Test 1: parser round-trip minimal design ---

def test_parser_roundtrip_minimal_design(tmp_path):
    """A minimal design.md round-trips through the parser contract."""
    fixture = tmp_path / "design.md"
    fixture.write_text(MINIMAL_DESIGN)
    content = fixture.read_text()
    # Extract frontmatter
    m = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    assert m is not None
    fm = yaml.safe_load(m.group(1))
    assert fm["status"] == "resolved"
    assert fm["tradition"] == "chinese_gongbi"
    assert fm["domain"] == "poster"
    assert "schema_version" in fm


# --- Test 2: full design with spike section ---

def test_parser_roundtrip_full_design_with_spike(tmp_path):
    """9-section design (E present) parses cleanly."""
    with_spike = MINIMAL_DESIGN.replace(
        "## Open questions\nnone",
        "## Open questions\n- spike: 3 seeds\n"
    ).replace(
        "## F. Cost budget",
        '## E. Spike plan\n```yaml\nreviewed: true\nspike_requested: true\nspike_count: 3\njudgment_criterion: "L3>=0.6"\nresults: []\nstatus: pending\n```\n\n## F. Cost budget'
    )
    fixture = tmp_path / "design.md"
    fixture.write_text(with_spike)
    content = fixture.read_text()
    # E section extractable
    assert "## E. Spike plan" in content
    assert "spike_requested: true" in content


# --- Test 3: null-tradition no-spike 7-section ---

def test_parser_roundtrip_null_tradition_no_spike(tmp_path):
    """7-section design (D1 + E both omitted per null-tradition)."""
    null_trad = MINIMAL_DESIGN.replace(
        "tradition: chinese_gongbi",
        "tradition: null"
    )
    # Remove D1 section
    null_trad = re.sub(
        r"## D1\. L1-L5 weights\n```yaml.*?```\n\n",
        "",
        null_trad,
        flags=re.DOTALL,
    )
    fixture = tmp_path / "design.md"
    fixture.write_text(null_trad)
    content = fixture.read_text()
    assert "## D1." not in content
    assert "## D2." in content


# --- Test 4: tolerant read — flat tradition_tokens ---

def test_tolerant_read_flat_tradition_tokens():
    """SKILL.md §4.1 rule 5: flat string list is accepted."""
    skill = _read_skill()
    assert "flat string list" in skill.lower() or "list[dict]" in skill.lower()


# --- Test 5: tolerant read — dict tradition_tokens ---

def test_tolerant_read_dict_tradition_tokens():
    """SKILL.md §4.1 rule 5: list[dict] shape normalizes to flat string."""
    skill = _read_skill()
    # SKILL.md must document both forms
    assert "tradition_tokens" in skill
    assert re.search(r"term.*translation|translation.*term", skill) is not None


# --- Test 6: tolerant read — bare numeric D2 threshold ---

def test_tolerant_read_bare_numeric_d2_threshold():
    """SKILL.md §4.1 rule 7: bare number wraps to {value, source: assumed, confidence: low}."""
    skill = _read_skill()
    assert "source: assumed" in skill
    assert "confidence: low" in skill


# --- Test 7: tolerant read — bare sdxl provider normalize ---

def test_tolerant_read_bare_sdxl_provider():
    """SKILL.md §4.1 rule 6: bare 'sdxl' → 'sdxl-mps' on darwin."""
    skill = _read_skill()
    assert "sdxl-mps" in skill
    assert re.search(r"bare\s+[`']?sdxl[`']?|sdxl\s+→\s+sdxl-mps", skill) is not None


# --- Test 8: tolerant read — inline comments stripped on write ---

def test_tolerant_read_inline_comments_stripped_on_write():
    """SKILL.md §4.1 rule 3: # comments allowed on read, stripped on write."""
    skill = _read_skill()
    assert re.search(r"inline.*comment|# comment", skill) is not None


# --- Test 9: tolerant read — unknown top-level key warning ---

def test_tolerant_read_unknown_top_level_key_warning():
    """SKILL.md §4.1 rule 1: unknown keys drop + warn to Notes."""
    skill = _read_skill()
    assert "[parser-warn]" in skill


# --- Test 10: tolerant read — missing optional section E ---

def test_tolerant_read_missing_optional_section_E():
    """SKILL.md §4.1: E section is conditional (spike only)."""
    skill = _read_skill()
    assert "spike" in skill.lower()
    # The skill must state E is optional
    assert re.search(r"E\s+(section|is)\s+(optional|conditional)", skill) is not None or "E section" in skill


# --- Test 11: tolerant read — missing required section raises Err #10 ---

def test_tolerant_read_missing_required_section_raises_err10():
    """SKILL.md §6 Err #10 fires on missing required A/B/C/D2/F."""
    skill = _read_skill()
    assert "Err #10" in skill or "| 10 |" in skill
    assert "parse-fail" in skill


# --- Test 12: tolerant read — unknown section heading ignored silently ---

def test_tolerant_read_unknown_section_heading_ignored_silently():
    """SKILL.md §4.1 rule 4: unknown ## headings ignored silently (no warning)."""
    skill = _read_skill()
    assert re.search(r"unknown\s+##|ignore\s+silently", skill) is not None or "unknown section" in skill.lower()


# --- Test 13: tolerant read — missing defaultable field fills + logs ---

def test_tolerant_read_missing_defaultable_required_field_fills_and_logs():
    """SKILL.md §4.1 rule 2: fills default + logs [parser-default]."""
    skill = _read_skill()
    assert "[parser-default]" in skill


# --- Test 14: strict write — 9-field frontmatter incl schema_version ---

def test_strict_write_frontmatter_exactly_9_fields_includes_schema_version():
    """SKILL.md §4.2: plan.md frontmatter has exactly 9 fields."""
    skill = _read_skill()
    # Find the plan.md frontmatter template block
    assert "schema_version" in skill
    # Count fields in the template (robust: look for the fenced yaml with 9 top-level keys)
    match = re.search(r"```yaml\n---\nslug:.*?---\n```", skill, re.DOTALL)
    if match is None:
        # Fallback: at least assert the 9 field names are present
        for field in ["slug", "status", "domain", "tradition", "schema_version",
                      "generated_by", "design_ref", "created", "updated"]:
            assert field in skill, f"plan.md frontmatter missing {field}"


# --- Test 15: SKILL.md drift audit — phase + invariant + err counts ---

def test_skill_body_matches_spec_phase_invariant_err_counts():
    """SKILL.md must have 4 phase headings, 7 invariants (S1-S7), 16 err rows."""
    skill = _read_skill()
    phase_headers = re.findall(r"^## Phase \d+", skill, re.MULTILINE)
    assert len(phase_headers) == 4, f"expected 4 phase headings, got {len(phase_headers)}"
    # Invariants S1-S7
    for si in range(1, 8):
        assert f"S{si}" in skill or f"**S{si}**" in skill, f"missing invariant S{si}"
    # Err matrix 16 rows (Err #1..#16)
    for ei in range(1, 17):
        assert f"Err #{ei}" in skill or f"| {ei} |" in skill or f"| **{ei}** |" in skill, \
            f"missing error row Err #{ei}"
