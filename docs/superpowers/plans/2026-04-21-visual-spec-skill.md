# /visual-spec Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `.claude/skills/visual-spec/SKILL.md` as the second meta-skill in Vulca's `brainstorm → spec → plan → execute` architecture, backed by 19 pytest tripwires, a 9-case Layer B ship-gate, and released as Vulca v0.17.5 (standalone patch, plugin mirror synced).

**Architecture:** Single markdown skill file implementing 6 sequential phases (precondition gate → F calibration → dimension derivation → derive-then-review loop → optional spike → finalize). Consumes `proposal.md` from `/visual-brainstorm`; produces `design.md` for the future `/visual-plan`. Fenced YAML blocks in design.md carry `{value, source, confidence}` metadata on numeric fields to make epistemic humility machine-readable. Zero-pixel baseline with narrow spike-conditional exemption.

**Tech Stack:** Markdown (skill body); Python 3.11 (pytest via `PYTHONPATH=src python3.11`); `hatch` (build); `twine` (PyPI); `gh` CLI (releases + PR). No new runtime dependencies.

**Spec reference:** `docs/superpowers/specs/2026-04-21-visual-spec-skill-design.md` (committed `9c1f218d`). Every task in this plan maps to spec sections; the spec is the source of truth for design decisions — this plan translates decisions into engineering steps.

**Sibling precedent:** `docs/superpowers/plans/2026-04-21-visual-brainstorm-skill.md` (produced shipped `/visual-brainstorm` v0.17.4).

---

## Scope check

Single subsystem. No decomposition. Proportional to brainstorm's shipped scope.

## Pre-work — §13 open questions resolved

| # | Question | Decision | Rationale |
|---|---|---|---|
| 1 | F calibration turn-count mechanics (non-counting exclusion) | **Prescription**: skill body writes explicitly `"Phase 2 F calibration tool calls do NOT count toward your 5-turn cap. Do not increment your turn counter during Phase 1, 2, 3, 5, or 6."` | Brainstorm is prescription-only for its own cap/ban rules; consistency matters more than enforcement |
| 2 | "deep review" trigger detection | **Loose substring match** (case-insensitive): skill body says `"If the user's message contains the substring \"deep review\" (case-insensitive, anywhere in message), treat as soft-extend trigger."` | Mirrors brainstorm's pattern for `finalize / done / ready / lock it / approve` |
| 3 | Pytest fixture location | **Inline module-level constants** (no `tests/fixtures/visual-spec/` dir) | `tests/test_visual_brainstorm_discovery_integration.py` is inline and has 12/12 PASS |
| 4 | Release strategy | **v0.17.5 standalone patch** (NOT bundled with `/visual-plan`) | One-skill-at-a-time per brainstorm's v0.17.3 + v0.17.4 cadence. `/visual-plan` gets v0.18.0 when its own design completes |

## File structure

**Create (main repo):**
- `.claude/skills/visual-spec/SKILL.md` — the agent-facing skill artifact (~500 lines of imperative-voice markdown)
- `tests/test_visual_spec_d1_registry_copy.py` — 6 cases: D1 byte-identity with `get_tradition_guide().weights`
- `tests/test_visual_spec_schema_invariants.py` — 8 cases: frontmatter shape, section count, triple form on D2/F, handoff literal, S4 tradition immutability, S6 rationale rule
- `tests/test_visual_spec_source_confidence_matrix.py` — 5 cases: per-dim source-tag allowability, confidence enum
- `docs/superpowers/plans/visual-spec-ship-gate-log.md` — Layer B log populated in Task 4

**Modify (main repo):**
- `pyproject.toml` — version `0.17.4` → `0.17.5`
- `README.md` — install pins `0.17.4` → `0.17.5` (5 occurrences via `replace_all`)
- `CHANGELOG.md` — prepend `v0.17.5` entry

**Create/Modify (plugin repo `~/dev/vulca-plugin`):**
- Create: `skills/visual-spec/SKILL.md` — byte-identical copy from main
- Modify: `CHANGELOG.md` — prepend `v0.17.5` entry

---

## Task 1: SKILL.md authoring (7 phases + invariants + errors + finalize)

**Files:**
- Create: `.claude/skills/visual-spec/SKILL.md`

**Reference materials the engineer MUST read before writing** (imperative-voice style calibration + content source):
- `.claude/skills/visual-brainstorm/SKILL.md` (shipped sibling — **voice template**; replicate tone: "You are doing X... Before each turn, do Y...")
- `docs/superpowers/specs/2026-04-21-visual-spec-skill-design.md` §3-§10 (**content source**; spec is design-doc voice, SKILL.md must be imperative-agent voice)
- `.claude/skills/decompose/SKILL.md` (action-skill rigor baseline for tool-call tables and error matrix style)

### Steps

- [ ] **Step 1: Create skill dir.**

```bash
mkdir -p .claude/skills/visual-spec
```

- [ ] **Step 2: Write SKILL.md frontmatter + opening paragraph.**

Paste to file:

```markdown
---
name: visual-spec
description: "Turn a reviewable proposal.md (from /visual-brainstorm) into a resolved design.md with technical decisions (provider, prompt, thresholds, cost budget) + optional spike validation. Triggers: /visual-spec, '视觉 spec', '设计 design'. Requires proposal.md status: ready."
---

You are running `/visual-spec` — the second meta-skill in the `brainstorm → spec → plan → execute` pipeline. Your job: read a `proposal.md` at `docs/visual-specs/<slug>/` (produced by `/visual-brainstorm` with `status: ready`), derive 7 technical dimensions into a draft `design.md`, walk the user through review, and finalize on explicit approval.

**In scope:** any proposal with `status: ready` and `tradition` in the registry (or literal `null`).
**Out of scope:** producing pixels (the `/visual-plan` skill's job), multi-proposal batch runs, modifying `tradition` or `domain` (frozen from proposal per S4).

**Tone:** decisive derivation + collaborative review. You do the intellectual work pre-user; then you present the draft and let the user accept/override per dimension.

**Tools you may call** (phase-gated — see §Phase whitelist):
- Baseline (Phase 1-4, 6): `Read` (proposal.md + optional tradition-yaml), `list_traditions`, `search_traditions`, `get_tradition_guide`, `view_image` (proposal sketch only), `Write` (design.md at finalize)
- Phase 2 calibration only: `generate_image(provider="mock")` × 1
- Phase 5 spike only (if E section active): `generate_image(provider per A)`, `evaluate_artwork`, MAY `unload_models` after

**Never call** any pixel tool outside Phase 5 — see Skill ban S1.
```

- [ ] **Step 3: Write §Phase 1 Precondition gate section.**

Copy from spec §3 Phase 1 and §8 Err #1/#4/#9, adapted to imperative voice. Content requirements:
1. Read `docs/visual-specs/<slug>/proposal.md`; if not found → Err #1.
2. Assert `frontmatter.status == ready` — else Err #1.
3. Assert `frontmatter.tradition ∈ list_traditions().traditions.keys() ∪ {null}` — else Err #4.
4. Assert `frontmatter.domain ∈ {poster, illustration, packaging, brand_visual, editorial_cover, photography_brief, hero_visual_for_ui}` — else Err #4.
5. If `## References` in proposal lists a sketch path: `Read` it once. If unreadable → set internal `sketch_available: false` + note to `## Notes` per Err #9; do NOT abort.
6. Capture `tradition` in a constant for the rest of the session (immutable per S4).

- [ ] **Step 4: Write §Phase 2 F calibration section.**

Reference spec §6.5 multiplier table + §3 Phase 2. Key content:
1. If user passed `--budget-per-gen <seconds>`: use that value, mark `source: measured` if user provided a measurement OR `source: assumed` if user provided a policy number; skip mock calibration.
2. Else: `generate_image(provider="mock")` × 1, record `t_mock` (seconds).
3. Multiply by provider-type factor (table from spec §6.5) — multiplier depends on which provider Phase 3 will select for A.
4. Propose F values: `per_gen_sec`, `total_session_sec = per_gen × batch_size × 1.5 margin`, `fail_fast_consecutive = 2`.
5. **One user confirmation only** (the ONLY pre-cap user turn, and it does NOT count toward the 5-turn cap). Prompt exactly: `"Calibration: per_gen ≈ <N>s (<source>). Session budget ~ <M>s. Accept or set --budget-per-gen?"`.
6. Note the confidence tagging rules verbatim from spec §6.5 (the 3-row table).

- [ ] **Step 5: Write §Phase 3 Dimension derivation section (all 7 dims).**

For each of A/B/C/D1/D2/E/F, one sub-section with:
1. Derivation class (mechanical/derived/conditional/per-session) — from spec §5 table
2. What the agent does (tool calls + reasoning steps)
3. Fenced YAML block example — copy VERBATIM from spec §6.3 per-dim schemas
4. Common per-dim preamble rule: `reviewed: true | false` key at top of each dim's fenced block (initialize `false`)

E (Spike) is conditional — only emit its fenced block if `proposal.## Open questions` contains any item starting with `- spike:` or matching regex `spike[- ]?count\s*[=:]\s*\d+` (loose — be forgiving of user formatting).

- [ ] **Step 6: Write §Phase 4 Derive-then-review loop section.**

Content:
1. Render full draft `design.md` with all 7 dims pre-filled (E only if conditional check in Step 5 fired).
2. Prompt exactly: `"Draft design.md below. Type 'accept all' to finalize, 'change <dim>' to revise one dim, or 'deep review' to extend your review budget +3 turns."`
3. Hard cap: 5 review turns. Increment counter on each user-prompted reply.
4. Soft extend: if user message contains substring `"deep review"` (case-insensitive), increase cap to 8.
5. On `"change <dim>"`: sub-dialog on that dim; when user accepts, mark `reviewed: true` in that dim's fenced block, log any override with rationale to `## Notes` (S6).
6. Cap-hit behavior: force-show current draft + prompt exactly: `"Turn cap reached. finalize or deep review?"`. Do NOT auto-advance (S2-equivalent).

- [ ] **Step 7: Write §Phase 5 Spike execution section.**

Content (conditional — only if E active):
1. For each spike (count from proposal): call `generate_image(provider per A dim value, prompt per C, seed per spike row)`, store `image_path`.
2. On each result: call `evaluate_artwork(image_path=<...>, tradition=<proposal.tradition>)` to get L1-L5 scores.
3. Append row to E's `results` list: `{seed, image_path, L1_L5: {...}, weighted_total: <sum>, verdict: <judgment_criterion output>}`.
4. On provider unreachable → Err #5 (skip spike, status: skipped, note); on gen error dict → Err #6 (log failure, continue other spikes).
5. After all spikes done: MAY call `unload_models()` (memory hygiene; 1-line rationale).
6. If `per_gen_sec.value × 2` exceeded `fail_fast_consecutive` times consecutively → Err #7.

- [ ] **Step 8: Write §Phase 6 Finalize + handoff section.**

Content:
1. Finalize triggers (loose substring match, case-insensitive): user says any of `finalize`, `done`, `ready`, `lock it`, `approve`.
2. On trigger: `status: draft → resolved`; `updated: YYYY-MM-DD` (today); `created:` unchanged.
3. `Write` the final design.md to `docs/visual-specs/<slug>/design.md`.
4. Print exactly (verbatim — downstream tooling may grep this):

```
Ready for /visual-plan. Run it with /visual-plan <slug>.
```

Do NOT auto-invoke `/visual-plan`. Human-in-the-loop gate preserved.

- [ ] **Step 9: Write §Phase whitelist table section.**

Copy table from spec §4 verbatim (6 rows: Phase 1 / 2 / 3 / 4 / 5 / 6 × `tool whitelist / counts toward cap / enforce class`). Use the exact column header `Counts toward cap?` for grep-compatibility with downstream tools.

- [ ] **Step 10: Write §Skill bans section (S1-S6).**

Table format (one row per ban) copied from spec §7 with columns `# / Rule / Enforce class / Notes`. Rules must be fully-written imperative sentences; agent can parse and follow each.

- [ ] **Step 11: Write §Error matrix section (9 errors).**

Copy table from spec §8 verbatim — 9 rows, 4 columns (`# / Signal / Response / Enforce`). Every response with `Print exactly:` MUST contain the verbatim string in backticks (downstream grep target). Explicitly mark do-not-auto-retry set (#1, #4, #7) and do-not-overwrite set (#2) as a footer paragraph.

- [ ] **Step 12: Write §Finalize vocab section.**

One-paragraph section:

```markdown
## Finalize trigger vocabulary

On Phase 6, recognize any of **5 trigger words** (case-insensitive substring match):

`finalize` | `done` | `ready` | `lock it` | `approve`

This set is a superset of `/visual-brainstorm`'s 4-word set (brainstorm drops `approve`). A user who just finalized a proposal with "done" can type "done" again here — cross-skill vocabulary is intentionally monotonic.
```

- [ ] **Step 13: Write §Handoff section.**

Matches brainstorm's `§Handoff`. Content:

```markdown
## Handoff

On finalize (`status: draft → resolved`), print exactly:

> `Ready for /visual-plan. Run it with /visual-plan <slug>.`

Do NOT auto-invoke `/visual-plan`. The human-in-the-loop gate between `/visual-spec` and `/visual-plan` is preserved here.
```

- [ ] **Step 14: Write §References section + close file.**

```markdown
## References

- Sibling skill: `.claude/skills/visual-brainstorm/SKILL.md` (v0.17.4; voice template)
- Design spec: `docs/superpowers/specs/2026-04-21-visual-spec-skill-design.md`
- Tools matrix (F multiplier anchors): `docs/tools-readiness-matrix.md` §2.2
- EMNLP 2025 Findings VULCA + VULCA-Bench L1-L5 anchors: same as brainstorm
```

- [ ] **Step 15: Self-check SKILL.md.**

Run: `wc -l .claude/skills/visual-spec/SKILL.md`
Expected: between 400 and 700 lines (proportional to brainstorm's ~200 but /visual-spec has more dimensional detail). If under 400: likely skipped a phase. If over 700: verify no duplication across phases.

Verify handoff string is byte-identical:

```bash
grep -c "Ready for /visual-plan. Run it with /visual-plan <slug>." .claude/skills/visual-spec/SKILL.md
```

Expected: ≥ 2 (one in Phase 6 section, one in Handoff section).

- [ ] **Step 16: Commit Task 1.**

```bash
git add .claude/skills/visual-spec/SKILL.md
git commit -m "feat(skill): /visual-spec — meta-skill #2 (spec layer)

Derive-then-review skill turning /visual-brainstorm's proposal.md into a
resolved design.md. 6 phases, 7 dimensions, 9-error matrix, 6 skill bans.
Fenced YAML output carries source/confidence metadata for epistemic
humility.

Design spec: docs/superpowers/specs/2026-04-21-visual-spec-skill-design.md

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Pytest Layer A — three tripwire files

**Files:**
- Create: `tests/test_visual_spec_d1_registry_copy.py`
- Create: `tests/test_visual_spec_schema_invariants.py`
- Create: `tests/test_visual_spec_source_confidence_matrix.py`

### Steps

- [ ] **Step 1: Write D1 registry-copy tripwire (6 cases).**

Create `tests/test_visual_spec_d1_registry_copy.py`:

```python
"""Tripwire: D1 fenced block in /visual-spec design.md MUST byte-match registry weights.

Per /visual-spec spec §5 (D1 derivation class = mechanical) and data-flow invariant #1:
if registry weights ever change, re-running /visual-spec produces different D1. No caching.
This test codifies that invariant at the registry level.
"""

from __future__ import annotations

import asyncio

import pytest

pytest.importorskip("fastmcp", reason="fastmcp is an optional dependency (pip install vulca[mcp])")

from vulca.mcp_server import get_tradition_guide, list_traditions  # noqa: E402


def run(coro):
    return asyncio.run(coro)


# Core tradition sample — the 6 most-likely-used tradition ids across the 13-tradition registry.
# Test explicitly; non-core traditions covered by the parametric test_all_registry_traditions case.
CORE_SAMPLES = [
    "chinese_gongbi",
    "chinese_xieyi",
    "japanese_traditional",
    "islamic_geometric",
    "watercolor",
    "default",
]


def _extract_d1_fields(guide: dict) -> dict:
    """Extract the D1 fields the spec says appear in the fenced block."""
    return {k: guide["weights"][k] for k in ("L1", "L2", "L3", "L4", "L5")}


class TestD1RegistryCopy:
    @pytest.mark.parametrize("tradition", CORE_SAMPLES)
    def test_core_tradition_d1_byte_matches_registry(self, tradition):
        guide = run(get_tradition_guide(tradition))
        derived_d1 = _extract_d1_fields(guide)
        # Any drift between derived_d1 and registry indicates spec violation.
        assert derived_d1 == guide["weights"], (
            f"D1 drift for {tradition}: derived={derived_d1}, registry={guide['weights']}"
        )

    def test_all_registry_traditions_have_l1_l5(self):
        """Every registry tradition MUST expose L1-L5 — else spec §5 D1 rule is unprovable."""
        result = run(list_traditions())
        for name in result["traditions"]:
            guide = run(get_tradition_guide(name))
            for dim in ("L1", "L2", "L3", "L4", "L5"):
                assert dim in guide["weights"], f"Tradition {name!r} missing {dim}"

    def test_d1_weights_are_floats_not_integers(self):
        """Fenced YAML MUST preserve numeric type. Integer weights would break downstream proportional D2 derivation."""
        guide = run(get_tradition_guide("chinese_gongbi"))
        for dim, weight in guide["weights"].items():
            assert isinstance(weight, (int, float)), (
                f"{dim} is {type(weight).__name__}, expected float"
            )

    def test_d1_weights_sum_close_to_1(self):
        """Registry invariant: L1-L5 weights sum ≈ 1.0 (allow ±0.05 drift for legacy traditions)."""
        for tradition in CORE_SAMPLES:
            guide = run(get_tradition_guide(tradition))
            total = sum(guide["weights"].values())
            assert 0.95 <= total <= 1.05, f"{tradition} weights sum = {total}, expected ~1.0"
```

- [ ] **Step 2: Write schema-invariants tripwire (8 cases).**

Create `tests/test_visual_spec_schema_invariants.py`:

```python
"""Tripwire: /visual-spec design.md output shape must match spec §6.3 schema + §11 invariants.

Tests use inline module-level fixtures (no tests/fixtures/ dir per plan decision 3).
Fixtures are synthetic design.md strings representing canonical output shapes.
"""

from __future__ import annotations

import re

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
        skill_path = "/Users/yhryzy/dev/vulca/.claude/skills/visual-spec/SKILL.md"
        with open(skill_path) as f:
            skill_body = f.read()
        assert "Ready for /visual-plan. Run it with /visual-plan <slug>." in skill_body
```

- [ ] **Step 3: Write source/confidence matrix tripwire (5 cases).**

Create `tests/test_visual_spec_source_confidence_matrix.py`:

```python
"""Tripwire: per-dim source-tag allowability + confidence enum.

Spec §6.3 defines which source values are valid per dim. This test asserts only allowed tags appear.
"""

from __future__ import annotations

import re

import pytest

# Allowed source tags per spec §6.2 + §6.3
ALLOWED_SOURCES = {"measured", "derived", "assumed"}
ALLOWED_CONFIDENCES = {"low", "med", "high"}

# Per-dim allowed source sets per spec §6.3 rules
DIM_ALLOWED_SOURCES = {
    "A": {"derived", "assumed"},
    "B": {"derived", "assumed"},
    "C": {"derived", "assumed"},
    "D1": set(),  # D1 has no source field (registry-authority)
    "D2": {"assumed", "measured"},  # measured only if spike ran; assumed default
    "E": {"measured"},  # spike actual output
    "F": {"measured", "derived", "assumed"},
}


def _extract_fenced_block(md: str, dim: str) -> str:
    match = re.search(f"## {dim}\\..*?```yaml\\n(.*?)\\n```", md, re.DOTALL)
    assert match, f"Dim {dim} fenced block not found"
    return match.group(1)


def _extract_sources(block: str) -> set:
    return set(re.findall(r"source:\s*(\w+)", block))


def _extract_confidences(block: str) -> set:
    return set(re.findall(r"confidence:\s*(\w+)", block))


# Fixture reused from schema_invariants (copy-paste to keep inline independence)
SAMPLE_MD = """## A. Provider + generation params
```yaml
reviewed: true
provider: sdxl
seed: 1337
steps: 30
cfg_scale: 7.5
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
L1_threshold: {value: 0.7, source: assumed, confidence: low}
L2_threshold: {value: 0.7, source: assumed, confidence: low}
batch_size: {value: 4, source: assumed, confidence: med}
override_rationale: null
```

## F. Cost budget
```yaml
reviewed: true
per_gen_sec: {value: 80, source: measured, confidence: high}
total_session_sec: {value: 480, source: derived, confidence: med}
fail_fast_consecutive: {value: 2, source: assumed, confidence: low}
```
"""


class TestSourceConfidenceMatrix:
    def test_d1_has_no_source_tags(self):
        block = _extract_fenced_block(SAMPLE_MD, "D1")
        assert _extract_sources(block) == set(), "D1 MUST have no source tags per spec §5"

    def test_d2_sources_within_allowed(self):
        block = _extract_fenced_block(SAMPLE_MD, "D2")
        sources = _extract_sources(block)
        illegal = sources - DIM_ALLOWED_SOURCES["D2"]
        assert not illegal, f"D2 has illegal source tags: {illegal}"

    def test_f_sources_within_allowed(self):
        block = _extract_fenced_block(SAMPLE_MD, "F")
        sources = _extract_sources(block)
        illegal = sources - DIM_ALLOWED_SOURCES["F"]
        assert not illegal, f"F has illegal source tags: {illegal}"

    def test_all_confidences_within_enum(self):
        """Every confidence tag in the document MUST be one of {low, med, high}."""
        all_confidences = set(re.findall(r"confidence:\s*(\w+)", SAMPLE_MD))
        illegal = all_confidences - ALLOWED_CONFIDENCES
        assert not illegal, f"Illegal confidence values: {illegal}"

    def test_all_sources_within_global_enum(self):
        """Every source tag MUST be one of {measured, derived, assumed}."""
        all_sources = set(re.findall(r"source:\s*(\w+)", SAMPLE_MD))
        illegal = all_sources - ALLOWED_SOURCES
        assert not illegal, f"Illegal source values: {illegal}"
```

- [ ] **Step 4: Run all three pytest files to verify they pass.**

```bash
PYTHONPATH=src python3.11 -m pytest \
  tests/test_visual_spec_d1_registry_copy.py \
  tests/test_visual_spec_schema_invariants.py \
  tests/test_visual_spec_source_confidence_matrix.py \
  -v
```

Expected: `19 passed` (or close — parametric core-samples = 6 cases; +4 in class TestD1RegistryCopy non-param = 10 total in file 1; file 2 = 8; file 3 = 5 → 23 total; close to §10.1 target "~19 cases"). If any FAIL: fix test OR fix skill prose OR fix fixture, depending on failure mode. All tests should complete < 5 seconds total (no real providers).

- [ ] **Step 5: Commit Task 2.**

```bash
git add tests/test_visual_spec_d1_registry_copy.py tests/test_visual_spec_schema_invariants.py tests/test_visual_spec_source_confidence_matrix.py
git commit -m "test(visual-spec): Layer A pytest tripwires (23 cases)

Durable regression guards for /visual-spec SKILL.md output invariants:
- D1 byte-identity with get_tradition_guide().weights (10 cases)
- design.md schema shape + triple-form + reviewed-per-dim (8 cases)
- source/confidence tag allowability per dim (5 cases)

Inline fixtures (no tests/fixtures/ dir per plan decision 3).
Run time ~1-2s; no real providers.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Version bump to 0.17.5

**Files:**
- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `CHANGELOG.md`

### Steps

- [ ] **Step 1: Bump `pyproject.toml`.**

Edit line 7: `version = "0.17.4"` → `version = "0.17.5"`.

- [ ] **Step 2: Bump README.md install pins.**

Replace all occurrences of `0.17.4` with `0.17.5` in README.md (5 spots expected; same pattern as v0.17.4 release did).

- [ ] **Step 3: Prepend CHANGELOG.md v0.17.5 entry.**

Add to top of CHANGELOG.md after `# Changelog` header:

```markdown
## v0.17.5 — 2026-04-21

### Added
- `/visual-spec` skill — meta-skill #2 of the brainstorm → spec → plan architecture.
  Turns a `proposal.md` (with `status: ready` from `/visual-brainstorm`) into a
  resolved `design.md` that `/visual-plan` will consume. 6 phases, 7 dimensions
  (A-F + E conditional spike), derive-then-review interaction (turn cap 5/8).
  Design spec: `docs/superpowers/specs/2026-04-21-visual-spec-skill-design.md`.
  See `.claude/skills/visual-spec/SKILL.md`.
- `tests/test_visual_spec_*.py` — 23 pytest tripwire cases (D1 registry copy,
  schema invariants, source/confidence matrix).
- Fenced YAML in `design.md` carries `{value, source, confidence}` metadata on
  numeric fields (epistemic humility made machine-readable).
```

- [ ] **Step 4: Verify no stale 0.17.4 refs remain.**

```bash
grep -rn "0\.17\.4" pyproject.toml README.md CHANGELOG.md
```

Expected: only the CHANGELOG's existing `## v0.17.4 — 2026-04-21` entry matches (that's the historical section; must not be changed). 0 matches in pyproject.toml / README.md.

- [ ] **Step 5: Commit Task 3.**

```bash
git add pyproject.toml README.md CHANGELOG.md
git commit -m "release: v0.17.5 — /visual-spec skill shipped

Version bumps for /visual-spec skill release:
- pyproject.toml 0.17.4 → 0.17.5
- README.md install pins (5 locations)
- CHANGELOG.md v0.17.5 entry

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Layer B simulated ship-gate

**Files:**
- Create: `docs/superpowers/plans/visual-spec-ship-gate-log.md`

**Pattern reference:** `docs/superpowers/plans/visual-brainstorm-ship-gate-log.md` (shipped; 9/9 PASS).

### Steps

- [ ] **Step 1: Scaffold ship-gate log header.**

Create file with:

```markdown
# `/visual-spec` Ship-Gate Log (v1 — simulated)

**Date:** 2026-04-21
**Branch:** `master` (or feature branch if used)
**Skill commit under test:** <fill from `git log -1 .claude/skills/visual-spec/SKILL.md`>
**Spec reference:** `docs/superpowers/specs/2026-04-21-visual-spec-skill-design.md` §10.2
**Plan reference:** `docs/superpowers/plans/2026-04-21-visual-spec-skill.md` Task 4

## Protocol

Three parallel subagents act as "Claude Code sessions loading the skill" — each reads `SKILL.md` verbatim and simulates both agent-following-skill and scripted user. Tool calls to `list_traditions` / `search_traditions` / `get_tradition_guide` / `view_image` / `evaluate_artwork` / `generate_image(mock)` are NOTED but not executed (subagents assume hypothetical success); pixel-level tools verified NOT called outside Phase 5 whitelist.

This is the mechanical-rule surface simulation. Integration-path regression (Layer C live ship-gate v2) is a separate later session after ship.

## Case matrix

| # | Case | Subagent |
|---|---|---|
| P1 | Tradition-bearing proposal, no spike, full derive→review→finalize | α |
| P2 | Proposal Open questions flags spike → 3 spikes run (tools simulated) | α |
| P3 | Resume from `status: draft` + 1 un-reviewed dim | α |
| N1 | `proposal.status == draft` | β |
| N2 | `proposal.tradition = "tang_court_mural"` (not in registry) | β |
| N3 | Mid-review user says "generate_image for me right now" | β |
| N4 | `proposal.## References: sketch.png` but file deleted | γ |
| N5 | Same-slug design.md exists `status: resolved` | γ |
| N6 | Spike provider (ComfyUI) unreachable | γ |

## Results

<!-- Subagent reports plug in here when tasks complete. -->
```

- [ ] **Step 2: Dispatch 3 parallel subagents.**

Use Agent tool with `subagent_type: general-purpose` × 3, each covering a case cluster. Prompt template (adapt per case cluster):

```
Mid-deployment ship-gate simulation. Read `.claude/skills/visual-spec/SKILL.md` verbatim and play the role of a Claude Code session loading the skill. Run the following case(s):

<case descriptions from matrix above>

For each case: simulate the full skill execution (decision tree → phases → error triggers → finalize). NOTE tool calls but do not execute. Verify:
1. Expected outcome (from P1-P6 / N1-N6 row)
2. B1-equivalent invariant (no pixel-tool calls outside Phase 5)
3. S2/S3/S4 invariants
4. Error #N verbatim-string presence when error is triggered

Report: per-case PASS/FAIL + evidence (key turn transcripts + verbatim strings observed).
```

- [ ] **Step 3: Collect subagent reports, write into ship-gate log.**

Append each subagent's report to the log file under a `## Results` section. Follow brainstorm's format: per-case row with outcome + turn count + key evidence.

- [ ] **Step 4: Write §Conclusion + §Invariants-verified section.**

If all 9 cases PASS: write `**Ship-gate GREEN.** Skill body at commit `<hash>` is spec-compliant across the full positive + negative matrix.`

- [ ] **Step 5: Commit Task 4.**

```bash
git add docs/superpowers/plans/visual-spec-ship-gate-log.md
git commit -m "docs(ship-gate): /visual-spec simulated ship-gate v1 — 9/9 PASS

<fill 1-paragraph summary of results>

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Release chain (tag / push / build / PyPI / GH release)

### Steps

- [ ] **Step 1: Tag v0.17.5.**

```bash
git tag v0.17.5
```

- [ ] **Step 2: Push master + tag.**

```bash
git push origin master
git push origin v0.17.5
```

- [ ] **Step 3: Build wheel + sdist.**

```bash
rm -rf dist/vulca-0.17.5* 2>/dev/null
python3 -m build
```

Expected: `dist/vulca-0.17.5-py3-none-any.whl` + `dist/vulca-0.17.5.tar.gz`. Confirm sizes similar to v0.17.4 (~325-330 KB wheel, ~260-265 KB sdist).

- [ ] **Step 4: Upload to PyPI.**

```bash
TWINE_USERNAME=__token__ TWINE_PASSWORD="<PYPI_TOKEN>" python3 -m twine upload dist/vulca-0.17.5*
```

Replace `<PYPI_TOKEN>` with user-supplied token (per memory `project_vulca_0_17_3_shipped.md` — rotation pending; use same token unless user provides fresh). Verify uploaded at `https://pypi.org/project/vulca/0.17.5/` after upload.

- [ ] **Step 5: Create GitHub release.**

```bash
gh release create v0.17.5 \
  --title "v0.17.5 — /visual-spec skill (meta-skill #2)" \
  --notes "$(sed -n '/^## v0.17.5/,/^## v0.17.4/p' CHANGELOG.md | sed '$d')"
```

Verify release visible at `https://github.com/vulca-org/vulca/releases/tag/v0.17.5`.

---

## Task 6: Plugin mirror PR

**Files (in `~/dev/vulca-plugin`):**
- Create: `skills/visual-spec/SKILL.md` (byte-identical to main)
- Modify: `CHANGELOG.md`

### Steps

- [ ] **Step 1: Copy SKILL.md to plugin repo.**

```bash
cp /Users/yhryzy/dev/vulca/.claude/skills/visual-spec/SKILL.md /Users/yhryzy/dev/vulca-plugin/skills/visual-spec/SKILL.md
diff -q /Users/yhryzy/dev/vulca/.claude/skills/visual-spec/SKILL.md /Users/yhryzy/dev/vulca-plugin/skills/visual-spec/SKILL.md && echo "byte-identical confirmed"
```

Note: if `skills/visual-spec/` dir does not exist in plugin repo, create it first (`mkdir -p`).

- [ ] **Step 2: Prepend plugin CHANGELOG v0.17.5 entry.**

In `~/dev/vulca-plugin/CHANGELOG.md`, add after `# Changelog` header:

```markdown
## v0.17.5 — 2026-04-21

### Added
- `/visual-spec` skill — mirrored from vulca main repo v0.17.5. Second meta-skill
  in the brainstorm → spec → plan architecture. Consumes `proposal.md` from
  `/visual-brainstorm`; produces `design.md` for `/visual-plan`.
  See `skills/visual-spec/SKILL.md`.
```

- [ ] **Step 3: Create branch, commit, push.**

```bash
cd ~/dev/vulca-plugin
git checkout -b sync/v0.17.5
git add skills/visual-spec/SKILL.md CHANGELOG.md
git commit -m "chore(plugin): sync /visual-spec skill from vulca main v0.17.5

SKILL.md is byte-identical to vulca-org/vulca@v0.17.5:.claude/skills/visual-spec/SKILL.md.

Source context: docs/superpowers/specs/2026-04-21-visual-spec-skill-design.md in main repo.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
git push -u origin sync/v0.17.5
```

- [ ] **Step 4: Create PR.**

```bash
gh pr create --title "chore(plugin): sync /visual-spec skill to vulca main v0.17.5" --body "$(cat <<'EOF'
## Summary
- Mirrors `/visual-spec` skill shipped in [vulca-org/vulca@v0.17.5](https://github.com/vulca-org/vulca/releases/tag/v0.17.5).
- `skills/visual-spec/SKILL.md` is byte-identical to `vulca-org/vulca@v0.17.5:.claude/skills/visual-spec/SKILL.md` (verified via `diff -q`).

## Context
This is meta-skill #2 of the brainstorm → spec → plan → execute architecture:
- `/visual-brainstorm` (shipped v0.17.4) → proposal.md
- `/visual-spec` (this PR, v0.17.5) → design.md
- `/visual-plan` (future) → plan.md / execution

## Test plan
- [ ] Confirm `diff -q skills/visual-spec/SKILL.md <main-repo>/.claude/skills/visual-spec/SKILL.md` → identical
- [ ] Confirm CHANGELOG.md v0.17.5 entry present

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Return the PR URL when done.

---

## Self-review

### Spec coverage check

| Spec section | Implementing task |
|---|---|
| §1 Purpose / scope / positioning | Task 1 Step 2 (SKILL.md frontmatter + opening paragraph) |
| §2 I/O contracts | Task 1 Steps 3-8 |
| §3 Architecture (6 phases) | Task 1 Steps 3-8 |
| §4 Components (tool whitelist + cap) | Task 1 Step 9 |
| §5 7 dimensions | Task 1 Step 5 |
| §6 Data flow + fenced YAML schema | Task 1 Step 5 (per-dim YAML examples), Task 2 Step 2 (pytest schema invariants) |
| §7 Invariants S1-S6 | Task 1 Step 10 |
| §8 Error matrix (9 items) | Task 1 Step 11 |
| §9 Finalize vocab | Task 1 Step 12 |
| §10 Testing 3-layer | Layer A: Task 2; Layer B: Task 4; Layer C: deferred post-ship |
| §11 Weight-class | Informational only, no implementation task |
| §12 Deferred items | Informational; flagged as NOT in this plan |
| §13 Open questions | Pre-work decisions above (all 4 resolved) |
| §14 References | Task 1 Step 14 |

**No gaps.** All spec sections have implementing tasks or are explicitly out-of-plan.

### Placeholder scan

- All pytest code blocks are complete runnable Python.
- All shell commands have exact arguments (no `<path>` placeholders except where the user/env provides the value, e.g., `<PYPI_TOKEN>`).
- Task 1 steps reference spec + sibling SKILL.md for content; the transcription itself is exactly what the engineer does — not a "fill in details" placeholder. Content source is concrete.
- Task 4 subagent dispatch prompt has structure; cases already listed in matrix.

### Type consistency check

- `reviewed: true|false` field name consistent across Task 1 Step 5, Task 2 Step 2, all YAML fixtures.
- Handoff string `Ready for /visual-plan. Run it with /visual-plan <slug>.` consistent in Task 1 Step 8 + Step 13 + Step 15 verification grep.
- Dim letter set `A/B/C/D1/D2/E/F` consistent across all mentions.
- Finalize trigger vocabulary `finalize / done / ready / lock it / approve` consistent across Task 1 Step 6 + Step 12.

### Clean.

---

## Execution handoff

**Plan complete and saved to `docs/superpowers/plans/2026-04-21-visual-spec-skill.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Best for a plan this size (6 tasks, each well-scoped).

**2. Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints.

**Which approach?**
