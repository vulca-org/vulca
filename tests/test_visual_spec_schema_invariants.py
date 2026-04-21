"""Tripwire: /visual-spec design.md output shape must match spec §6.3 schema + §11 invariants.

Tests use inline module-level fixtures (no tests/fixtures/ dir per plan decision 3).
Fixtures are synthetic design.md strings representing canonical output shapes.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# Inline fixture: a canonical resolved design.md (E section present = spike_triggered=true).
RESOLVED_DESIGN_MD = """---
slug: 2026-04-21-test-project-chinese-gongbi
status: resolved
input_proposal: ./proposal.md
generated_by: visual-spec@0.1.0
created: 2026-04-21
updated: 2026-04-21
spike_triggered: true
tradition: chinese_gongbi
---

# Test Project in Chinese Gongbi

## A. Provider + generation params
```yaml
reviewed: true
provider: sdxl
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
base_prompt: "plum blossom branch, song gongbi"
negative_prompt: "blurry, low-res"
tradition_tokens: ["gongbi 工笔", "xuan paper 宣纸"]
color_constraint_tokens: ["cinnabar red"]
sketch_integration: ignore
ref_integration: none
```

## D1. L1-L5 weights
```yaml
reviewed: true
L1: 0.3
L2: 0.25
L3: 0.2
L4: 0.15
L5: 0.1
```

## D2. Thresholds + batch + rollback
```yaml
reviewed: true
L1_threshold:   {value: 0.7, source: assumed, confidence: low}
L2_threshold:   {value: 0.7, source: assumed, confidence: low}
L3_threshold:   {value: 0.6, source: assumed, confidence: low}
L4_threshold:   {value: 0.55, source: assumed, confidence: low}
L5_threshold:   {value: 0.5, source: assumed, confidence: low}
batch_size:     {value: 4, source: assumed, confidence: med}
rollback_trigger: {value: "3 consecutive L3<0.5", source: assumed, confidence: low}
override_rationale: null
```

## E. Spike plan
```yaml
reviewed: true
spike_requested: true
spike_count: 3
judgment_criterion: "pick seed where L3>=0.6"
results: []
status: pending
```

## F. Cost budget
```yaml
reviewed: true
per_gen_sec: {value: 80, source: measured, confidence: high}
total_session_sec: {value: 480, source: derived, confidence: med}
fail_fast_consecutive: {value: 2, source: assumed, confidence: low}
provider_used_for_calibration: mock
provider_multiplier_applied: 20
```

## Open questions
- Q: resolved-during-finalize example

## Notes
- calibration ran via mock generate_image at t_mock=0.001s × 20 multiplier
- no overrides applied
"""

# Second fixture: 8-section variant (no E / spike_triggered=false)
RESOLVED_NO_SPIKE_MD = RESOLVED_DESIGN_MD.replace(
    """## E. Spike plan
```yaml
reviewed: true
spike_requested: true
spike_count: 3
judgment_criterion: "pick seed where L3>=0.6"
results: []
status: pending
```

""",
    "",
).replace("spike_triggered: true", "spike_triggered: false")


class TestDesignMdShape:
    def test_frontmatter_has_exactly_8_fields(self):
        """S4 + spec §6.2: frontmatter is 8 fields, no additional keys."""
        fm_match = re.search(r"^---\n(.*?)\n---", RESOLVED_DESIGN_MD, re.DOTALL)
        assert fm_match, "frontmatter missing"
        fields = [line.split(":")[0].strip() for line in fm_match.group(1).strip().split("\n") if line.strip()]
        assert set(fields) == {
            "slug", "status", "input_proposal", "generated_by",
            "created", "updated", "spike_triggered", "tradition"
        }

    def test_section_count_with_spike_is_9(self):
        """Spec §5: 9 sections when spike_triggered=true."""
        sections = re.findall(r"^## ", RESOLVED_DESIGN_MD, re.MULTILINE)
        assert len(sections) == 9

    def test_section_count_without_spike_is_8(self):
        """Spec §5: 8 sections when spike_triggered=false (E omitted)."""
        sections = re.findall(r"^## ", RESOLVED_NO_SPIKE_MD, re.MULTILINE)
        assert len(sections) == 8

    def test_d2_numerics_use_triple_form(self):
        """Spec §6.3 per-dim preamble: D2 numerics MUST use {value, source, confidence} triple."""
        d2_block = re.search(r"## D2\..*?```yaml\n(.*?)\n```", RESOLVED_DESIGN_MD, re.DOTALL).group(1)
        # Check L1-L5 thresholds + batch_size + rollback_trigger each use triple form
        assert "L1_threshold:" in d2_block and "source:" in d2_block
        # Negative check: no bare-value L1_threshold (e.g., `L1_threshold: 0.7`)
        assert not re.search(r"L1_threshold:\s*\d", d2_block)

    def test_d1_has_no_source_or_confidence(self):
        """Spec §5: D1 is registry-authority; no source/confidence fields."""
        d1_block = re.search(r"## D1\..*?```yaml\n(.*?)\n```", RESOLVED_DESIGN_MD, re.DOTALL).group(1)
        assert "source:" not in d1_block
        assert "confidence:" not in d1_block

    def test_f_numerics_use_triple_form(self):
        """Spec §6.3: F numerics MUST use triple form."""
        f_block = re.search(r"## F\..*?```yaml\n(.*?)\n```", RESOLVED_DESIGN_MD, re.DOTALL).group(1)
        assert "per_gen_sec: {value:" in f_block
        assert "source:" in f_block

    def test_every_dim_block_has_reviewed_key(self):
        """Spec §6.3 preamble: every dim's fenced block MUST have `reviewed: true|false` at top."""
        for dim in ["A", "B", "C", "D1", "D2", "E", "F"]:
            block_match = re.search(f"## {dim}\\..*?```yaml\\n(.*?)\\n```", RESOLVED_DESIGN_MD, re.DOTALL)
            assert block_match, f"Dim {dim} block not found"
            assert "reviewed:" in block_match.group(1), f"Dim {dim} missing reviewed key"

    def test_handoff_string_verbatim(self):
        """Finding 9: handoff string MUST be byte-identical. Downstream tooling may grep."""
        # The test design.md doesn't contain handoff (that's printed, not written);
        # this test is a placeholder that inspects the skill file itself.
        # Use a path relative to this test file so CI + contributor clones work.
        skill_path = Path(__file__).resolve().parent.parent / ".claude/skills/visual-spec/SKILL.md"
        skill_body = skill_path.read_text()
        assert "Ready for /visual-plan. Run it with /visual-plan <slug>." in skill_body
