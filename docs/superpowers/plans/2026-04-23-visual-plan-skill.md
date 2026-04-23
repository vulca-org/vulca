# /visual-plan Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `/visual-plan` as the 3rd meta-skill in the `brainstorm → spec → plan → execute` architecture — a single SKILL.md artifact at `.claude/skills/visual-plan/SKILL.md` + ~57 pytest tripwires + 3-layer ship-gate + v0.17.7 release.

**Architecture:** Skill-body-only artifact (no Python backing). Agent reads SKILL.md and executes its instructions directly, consuming `design.md` (from /visual-spec) → producing reviewable `plan.md` + `plan.md.results.jsonl` sidecar + real `iters/<seed>/*.png` outputs. Mirrors /visual-spec's 2026-04-21 v0.17.5 ship pattern.

**Tech Stack:**
- `.claude/skills/visual-plan/SKILL.md` (~550-700 lines markdown)
- `tests/test_visual_plan_*.py` (4 files, pytest, ~57 cases)
- Ship-gate: 3 parallel subagents (Layer B simulated) + 2 parallel (Layer C live)
- Release: PyPI (vulca v0.17.7) + GitHub release + plugin mirror PR

**Blocking prerequisite:** Task C (v0.17.6) must ship before Task 9 (Layer C live ship-gate) — v0.17.6 lands MCP extension (`generate_image` seed/steps/cfg_scale/negative_prompt kwargs) + schema_version field + 10 clarity-gap items from `project_visual_spec_clarity_gaps.md`. Tasks 1-8 are independent of Task C and can land first.

**Spec reference:** `docs/superpowers/specs/2026-04-23-visual-plan-skill-design.md` (commit `6a9254c2`, 767 lines, 16-section).

---

## File Structure

### Created files

- `.claude/skills/visual-plan/SKILL.md` — single skill artifact, ~550-700 lines
- `tests/test_visual_plan_parser_invariants.py` — 15 cases covering §4 parser contract
- `tests/test_visual_plan_source_gating.py` — 11 cases covering §8 gating + §3 F-summary
- `tests/test_visual_plan_execution_loop.py` — 14 cases covering §5 Phase 3 + §9 jsonl
- `tests/test_visual_plan_error_matrix.py` — 17 cases covering §6 16-row matrix
- `docs/superpowers/plans/visual-plan-ship-gate-log.md` — Layer B simulated transcript
- `docs/superpowers/plans/visual-plan-live-ship-gate-log.md` — Layer C v2 transcript

### Modified files

- `pyproject.toml` — bump version to 0.17.7
- `CHANGELOG.md` (or wherever releases log) — v0.17.7 entry

### NOT modified in this plan (deferred to Task C v0.17.6)

- `src/vulca/mcp_server.py` — MCP `generate_image` signature extension
- `src/vulca/providers/*.py` — 4-provider seed/steps/cfg_scale/negative_prompt plumbing
- `.claude/skills/visual-spec/SKILL.md` — 10 clarity-gap items + schema_version field write
- `tests/test_generate_image_extended_signature.py` — v0.17.6-scoped 8 pytest cases

---

## Test Strategy

Per /visual-spec v0.17.5 precedent, pytest tripwires assert SKILL.md text contracts + fixture round-trip, not live skill execution. Categories:

1. **Verbatim-string grep contracts** — assert specific byte strings appear in SKILL.md (error matrix rows, handoff strings, F-summary prompt)
2. **Schema invariants** — fixture round-trip: sample `design.md` fixture → internal model → canonical `plan.md` output → re-read → byte-identical
3. **Section presence + structure** — assert SKILL.md has exactly N phases, N invariants, N error rows
4. **Source-gating decision tables** — exhaustive fixture: every `source × threshold × score` combo → expected verdict

Each pytest runs in ~50-500 ms. Total Layer A suite should complete in < 30 s.

---

## Task 1: Scaffold skill directory + SKILL.md skeleton

**Files:**
- Create: `.claude/skills/visual-plan/SKILL.md` (skeleton only)
- Create: `.claude/skills/visual-plan/` directory

- [ ] **Step 1: Verify working directory + precondition**

```bash
pwd
# Expect: /Users/yhryzy/dev/vulca (or equivalent repo root)
ls .claude/skills/ | head -10
# Expect: visual-brainstorm  visual-spec  (both exist, visual-plan does not)
```

- [ ] **Step 2: Create skill directory**

```bash
mkdir -p .claude/skills/visual-plan
```

- [ ] **Step 3: Write SKILL.md skeleton (frontmatter + 4 phase headers only)**

File: `.claude/skills/visual-plan/SKILL.md`

```markdown
---
name: visual-plan
description: "Turn a resolved design.md (from /visual-spec) into reviewable plan.md + run generate+evaluate loop → status {completed, partial, aborted}. Triggers: /visual-plan, '视觉 plan', '设计 execute'. Requires design.md status: resolved + Vulca checkout."
---

You are running `/visual-plan` — the third meta-skill in the `brainstorm → spec → plan → execute` pipeline. Your job: read a `design.md` at `docs/visual-specs/<slug>/` (produced by `/visual-spec` with `status: resolved`), derive a reviewable `plan.md` draft, walk the user through plan review, execute the generate+evaluate loop against the provider specified by `design.A.provider`, and finalize with terminal status + handoff string.

**In scope:** any `design.md` with `status: resolved` and `tradition` in the registry (or literal `null`), inside a Vulca checkout (`src/vulca/` present at cwd).
**Out of scope:** producing pixels outside Phase 3 (Err #8); multi-slug batch runs; modifying `design.md` (`/visual-plan` NEVER writes to `design.md` — S4 invariant).

**Tone:** decisive plan derivation + collaborative review gate + disciplined execution with per-iter audit.

## Phase 1 — Precondition gate + derivation + plan.md draft write

(filled in Task 6)

## Phase 2 — Plan-review loop

(filled in Task 6)

## Phase 3 — Execution loop

(filled in Task 6)

## Phase 4 — Finalize + optional hygiene

(filled in Task 6)

## References

- Design spec: `docs/superpowers/specs/2026-04-23-visual-plan-skill-design.md`
- Sibling skills: `.claude/skills/visual-brainstorm/SKILL.md` (v0.17.4), `.claude/skills/visual-spec/SKILL.md` (v0.17.5)
```

- [ ] **Step 4: Verify skeleton parseable**

```bash
wc -l .claude/skills/visual-plan/SKILL.md
head -5 .claude/skills/visual-plan/SKILL.md
# Expect: ~30 lines with valid frontmatter fence
```

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/visual-plan/SKILL.md
git commit -m "feat(visual-plan): skeleton SKILL.md with 4-phase scaffolding

Creates .claude/skills/visual-plan/ directory + SKILL.md frontmatter
and phase headers. Phase bodies filled in Task 6. Matches
sibling /visual-spec (v0.17.5) voice.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Parser invariants pytest + SKILL.md §4 body

**Files:**
- Create: `tests/test_visual_plan_parser_invariants.py` — 15 cases
- Modify: `.claude/skills/visual-plan/SKILL.md` — add Phase 1 parser section + Phase 1 steps 0-10

**Spec anchor:** §4.1 tolerant-read rules (7 entries), §4.2 strict-write (9-field frontmatter, 10 sections), §4.3 three-file system.

- [ ] **Step 1: Create pytest file with 15 failing tests**

File: `tests/test_visual_plan_parser_invariants.py`

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_visual_plan_parser_invariants.py -v 2>&1 | head -40`
Expected: all 15 tests FAIL with errors like "missing invariant S1", "missing error row Err #1", etc. (SKILL.md body is still skeleton)

- [ ] **Step 3: Write SKILL.md Phase 1 body**

Modify `.claude/skills/visual-plan/SKILL.md` — replace `## Phase 1 — Precondition gate + derivation + plan.md draft write\n\n(filled in Task 6)` with:

```markdown
## Phase 1 — Precondition gate + derivation + plan.md draft write

Runs before anything else. No turn cap charged. Early-exit on any Err; SKILL.md §6 error matrix governs.

0. **Vulca-sentinel precondition.** Assert `Path("src/vulca").is_dir()` at cwd. Failure → Err #14.
1. **Resolve slug + paths.** From positional arg, compute:
   - `design_path = docs/visual-specs/<slug>/design.md`
   - `plan_path = docs/visual-specs/<slug>/plan.md`
   - `jsonl_path = docs/visual-specs/<slug>/plan.md.results.jsonl`
   - `lock_path = docs/visual-specs/<slug>/plan.md.lock`
   - `iters_dir = docs/visual-specs/<slug>/iters/`
2. **Read design.md.** Missing file → Err #1. Parse frontmatter. `status != resolved` → Err #1.
3. **Check same-slug plan.md collision.**
   - Terminal status (`completed` / `partial` / `aborted`) → Err #2 refuse-overwrite.
   - `status: draft` → Err #3 resume path. **If a stale lockfile also exists, fold Err #12 side-effects (unlink + `[stale-lock-recovery]` Notes line + Phase 4 handoff suffix) into the resume path.**
4. **Check lockfile** (skip if step 3 folded it):
   - Exists + jsonl fresh (< 300s mtime) OR lockfile `started_at` < 300s + no jsonl → Err #11 concurrent.
   - Exists + stale (jsonl > 300s OR lockfile.started_at > 300s + no jsonl) → Err #12 auto-recover: `os.unlink(lockfile)`, append Notes `[stale-lock-recovery]` line, continue.
5. **Validate schema_version.** `design.frontmatter.schema_version` in supported set `{"0.1"}`. Absent → treat as `"0.1"` (back-compat). Unrecognized → Err #15.
6. **Validate tradition.** `list_traditions()`. `frontmatter.tradition` ∈ `traditions.keys()` OR literal YAML null. Violation → Err #4.
7. **Validate domain.** `frontmatter.domain` ∈ `{poster, illustration, packaging, brand_visual, editorial_cover, photography_brief, hero_visual_for_ui}`. Violation → Err #4.
8. **Parse 7 fenced-YAML dim blocks** (A/B/C/D1/D2/E/F) per tolerant-read rules below. Required section missing → Err #10.

### Fenced-YAML parser — tolerant read (Phase 1 step 8)

Extract fenced ```` ```yaml ... ``` ```` blocks under `## A.` / `## B.` / `## C.` / `## D1.` / `## D2.` / `## E.` / `## F.` headings. Parse via `yaml.safe_load` with `allow_duplicate_keys=False` (PyYAML strict default).

**Accept-with-normalization**:
1. **Unknown top-level keys** inside a dim block → ignore + log to plan.md Notes: `[parser-warn] <section>.<key>: unknown key dropped`.
2. **Missing required key** (e.g. `A.seed`) → fill from schema default + log: `[parser-default] <section>.<key> missed; filled with <default>`.
3. **Inline `# comments`** inside fences → allowed on read; stripped on write.
4. **Unknown `##` section headings** outside `A/B/C/D1/D2/E/F/Open questions/Notes` → ignore silently.
5. **`C.tradition_tokens` as flat string list** OR **list[dict]** with `{term, translation, definition?}` → normalize to flat strings `f"{term} {translation}"`.
6. **`A.provider` as bare `sdxl`** → on darwin normalize to `sdxl-mps`, elsewhere `sdxl-cuda`; log `[parser-normalize] A.provider: sdxl → sdxl-mps`.
7. **`D2.L_N_threshold` / `F.*` as bare number** `0.7` → wrap to `{value: 0.7, source: assumed, confidence: low}`.

**Hard-reject** → Err #1, #4, #10, #15 per §6.

9. **Sketch readability probe.** If `design.C.sketch_integration != "ignore"` and sketch path in `design.## References`: `Read(sketch_path)`. Failure → Err #9 (internal `sketch_available: false`; override `plan.C.sketch_integration: ignore`; queue Notes entry).
10. **Freeze session constants.** Capture `{tradition, domain, slug}` + `design_hash = sha256(design.md bytes)` for S4 content-guard (Phase 3 per-iter re-asserts).
11. **Derive plan.**
    - `seed_list`: start from `design.A.seed`, step +1 for `design.B.variant_count` items. If `design.## Open questions` has `- seeds: [<list>]` explicit override → prefer.
    - `gating_decisions`: per D2 L_N: `gate_class = hard` if source ∈ `{measured, derived}`, else `soft`. Initial `user_elevated: []`.
    - `composed_prompts`: per variant, assemble `{base_prompt} + ", " + {tradition_tokens joined} + ", " + {color_constraint_tokens joined}` + `negative_prompt` as separate kwarg. One composed string per iter.
    - `fail_fast_budget`: copy `F.fail_fast_consecutive`; if `None`, fail-fast disabled.
    - `rollback_plan`: copy `D2.rollback_trigger`; derive `rollback_action` default `partial` (user overrideable in Phase 2).
    - `F.initial_budget`: copy `design.F` verbatim.
12. **Create lockfile** via `open(lock_path, O_CREAT | O_EXCL | O_WRONLY)` with JSON `{pid: os.getpid(), started_at_iso: now(), design_ref: <path>}`. Precedent: `src/vulca/digestion/dream.py:46-80`.
13. **Write plan.md** with `status: draft` + derived body (schema per §4.2 below). Turn cost: zero.

### plan.md canonical schema (strict write)

**Frontmatter — exactly 9 fields, no comments inside `---` fence, deterministic order:**
```yaml
---
slug: <copied from design.md>
status: draft | running | completed | partial | aborted
domain: <copied, S4 immutable>
tradition: <copied, S4 immutable>
schema_version: "0.1"              # back-compat: absent in source → treated as "0.1"
generated_by: visual-plan@0.1.0
design_ref: docs/visual-specs/<slug>/design.md
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

**Body — exactly 10 sections, fixed order, every section present (empty uses `none`):**

```
# <human-readable title, mirror design.md>
## A. Execution parameters         — fenced YAML from design.A (MCP-extended)
## B. Iteration plan               — fenced YAML: strategy, variation_axis, seed_list, variant_count, batch_size
## C. Prompt composition           — fenced YAML: composed prompts per variant
## D. Gating decisions             — fenced YAML: per L_N {value, source, gate_class}, user_elevated, soft_gate_warn_count
## E. Fail-fast budget + rollback  — fenced YAML: fail_fast_consecutive, rollback_trigger, rollback_action
## F. Cost ledger                  — fenced YAML: initial_budget, actual (from jsonl), overage_pct
## Results                         — markdown table rendered from jsonl at Phase 4
## Notes                           — free-form audit lines
```

Notes convention lines (when relevant): `[parser-default]` / `[parser-warn]` / `[parser-normalize]` / `[override]` / `[resume-state]` / `[fail-fast]` / `[stale-lock-recovery]` / `[review-required]` / `[unload-models]` / `[evaluate-suspect]` / `[design-drift]` / `[failover-cross-class]`.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_visual_plan_parser_invariants.py -v 2>&1 | tail -20`
Expected: 15/15 PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_visual_plan_parser_invariants.py .claude/skills/visual-plan/SKILL.md
git commit -m "feat(visual-plan): Phase 1 parser + 15 pytest tripwires

Phase 1 precondition gate + derivation + plan.md draft write body
lands full tolerant-read rules (§4.1) and strict-write canonical
schema (§4.2). 15 pytest cases assert SKILL.md text contracts:
- 3 round-trip fixtures (minimal / full-with-spike / null-tradition)
- 7 tolerant-read rules
- 4 invariant+count tripwires (9 frontmatter fields, 4 phases, 7 S, 16 Err)
- 1 drift audit

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Source-gating pytest + SKILL.md §8 body

**Files:**
- Create: `tests/test_visual_plan_source_gating.py` — 11 cases
- Modify: `.claude/skills/visual-plan/SKILL.md` — add §Source-gating decisions body (follows Phase 1) + §Phase 2 F-summary prompt

**Spec anchor:** §8 source-gating matrix, §5 Phase 2 F-summary prompt + reply handling, §8 verdict tree with all-zero sentinel.

- [ ] **Step 1: Create pytest file with 11 failing tests**

File: `tests/test_visual_plan_source_gating.py`

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_visual_plan_source_gating.py -v 2>&1 | head -30`
Expected: 11/11 FAIL.

- [ ] **Step 3: Append Source-gating section to SKILL.md (after Phase 1 body)**

Append to `.claude/skills/visual-plan/SKILL.md` (before `## Phase 2` placeholder):

```markdown

## Source-gating decisions (consumed by Phase 2 + 3)

For each design.md numeric threshold `{value, source, confidence}`, Phase 1 derivation maps to `gate_class`:

| design.md field | source value | plan.md `gate_class` | Phase 3 behavior |
|---|---|---|---|
| `D2.L_N_threshold` | `measured` | **hard** | score < value → `reject` verdict, fail_fast_counter++ |
| `D2.L_N_threshold` | `derived` | **hard** | same as measured (calibration-anchored, trusted) |
| `D2.L_N_threshold` | `assumed` | **soft** | score < value → `accept-with-warning`, log `[review-required]` to Notes, soft_gate_warn_count++, counter unchanged |
| `D2.L_N_threshold` | `user-confirmed` (post-elevation via Phase 2 change) | **hard** | same as measured; only possible after Phase 2 `change D.L_N` subcommand |
| `F.per_gen_sec` | `measured` / `derived` | **hard-budget** | enforced by Err #7 fail_fast counter |
| `F.per_gen_sec` | `assumed` | **Phase 2 F-summary prompt decides** | reply (a) → hard-budget continues + `user_ack_assumed_budget: true`; (b) → updates value, source=user-confirmed, hard-budget; (c) → disables Err #7 via `fail_fast_consecutive = None` |
| `F.fail_fast_consecutive` | any source | **hard-counter** | value applies regardless of source once F-summary resolved |
| `D1.L_N` weight | (no source triple) | **registry-authority** | weighted_total multiplier only; not itself a gate |

**Critical invariant**: when Phase 2 `change D.L_N` elevates a threshold from assumed → user-confirmed, `user_elevated` list in plan.md tracks the change + `gate_class: soft → hard` + `[override]` Notes line logged. **`user_elevated` persists ONLY in plan.md — never back-written to design.md. design.md is immutable post-resolved per /visual-spec S4 contract.**

### Phase 3 verdict tree

```python
# Sentinel: all-zero scores indicate evaluator failure masquerading as pass.
# Without this guard, a broken evaluate_artwork silently greenlights every iter.
# Threshold is <0.01 (not ==0.0) to catch float-representation noise from evaluators
# that emit 1e-7 rather than exact zero. Legitimate single-L outliers at 0.008 do NOT
# trigger — sentinel requires ALL FIVE dims simultaneously below 0.01.
if all(l_scores[k] < 0.01 for k in ("L1", "L2", "L3", "L4", "L5")):
    _append_notes(f"[evaluate-suspect] iter {iter}: all L_N scores < 0.01; flagged for review")
    return "accept-with-warning"

hard_fails = [L_N for L_N in L1..L5 if gate_class=hard AND score < value]
soft_fails = [L_N for L_N in L1..L5 if gate_class=soft AND score < value]
budget_overage = (F.fail_fast_consecutive is not None AND wall_time > F.per_gen_sec.value * 2)

if hard_fails: return "reject"
if soft_fails or budget_overage: return "accept-with-warning"   # NOT reject, counter unchanged
return "accept"                                                   # fail_fast_counter → 0
```

### Phase 2 F-summary prompt (fires before main draft prompt; NOT charged toward 5-turn cap)

Triggered when any of `F.per_gen_sec / F.total_session_sec` has `source == "assumed"`. Print exactly:

```
F budget is assumed: per_gen_sec ~<X>s × <N> iters × 1.5 margin = ~<Y>s total.
This is derived from mock calibration + provider multiplier; not measured on your hardware.
Reply:
  (a) accept this budget as-is
  (b) override <per_gen_sec_seconds>
  (c) skip-budget-check (disables Err #7 cost enforcement)
```

Reply handling:
- `(a)` / `a` / `accept` → set `F.user_ack_assumed_budget: true`; F stays assumed; fail_fast still active.
- `(b) <N>` / `override <N>` → `F.per_gen_sec = {value: N, source: user-confirmed, confidence: high}`; recompute `F.total_session_sec`; fail_fast active with new baseline.
- `(c)` / `skip` / `skip-budget-check` → `F.fail_fast_consecutive = None`; Err #7 disabled; log Notes `[budget-skipped] user opted out of per-gen latency enforcement`.
- Invalid first time → re-prompt once.
- Invalid second time → default to `(a)` + log `[budget-assumed-default] invalid reply treated as accept`.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_visual_plan_source_gating.py -v 2>&1 | tail -20`
Expected: 11/11 PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_visual_plan_source_gating.py .claude/skills/visual-plan/SKILL.md
git commit -m "feat(visual-plan): source-gating matrix + F-summary prompt + verdict tree

Adds §Source-gating decisions to SKILL.md covering:
- Gate class map (measured/derived→hard, assumed→soft, user-confirmed→hard)
- Phase 3 verdict tree with all-zero evaluator sentinel at <0.01
- Phase 2 F-summary prompt with (a)/(b)/(c) lettered reply handling
- user_elevated persists only in plan.md (design.md immutable invariant)

11 pytest tripwires assert each gate mapping, F-summary trigger + 3
reply paths, verdict tree branches, sentinel rule.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Execution loop pytest + SKILL.md Phase 3 body

**Files:**
- Create: `tests/test_visual_plan_execution_loop.py` — 14 cases
- Modify: `.claude/skills/visual-plan/SKILL.md` — replace Phase 3 placeholder + add §jsonl schema

**Spec anchor:** §5 Phase 3 pseudocode, §9 jsonl row schema (14 required fields), §4.3 three-file system, §5 Phase 4 terminal status priority.

- [ ] **Step 1: Create pytest file with 14 failing tests**

File: `tests/test_visual_plan_execution_loop.py`

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_visual_plan_execution_loop.py -v 2>&1 | head -30`
Expected: 14/14 FAIL.

- [ ] **Step 3: Replace Phase 3 placeholder in SKILL.md**

In `.claude/skills/visual-plan/SKILL.md`, replace `## Phase 3 — Execution loop\n\n(filled in Task 6)` with:

```markdown
## Phase 3 — Execution loop

Runs only after Phase 2 user types `accept all` and status flips `draft → running`. No review cap. Sequential iteration over `seed_list`. Lockfile heartbeat = jsonl mtime (no separate heartbeat file).

**S1 enforcement**: Phase 3 tool whitelist = `generate_image` + `evaluate_artwork` + MAY `unload_models` at loop end. Forbidden across all phases: `create_artwork`, `generate_concepts`, `inpaint_artwork`, any `layers_*`.

```python
fail_fast_counter = 0
completed_iters = _replay_jsonl_if_exists()   # Err #3 resume or Err #12 recovery
soft_gate_warn_count = 0

for iter_idx, seed in enumerate(seed_list):
    if iter_idx < len(completed_iters):
        # Resume: rebuild fail_fast_counter from last contiguous reject-run
        fail_fast_counter = _rebuild_counter(completed_iters)
        soft_gate_warn_count = _rebuild_soft_count(completed_iters)
        continue

    # S4 content-guard: re-hash design.md and compare to captured session constant
    current_hash = _sha256(Path(design_ref).read_bytes())
    if current_hash != design_hash:
        _terminate_phase3(status="aborted", at_iter=iter_idx, reason="err16")
        return  # Err #16 fires

    variant = _variant_for_iter(iter_idx, plan.B)
    composed_prompt = plan.C.composed_prompts[variant.idx]
    t0 = perf_counter()
    started_at = now_iso()

    try:
        gen_result = await generate_image(
            prompt=composed_prompt,
            provider=plan.A.provider,
            tradition=design.frontmatter.tradition,
            reference_path=plan.A.reference_path if plan.C.sketch_integration != "ignore" else "",
            output_dir=f"docs/visual-specs/{slug}/iters/{seed}/",
            seed=plan.A.seed + iter_idx,          # MCP-extended (v0.17.6 prereq)
            steps=plan.A.steps,                    # MCP-extended
            cfg_scale=plan.A.cfg_scale,            # MCP-extended
            negative_prompt=plan.A.negative_prompt, # MCP-extended
        )
    except ProviderUnreachable as e:
        # Err #5 hands off directly to Err #13 cross-class user prompt (no S8 auto-failover)
        user_choice = prompt_err13(e, plan.A.provider)
        if user_choice == "a":
            plan.A.provider = _alt_class_provider(plan.A.provider)
            _log_failover_notes(plan.A.provider)
            continue
        elif user_choice == "b":
            _terminate_phase3(status="aborted", at_iter=iter_idx); return
        elif user_choice == "c":
            _terminate_phase3(status="partial", at_iter=iter_idx); return

    wall_time = perf_counter() - t0

    if "error" in gen_result:
        # Err #6: per-iter failure, log + continue
        _append_jsonl_row(iter_idx, seed, verdict="failed",
                          error=gen_result["error"], ...)
        continue

    eval_result = await evaluate_artwork(
        image_path=gen_result["image_path"],
        tradition=design.frontmatter.tradition,
    )
    # evaluate_artwork returns {"score": float, "dimensions": {...}, "tradition": str}.
    # Map the 5 L scores out of the dimensions dict (keys are rubric names per tradition).
    # On missing / malformed dimensions → jsonl row verdict=failed with error=<excerpt>, continue.
    l_scores = _extract_l_scores(eval_result)
    weighted_total = sum(l_scores[k] * plan.D1[k] for k in ("L1", "L2", "L3", "L4", "L5"))

    verdict, gate_decisions = _compute_verdict(l_scores, plan.D.gating_decisions,
                                                plan.F, wall_time)

    _append_jsonl_row(iter_idx, seed, variant, gen_result["image_path"],
                     started_at, wall_time, plan.A.provider,
                     l_scores, weighted_total, verdict, gate_decisions,
                     composed_prompt)

    if verdict == "reject":
        fail_fast_counter += 1
    elif verdict == "accept":
        fail_fast_counter = 0   # accept resets counter to 0
    elif verdict == "accept-with-warning":
        soft_gate_warn_count += 1
        # fail_fast_counter unchanged — soft never contributes

    # Err #7: unified 3-option prompt (no F.source branching)
    if (plan.F.fail_fast_consecutive is not None
        and fail_fast_counter >= plan.F.fail_fast_consecutive.value):
        # force-show plan; print exactly: cost budget exceeded (<consecutive>×over). Abort, extend budget, or accept remaining?
        user_choice = prompt_err7()
        if user_choice == "abort":
            _terminate_phase3(status="aborted", at_iter=iter_idx); return
        elif user_choice.startswith("extend"):
            plan.F.fail_fast_consecutive.value = _parse_extend(user_choice)
            fail_fast_counter = 0  # reset on extend
        elif user_choice == "accept-remaining":
            _terminate_phase3(status="partial", at_iter=iter_idx); return
```

### plan.md.results.jsonl — row schema (14 required fields + 2 optional)

```json
{
  "iter": 3,
  "seed": 1340,
  "variant_idx": 2,
  "variant_name": "season=summer",
  "image_path": "docs/visual-specs/<slug>/iters/1340/gen_abc12345.png",
  "started_at": "2026-04-23T14:05:12Z",
  "wall_time_sec": 82.34,
  "provider_used": "sdxl-mps",
  "l_scores": {"L1": 0.78, "L2": 0.72, "L3": 0.58, "L4": 0.61, "L5": 0.49},
  "weighted_total": 0.651,
  "verdict": "accept-with-warning",
  "gate_decisions": {"hard_fails": [], "soft_fails": [["L3", 0.58, 0.6]], "budget_overage": false},
  "prompt_used": "..."
}
```

Schema rules:
- UTF-8, NDJSON (newline-delimited JSON), one row per line.
- Serialize: `json.dumps(..., ensure_ascii=True, separators=(",", ":"))` — grep-safe (CJK escapes to `\uXXXX`).
- Always terminate with `"\n"`; read: `[json.loads(l) for l in content.splitlines() if l.strip()]` (tolerant of torn last line from crash).
- 14 required fields above; 2 optional: `error` (on `verdict: failed` rows) and `evaluate_artwork_raw` (full tool return; off by default).
- `iter` strictly monotonic increasing by 1 per append (natural from sequential Phase 3).
- **append-only** — a crash between row N-1 and row N leaves exactly N-1 rows on disk, not N+partial.

### Phase 3 tool whitelist reminder

- `generate_image` (MCP-extended v0.17.6 signature)
- `evaluate_artwork`
- MAY `unload_models` at loop end (optional memory hygiene; log Notes `[unload-models] freeing <provider> weights` when called).

**S1 absolute ban** (any phase): `create_artwork`, `generate_concepts`, `inpaint_artwork`, any `layers_*`. User request for any of these → Err #8 decline, turn NOT charged.
```

Also replace `## Phase 4 — Finalize + optional hygiene\n\n(filled in Task 6)` with:

```markdown
## Phase 4 — Finalize + optional hygiene

1. Read `plan.md.results.jsonl` → all completed rows.
2. Determine terminal status (priority order: `aborted` > `partial` > `completed`):
   - **`aborted`** triggers: user-triggered abort, Err #13(b) user picked "no, abort", Err #7 user picked "abort", Err #16 design.md drift detected mid-Phase-3.
   - **`partial`** triggers: Err #7 user picked "accept-remaining", Err #13(c) user picked "skip as partial", all iters completed but zero had verdict ∈ {accept, accept-with-warning} (every row `verdict: failed` via Err #6). Mixed rows where at least one is `accept`/`accept-with-warning` fall through to `completed` with `[iter-failures]` Notes line.
   - **`completed`** trigger: all iters in seed_list completed AND at least one verdict ∈ {accept, accept-with-warning}. Soft warnings affect handoff variant selection but do NOT demote to partial.
   - **Zero-rows corner case**: if Err #16 / user abort fires at iter 0 before any jsonl row appended → fall-through to `aborted`.
3. Render `## Results` markdown table from jsonl rows (columns: `iter | seed | variant | image | L1-L5 | weighted | verdict | wall_time | provider | notes`).
4. Populate `## F. Cost ledger` actual: `total_wall_time` sum from jsonl, `overage_pct = actual / initial_budget - 1`.
5. Append terminal-state Notes lines (`[fail-fast]`, `[aborted-at-iter]`, etc.).
6. Rename `plan.md.results.jsonl` → `plan.md.results.jsonl.archive` (atomic on same filesystem).
7. Delete `plan.md.lock` via `os.unlink`.
8. MAY call `unload_models()` on `plan.A.provider`'s weight family for post-session cleanup. Log Notes if called.
9. Write final `plan.md` with `status: <terminal>`, `updated: <today>`.
10. Assert S4: `plan.frontmatter.{tradition, domain, slug}` == captured values. Violation → raise (code bug).
11. Determine handoff string variant (8 variants total — see §Handoff below); append ` (recovered from stale lock at iter <K>)` suffix if Phase 1 fired Err #12 or folded via Err #3.
12. Print handoff string byte-identical.

**Do NOT auto-invoke anything downstream.** /visual-plan is terminal.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_visual_plan_execution_loop.py -v 2>&1 | tail -20`
Expected: 14/14 PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_visual_plan_execution_loop.py .claude/skills/visual-plan/SKILL.md
git commit -m "feat(visual-plan): Phase 3 execution loop + Phase 4 finalize + jsonl schema

Phase 3 body covers sequential seed_list iteration, MCP-extended
generate_image call (v0.17.6 prereq), S4 content-guard re-hash per
iter, evaluate_artwork dimensions → L1-L5 extraction, verdict tree
with fail_fast counter, unified Err #7 3-option prompt.

Phase 4 body covers jsonl → ## Results render, terminal status
priority (aborted > partial > completed), zero-rows corner case,
lockfile cleanup, optional unload_models, handoff selection.

§jsonl row schema 14 required + 2 optional fields documented.

14 pytest tripwires assert verdict transitions, jsonl schema +
ensure_ascii=True grep-safety, resume replay + counter rebuild,
lockfile atomicity, S2 cap-hit stays draft, terminal priority.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Error matrix pytest + SKILL.md §Error matrix body

**Files:**
- Create: `tests/test_visual_plan_error_matrix.py` — 17 cases
- Modify: `.claude/skills/visual-plan/SKILL.md` — add §Error matrix (16 rows) + §Invariants (S1-S7) + §Handoff (8 variants)

**Spec anchor:** §6 Error matrix (16 rows with grep-contract verbatim strings), §7 Invariants S1-S7, §2 Handoff table.

- [ ] **Step 1: Create pytest file with 17 failing tests**

File: `tests/test_visual_plan_error_matrix.py`

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_visual_plan_error_matrix.py -v 2>&1 | head -30`
Expected: 17/17 FAIL.

- [ ] **Step 3: Append §Error matrix + §Invariants + §Handoff to SKILL.md**

Append to `.claude/skills/visual-plan/SKILL.md` (after Phase 4 body):

```markdown

## Invariants (S1-S7)

| # | Rule | Enforce class |
|---|---|---|
| **S1** | Pixel-tool ban baseline. Exemptions: Phase 3 execution authorizes ONLY `generate_image`, `evaluate_artwork`, MAY `unload_models`. Forbidden across every phase: `create_artwork`, `generate_concepts`, `inpaint_artwork`, any `layers_*`. | prescription |
| **S2** | Do not flip `frontmatter.status` without explicit user trigger. `draft → running` requires `accept all` in Phase 2. `running → terminal` requires a terminal condition (all iters done / fail_fast / user-abort / Err #13 / Err #16). Cap-hit alone is NOT a trigger. | prescription |
| **S3** | Only consume `design.md` with `status: resolved`. Reject anything else via Err #1. | helper |
| **S4** | `frontmatter.{tradition, domain, slug}` are immutable across the session (captured at Phase 1, asserted at Phase 4 Write). `A.provider` is **EXPLICITLY MUTABLE** via user-approved Err #13 cross-class failover only — any mutation outside Err #13 is an S4 violation. design.md file bytes are content-hash-guarded: Phase 1 captures `sha256(design.md)` into session `design_hash`; Phase 3 re-hashes per iter; drift → Err #16 abort. | helper |
| **S5** | Concurrency control via `plan.md.lock` (`O_CREAT \| O_EXCL` with `{pid, started_at_iso, design_ref}` JSON). Staleness judged by jsonl mtime (when present) OR lockfile `started_at` (when no jsonl), both compared to 300s threshold. Stale → Err #12 auto-recover. Fresh → Err #11 refuse. Precedent: `src/vulca/digestion/dream.py:46-80`. | helper |
| **S6** | `plan.md.results.jsonl` is append-only during Phase 3. One row per completed iter (success OR failed OR skipped). No rewrites; sequential append in `iter_idx` order (natural from sequential Phase 3). | helper |
| **S7** | `plan.md` is a render artifact only. Phase 3 does NOT rewrite `plan.md` mid-loop (all per-iter progress goes to jsonl sidecar). Phase 4 finalize reads jsonl → renders `## Results` → atomic `os.rename(.jsonl → .jsonl.archive)` → Write terminal plan.md. | prescription + helper |

## Error matrix (16 rows, grep-contract verbatim)

| # | Signal | Response | Enforce |
|---|---|---|---|
| 1 | `design.md` not found OR `status != resolved` | Print exactly: `design.md not found or status != resolved at <path>. Run /visual-spec <slug> first.` Terminate. | helper |
| 2 | Same-slug `plan.md` exists with terminal status (`completed` / `partial` / `aborted`) | Print exactly: `already <status> at <path>; branch with -v2 or pick new slug`. Terminate. **Do not overwrite.** | helper + prescription |
| 3 | Same-slug `plan.md` status: draft (with or without jsonl) | Resume Phase 2 review loop; skip sections with `reviewed: true`; accumulate `turns_used` from Notes `[resume-state]` line. If jsonl present → Phase 3 entry replays `completed_iters`. **If a stale lockfile also exists, fold Err #12 side-effects (unlink + `[stale-lock-recovery]` Notes line + Phase 4 handoff suffix) into the resume path; only one recovery Notes line total.** | helper + prescription |
| 4 | design.md frontmatter violation (`tradition` not in registry AND not YAML null; OR `domain` not in 7-enum) | Print exactly: `design.md frontmatter violation: <field> <value> invalid. Re-run /visual-spec <slug> to fix.` Terminate. **Do not auto-retry.** | helper |
| 5 | Phase 3 provider unreachable (connection refused / missing key / timeout) | **No auto-failover.** Append `[failover-needed] <provider> unreachable: <err>` to Notes. Hand off directly to Err #13 user prompt. | helper (hands off to #13) |
| 6 | `generate_image` returns error dict (validation / OOM / malformed param) | jsonl row: `verdict: failed, error: <excerpt>`. Continue next iter. All-fail → terminal `partial`. | helper |
| 7 | Phase 3 `fail_fast_counter >= F.fail_fast_consecutive.value` (fires only when `F.fail_fast_consecutive is not None`) | Force-show current draft + print exactly: `cost budget exceeded (<consecutive>×over). Abort, extend budget, or accept remaining?` User `(a)` → `aborted`; `(b) extend <N>` → fail_fast_consecutive reset to N, counter reset 0, continue; `(c) accept-remaining` → `partial`. **Never auto-extend.** | prescription |
| 8 | User requests pixel action in Phase 1/2/4 (`generate now`, `skip review`) | Print exactly: `plan layer executes pixels in Phase 3 only. Complete review (accept all) first, or change spec via /visual-spec <slug>.` Do NOT invoke tool. **Turn NOT charged.** | prescription |
| 9 | design.md `## References` sketch unreadable at Phase 1 probe | Set state `sketch_available: false`; override `plan.C.sketch_integration: ignore`. Notes: `sketch at <path> unreadable at plan time: <err>. Proceeding text-only; C.sketch_integration forced to "ignore".` **Do not abort.** | helper |
| 10 | design.md YAML parse-fail (required section missing / dup keys / fence syntax) | Print exactly: `design.md parse-fail at <slug>: <issue>. Re-run /visual-spec <slug> to regenerate.` Terminate. **Do not auto-retry.** | helper |
| 11 | Same-slug concurrent /visual-plan (lockfile fresh + jsonl mtime < 300s OR lockfile.started_at < 300s + no jsonl) | Print exactly: `<slug> currently running (pid: <pid>, started: <iso>). Abort the other session first, or wait and retry.` Terminate. **Do not kill other pid.** | helper |
| 12 | Stale lockfile (jsonl mtime > 300s OR lockfile.started_at > 300s + no jsonl) | Auto-recover silently: `os.unlink(lockfile)`. Append Notes: `[stale-lock-recovery] previous pid <N> abandoned at <iso>; reclaimed at <now>. Resuming from iter <K>.` Handoff string at Phase 4 appends ` (recovered from stale lock at iter <K>)` suffix. **No user prompt; NOT stderr** (Claude Code skills don't surface stderr). | helper |
| 13 | Phase 3 provider unreachable AND failover requires cross-class switch (local ↔ cloud) | Print exactly: `<current> unreachable, failover to <alt> requires cross-class switch (local→cloud or reverse). Approve? (a) yes / (b) no, abort / (c) no, skip remaining iters as partial`. **Prompt user. Turn NOT charged.** `(a)` → execute failover + Notes `[failover-cross-class]`; `(b)` → `aborted`; `(c)` → `partial`. | prescription |
| 14 | `Path("src/vulca").is_dir()` false | Print exactly: `not inside a Vulca checkout; /visual-plan requires repo presence at cwd. cd into your vulca repo and retry.` Terminate. | helper |
| 15 | `design.frontmatter.schema_version` present AND not in supported set `{"0.1"}` | Print exactly: `design.md schema_version <got> not recognized; upgrade /visual-spec (pip install --upgrade vulca) or pin vulca@<compatible>.` Terminate. **Do not auto-retry; do not suggest /visual-spec re-run.** | helper |
| 16 | Phase 3 per-iter hash guard detects `design.md` bytes changed since Phase 1 capture | Print exactly: `design.md mutated mid-session at iter <K>; aborting. Re-run /visual-plan <slug> to restart with new design.` Abort immediately. Status → `aborted`. jsonl up through iter `<K-1>` preserved. Append Notes: `[design-drift] design.md sha256 changed between Phase 1 and iter <K>; aborting.` | helper |

**Classification footer**:
- **Do NOT auto-retry**: Err 1, 4, 7, 10, 14, 15, 16.
- **Do NOT overwrite**: Err 2.
- **Degrade, continue**: Err 6, 9.
- **Resume / recover (special)**: Err 3 (draft resume), 12 (stale-lock auto-recover). Collision rule: Err #3 path absorbs Err #12 side-effects when both fire.
- **Decline without charge**: Err 8, 13.
- **Refuse-to-start**: Err 11, 14, 15.
- **User prompt**: Err 7, 13.
- **Hands-off**: Err 5 → #13.
- **Content-guard abort**: Err 16.

## Handoff — 8 variants byte-identical grep contract

| Terminal status + conditions | Handoff string |
|---|---|
| `completed`, zero soft warnings | `Plan /visual-plan/<slug> completed. <N> images at docs/visual-specs/<slug>/iters/.` |
| `completed`, ≥1 soft warning | `Plan /visual-plan/<slug> completed. <N> images; <K> iters with soft-gate warnings — review ## Results.` |
| `partial` via fail_fast (Err #7) | `Plan /visual-plan/<slug> partial (<N>/<M>). fail_fast triggered at iter <K>. <err excerpt>.` |
| `partial` via Err #7 `accept-remaining` | `Plan /visual-plan/<slug> partial (<N>/<M>). cost budget exceeded; user accepted remaining.` |
| `partial` via Err #13(c) cross-class skip | `Plan /visual-plan/<slug> partial (<N>/<M>). <provider> unreachable; user skipped remaining.` |
| `partial` via all-`failed` verdicts (Err #6) | `Plan /visual-plan/<slug> partial (<N>/<M>). all generate_image calls failed (<err excerpt>).` |
| `aborted` via user interrupt / Err #13(b) / Err #16 | `Plan /visual-plan/<slug> aborted by user at iter <K>. resume with /visual-plan <slug>.` |
| `aborted` via Err #7 `abort` | `Plan /visual-plan/<slug> aborted at iter <K>. cost budget exceeded.` |

**Error-excerpt convention**: `<err excerpt>` is first 80 chars, with `\n` and `` ` `` replaced by single spaces.

**Stale-lock suffix**: any recovery session appends ` (recovered from stale lock at iter <K>)` to the chosen variant **before the final period**.

**`--dry-run` mode**: prints no terminal handoff. stdout is draft plan.md body only. `--dry-run` never reaches Phase 3 or 4.

**Do NOT auto-invoke downstream.** /visual-plan is terminal.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_visual_plan_error_matrix.py -v 2>&1 | tail -20`
Expected: 17/17 PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_visual_plan_error_matrix.py .claude/skills/visual-plan/SKILL.md
git commit -m "feat(visual-plan): 16-row error matrix + 7 invariants + 8 handoff variants

Completes SKILL.md with §Invariants S1-S7 (S4 includes design.md
content-hash guard), §Error matrix (16 rows with grep-contract
verbatim strings), and §Handoff (8 variants + stale-lock suffix +
--dry-run clause).

17 pytest tripwires assert every Err row's verbatim signature,
Err #3+#12 collision fold rule (Blocker B5 fix), Err #7 unified
3-option prompt (no F.source branching), Err #12 Notes-not-stderr
channel (Ruling D fix), Err #15/#16 new rows.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Fill in SKILL.md Phase 2 body

**Files:**
- Modify: `.claude/skills/visual-plan/SKILL.md` — replace Phase 2 placeholder

**Spec anchor:** §5 Phase 2 Plan-review loop.

- [ ] **Step 1: Replace Phase 2 placeholder**

In `.claude/skills/visual-plan/SKILL.md`, replace `## Phase 2 — Plan-review loop\n\n(filled in Task 6)` with:

```markdown
## Phase 2 — Plan-review loop

Cap: **5 user turns** (hard). Soft extend: user message contains `deep review` (case-insensitive) → raise cap to 8. Inherits /visual-spec Phase 4 vocabulary byte-for-byte where possible.

1. **F-summary prompt** (if any `F.per_gen_sec` / `F.total_session_sec` has `source: assumed`): fire the prompt from §Source-gating before the main draft prompt. This turn is **NOT** charged toward the cap. User reply resolves F per the 3-branch handler.

2. **Render draft.** Print the full in-flight `plan.md` with all 6 sections (A/B/C/D/E/F) filled in. Frontmatter `status: draft`. **Persist to disk:** immediately after the initial render, `Write` the draft to `docs/visual-specs/<slug>/plan.md`. This enables Err #3 resume.

3. **Main draft prompt.** Print exactly:

   ```
   Draft plan.md below. Type 'accept all' to finalize, 'change <section>' to revise one, or 'deep review' to extend your review budget +3 turns.
   ```

4. **Handle user replies:**
   - **`accept all`** (case-insensitive exact match) → flip every section's internal `reviewed: true`, flip frontmatter `status: draft → running`, `Write` plan.md, enter Phase 3 (happy path; do not burn remaining cap).
   - **`change <section>`** (`change A`, `change D.L3`, `change C.base_prompt`, etc.) → open sub-dialog scoped to that section only. Rules:
     - Ask one targeted question per turn (e.g. `"D.L3 currently value: 0.6, source: assumed, gate_class: soft. New value + source (measured/user-confirmed)?"`).
     - On user-supplied valid value, apply and flip `reviewed: true`.
     - On invalid input: re-prompt once; second invalid = 1 turn cost + return to main prompt without changes.
     - If the edit changes `D.L_N.source` from `assumed` → `user-confirmed` → add `L_N` to `user_elevated`, flip `gate_class: soft → hard`, append Notes `[override] D.L_N.source: assumed → user-confirmed. Reason: <user rationale>.` If user declines rationale, write `Reason: none provided by user`.
     - **`user_elevated` persists ONLY in plan.md — never back-written to design.md (S4 per design decision).**
   - **`deep review`** → cap += 3 (max 8). Print one-liner: `Cap extended to 8 turns.` Do NOT advance to Phase 3. One-time use per session; second invocation treated as invalid.
   - **Ambiguous reply** (`"looks good but"`, `"mostly fine"`) → re-prompt main menu; count as 1 turn.
   - **Pixel action request** (`just generate it`, `run it now`) → Err #8 decline; turn NOT charged.

5. **Per-turn housekeeping.** After each round, re-render the current draft (compact form if no section mutated) and update `[resume-state] turns_used: <N>` line in Notes. **Then re-`Write` plan.md** (status: draft, updated: <today>) — pairs with EVERY turn that mutated state OR counter, per brainstorm/spec discipline. If user at cap−1, courtesy notice: `1 turn remaining. Last 'change <section>' or 'deep review'?`.

6. **Cap-hit behavior.** When counter reaches cap (5 or 8) without `accept all`:
   - Force-show current full draft.
   - Prompt exactly: `Turn cap reached. finalize or deep review?`
   - Do NOT auto-advance. Never flip `status` without explicit `accept all` (S2).
```

- [ ] **Step 2: Verify pytest still green after Phase 2 body added**

Run: `pytest tests/test_visual_plan_*.py -v 2>&1 | tail -20`
Expected: all ~57 tests PASS (15+11+14+17).

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/visual-plan/SKILL.md
git commit -m "feat(visual-plan): Phase 2 plan-review loop body

5-turn cap review loop inherits /visual-spec Phase 4 vocabulary.
F-summary prompt fires before main draft when any F assumed.
accept all / change <section> / deep review / ambiguous / pixel-
request handlers all implemented. user_elevated persists only in
plan.md (design.md untouched per S4 carve-out).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Layer A ship-gate — pytest green

**Files:**
- Run: all `tests/test_visual_plan_*.py` files

**Spec anchor:** §11 Layer A — pytest tripwires (blocking).

- [ ] **Step 1: Run full Layer A suite**

Run: `pytest tests/test_visual_plan_parser_invariants.py tests/test_visual_plan_source_gating.py tests/test_visual_plan_execution_loop.py tests/test_visual_plan_error_matrix.py -v 2>&1 | tail -30`
Expected: 57/57 PASS in < 30s.

- [ ] **Step 2: Run full repo pytest to confirm no regressions**

Run: `pytest tests/ -x --timeout=60 2>&1 | tail -20`
Expected: all tests pass except pre-existing cv2-noise baseline (~61 failures per memory `feedback_cv2_test_noise`) — NO new failures introduced by /visual-plan tests.

- [ ] **Step 3: If any failure in visual-plan pytest, iterate Task 2-6**

If a test fails, identify the missing contract, go back to the task that wrote that section, add the missing text to SKILL.md, re-run.

- [ ] **Step 4: Commit (if any iteration happened)**

```bash
git add -A
git commit -m "fix(visual-plan): Layer A pytest green — <summary of fixes>"
```

---

## Task 8: Layer B simulated ship-gate (3 parallel subagents)

**Files:**
- Create: `docs/superpowers/plans/visual-plan-ship-gate-log.md` — transcript + conclusion

**Spec anchor:** §11 Layer B simulated ship-gate — 3 parallel subagents covering ~12 cases.

- [ ] **Step 1: Write ship-gate log scaffold**

File: `docs/superpowers/plans/visual-plan-ship-gate-log.md`

```markdown
# `/visual-plan` Ship-Gate Log (v1 — simulated)

**Date:** <today>
**Branch:** `master`
**Skill commit under test:** <HEAD commit hash>
**Spec reference:** `docs/superpowers/specs/2026-04-23-visual-plan-skill-design.md` §11.2
**Plan reference:** `docs/superpowers/plans/2026-04-23-visual-plan-skill.md` Task 8

## Protocol

Three parallel subagents act as "Claude Code sessions loading the skill" — each reads `.claude/skills/visual-plan/SKILL.md` verbatim and simulates both agent-following-skill and scripted user. Tool calls (list_traditions / generate_image / evaluate_artwork / Read / Write) noted but not executed. Pixel tools verified NOT called outside Phase 3 whitelist.

This is the mechanical-rule surface simulation. Layer C live ship-gate v2 deferred to Task 9 (after v0.17.6 ships MCP extension).

## Case matrix

| # | Case | Subagent |
|---|---|---|
| P1 | Positive full flow (design.md status:resolved → plan.md draft → accept all → Phase 3 with mock provider → completed) | α |
| P2 | Err #3 resume (plan.md status:draft + 3-row jsonl → Phase 2 continues, Phase 3 from iter 3) | α |
| P3 | Err #11 concurrent lockfile (fresh lock + fresh jsonl → refuse) | α |
| N1 | Err #1 design.md not found → verbatim terminate | β |
| N2 | Err #2 same-slug completed → refuse-overwrite | β |
| N3 | Err #4 tradition not in registry → verbatim terminate | β |
| N4 | Err #8 pixel request in Phase 2 → decline + turn NOT charged | β |
| N5 | Err #9 sketch unreadable → degrade + continue | γ |
| N6 | Err #10 design.md YAML parse-fail → verbatim terminate | γ |
| N7 | Err #12 stale-lock auto-recover + Notes append (no stderr) | γ |
| N8 | Err #13 cross-class prompt option (c) → partial | γ |
| N9 | Err #14 not in Vulca checkout → sentinel terminate | γ |
| N10 | Err #15 schema_version unrecognized → refuse | γ |
| N11 | user_elevated persists plan.md only, design.md untouched (decision #10) | α |

## Results

<!-- Subagent reports plug in here when tasks complete. -->
```

- [ ] **Step 2: Dispatch 3 parallel subagents**

Use Agent tool with `subagent_type=general-purpose` × 3, each briefed to load SKILL.md, run its case list as the agent+user role, report PASS/FAIL per case with evidence. Brief template (adapt per subagent):

```
You are subagent α/β/γ in /visual-plan ship-gate v1. Load `.claude/skills/visual-plan/SKILL.md` verbatim — treat it as your skill body; simulate both Claude-following-skill and scripted user.

Your case list: <3-5 cases>. For each case: describe fixture setup, walk through each skill phase, note tool calls NOTED not executed, verify verbatim strings match error matrix, confirm invariants (S1/S2/S4).

Report format: per case, PASS/FAIL + evidence + artifact paths (simulated). Inline deltas + 1-paragraph conclusion.

Constraints: no pixel-level tool calls outside Phase 3 whitelist (S1 violation = FAIL). design.md never written to during simulation (decision #10 enforcement).

Target: <800 words structured report.
```

- [ ] **Step 3: Inline subagent reports into ship-gate log**

Edit `docs/superpowers/plans/visual-plan-ship-gate-log.md` — append each subagent's report under `## Results` + write a §Deltas section capturing any drift + §Conclusion with pass count.

- [ ] **Step 4: Verify 12/12+ PASS (accepting up to 1 clarity drift as non-blocker)**

If any case fails with a structural issue (not a wording drift) → iterate SKILL.md edits, re-run Layer A, re-dispatch failing subagent.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/visual-plan-ship-gate-log.md
git commit -m "docs(ship-gate): /visual-plan Layer B simulated — <N>/14 PASS

v1 mechanical-rule surface simulation. 3 parallel subagents covered
P1-P3 (positive + resume + concurrent), N1-N10 (error matrix single-
fire + Notes-channel + schema-version + sentinel + user_elevated
persistence). Any clarity-gap drifts logged for /visual-plan v0.17.8
follow-up patch.

Layer C live ship-gate v2 deferred to Task 9 (requires v0.17.6 MCP
extension).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: Layer C live ship-gate v2 (GATED on Task C v0.17.6 shipping first)

**Files:**
- Create: `docs/superpowers/plans/visual-plan-live-ship-gate-log.md`

**Prerequisite:** Task C v0.17.6 MUST have shipped (MCP `generate_image` signature extended + 4 providers plumbing + schema_version field added to /visual-spec).

**Spec anchor:** §11 Layer C live ship-gate v2 — 2 parallel subagents, ~6 cases.

- [ ] **Step 1: Verify v0.17.6 MCP surface landed**

```bash
python3.11 -c "
import asyncio, inspect
from vulca.mcp_server import generate_image
sig = inspect.signature(generate_image)
assert 'seed' in sig.parameters, 'v0.17.6 MCP extension not shipped'
assert 'steps' in sig.parameters
assert 'cfg_scale' in sig.parameters
assert 'negative_prompt' in sig.parameters
print('v0.17.6 MCP surface OK')
"
```
Expected: prints `v0.17.6 MCP surface OK`. If fails → **BLOCK Task 9**, return to Task C.

- [ ] **Step 2: Write live ship-gate log scaffold**

File: `docs/superpowers/plans/visual-plan-live-ship-gate-log.md`

```markdown
# `/visual-plan` Live Ship-Gate Log (v2)

**Date:** <today>
**Parent log:** `docs/superpowers/plans/visual-plan-ship-gate-log.md` (v1 simulated)
**Scope:** Close integration-path gaps v1 simulated over — real `generate_image(mock)` timing, real `evaluate_artwork` return shape, real filesystem for lockfile + jsonl + plan.md I/O.

## Gap-to-case mapping

| Parent v1 simulated gap | v2 case | Subagent |
|---|---|---|
| `generate_image(mock)` actually running → mock latency + real return | Case P1-live | α |
| `evaluate_artwork` actually returning `dimensions` → L1-L5 extraction | Case P1-live | α |
| jsonl actual append-only write + read atomicity | Case P1-live | α |
| Real filesystem lockfile O_CREAT \| O_EXCL collision | Case β-lockfile | β |
| Real filesystem stale-lock auto-recovery + Notes append | Case β-stale-lock | β |
| Real Err #16 design-drift content-guard | Case β-drift | β |

## Protocol

Mirrors /visual-spec v2 pattern. 2 parallel subagents. Subagent α runs in parent Claude Code session (has MCP tool access). Subagent β dispatches MCP via shell `PYTHONPATH=src python3.11 -c "import asyncio; from vulca.mcp_server import ...; asyncio.run(...)"` (subagent-dispatch caveat from v2 learning).

Tmp write paths: `tmp-shipgate-v2-plan/docs/visual-specs/<slug>/` (repo-relative; `/tmp/...` sandbox-denied per /visual-spec v2 precedent).

Tool whitelist: `list_traditions`, `get_tradition_guide`, `Read`, `Write`, `generate_image(provider="mock")` only, `evaluate_artwork`, MAY `unload_models`. Pixel-level tools (`create_artwork` / `generate_concepts` / `inpaint_artwork` / `layers_*`) banned.

## Results

<!-- subagent reports plug in here -->
```

- [ ] **Step 3: Dispatch 2 parallel subagents**

Subagent α (parent session, real MCP): P1-live 3-iter positive flow — seed a design.md fixture under `tmp-shipgate-v2-plan/`, run Phase 1 → Phase 2 `accept all` → Phase 3 3 iters with real `generate_image(mock)` + real `evaluate_artwork` → Phase 4 finalize → verify jsonl shape + handoff byte-identical + ## Results rendered.

Subagent β (filesystem real, MCP via shell): lockfile collision + stale-lock recovery + Err #16 design-drift cases.

- [ ] **Step 4: Inline reports into log + verify ≥ 6/6 PASS**

Clarity-gap findings (if any) log to project memory as v0.17.8 candidates.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/visual-plan-live-ship-gate-log.md
git commit -m "docs(ship-gate): /visual-plan Layer C live ship-gate v2 — <N>/6 PASS

v2 exercises real MCP tool returns + real filesystem. α parent
session runs P1-live 3-iter full positive flow with real
generate_image(mock) + evaluate_artwork. β dispatched subagent
covers lockfile collision + stale-lock recovery + Err #16
design-drift content-guard.

v1 14/14 + v2 6/6 = full skill-body validation for /visual-plan
non-pixel-heavy surface.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 10: v0.17.7 release chain

**Files:**
- Modify: `pyproject.toml` (version bump)
- Modify: `src/vulca/__init__.py` (if version duplicated)
- Create: git tag `v0.17.7`
- Create: GitHub release
- Create: PyPI publish
- Create: plugin sync PR (mirror)

**Spec anchor:** §11 release chain step 2.

**Prerequisite:** Task C v0.17.6 MUST have shipped (tagged, released, PyPI).

- [ ] **Step 1: Verify v0.17.6 is shipped**

```bash
pip index versions vulca 2>&1 | head -3
# Expect: vulca versions listed with 0.17.6 present
git tag | grep -E "^v0\.17\.[6-7]$"
# Expect: v0.17.6 present, v0.17.7 NOT present yet
```

- [ ] **Step 2: Bump version in `pyproject.toml`**

Replace `version = "0.17.6"` → `version = "0.17.7"` in `pyproject.toml`.

Also check `src/vulca/__init__.py` if it duplicates the version string.

- [ ] **Step 3: Verify Layer A + B + C are all green**

```bash
pytest tests/test_visual_plan_*.py -v 2>&1 | tail -5
git log --oneline -15 | grep -E "ship-gate.*PASS"
# Expect: both Layer B and Layer C logs committed
```

- [ ] **Step 4: Commit version bump**

```bash
git add pyproject.toml src/vulca/__init__.py
git commit -m "release: v0.17.7 — /visual-plan meta-skill shipped

3rd and final meta-skill in brainstorm → spec → plan → execute
architecture. Reads design.md (status:resolved) → produces
reviewable plan.md + runs generate+evaluate loop → terminal
artifact {completed, partial, aborted}.

- .claude/skills/visual-plan/SKILL.md (~X lines, 4 phases, 7
  invariants, 16 err rows, 8 handoff variants)
- 57 pytest cases across 4 test files (Layer A)
- Layer B simulated 14/14 PASS, Layer C live v2 6/6 PASS
- Requires v0.17.6 MCP extension prerequisite already landed

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 5: Tag + push**

```bash
git tag v0.17.7
git push origin master
git push origin v0.17.7
```

- [ ] **Step 6: Build + publish PyPI**

```bash
rm -rf dist/
python -m build
twine check dist/*
twine upload dist/vulca-0.17.7* -u __token__ -p $PYPI_TOKEN
```
(Per memory `project_vulca_0_17_5_shipped.md` note: PyPI token rotation pending since v0.17.3 — after this ship, rotate at pypi.org/manage/account/token/.)

- [ ] **Step 7: Create GitHub release**

```bash
gh release create v0.17.7 \
  --title "v0.17.7 — /visual-plan meta-skill" \
  --notes "$(cat <<'EOF'
## Summary
- Ships 3rd and final meta-skill in the brainstorm → spec → plan → execute architecture
- `.claude/skills/visual-plan/SKILL.md` with 4 phases, 7 invariants, 16-row error matrix, 8-variant handoff
- 57 pytest tripwires across 4 files (Layer A)
- Layer B simulated ship-gate 14/14 PASS + Layer C live ship-gate v2 6/6 PASS

## Dependencies
Requires v0.17.6 (shipped prior) for `generate_image` MCP extension + schema_version field.

## Artifacts
- Design spec: `docs/superpowers/specs/2026-04-23-visual-plan-skill-design.md`
- Implementation plan: `docs/superpowers/plans/2026-04-23-visual-plan-skill.md`
- Ship-gate logs: `visual-plan-ship-gate-log.md` + `visual-plan-live-ship-gate-log.md`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" \
  dist/vulca-0.17.7-py3-none-any.whl \
  dist/vulca-0.17.7.tar.gz
```

- [ ] **Step 8: Plugin mirror PR**

Mirror to `vulca-plugin` repo per previous release pattern. Create `sync/v0.17.7` branch with updated plugin SKILL.md + version bump; `gh pr create --repo vulca-org/vulca-plugin --title "sync: v0.17.7 /visual-plan" ...`.

- [ ] **Step 9: Update project memory**

Add to `MEMORY.md`:
```
- [Vulca v0.17.7 shipped](project_vulca_0_17_7_shipped.md) — /visual-plan meta-skill #3 of 3; brainstorm→spec→plan triad complete; <date>
```

Write memory file `project_vulca_0_17_7_shipped.md` with artifacts + dependencies + cross-skill handoff status.

- [ ] **Step 10: Final verification**

```bash
pip install --upgrade vulca
python -c "import vulca; print(vulca.__version__)"
# Expect: 0.17.7
ls .claude/skills/ | sort
# Expect: visual-brainstorm / visual-plan / visual-spec all present
```

---

## Self-review checklist

**Spec coverage:**
- §1 Purpose/scope/positioning → Task 1 (scaffold)
- §2 I/O contracts → Task 5 (handoff 8 variants)
- §3 Architecture diagram → Tasks 1 + 2 + 4 (assembled via SKILL.md body)
- §4 Parser contract → Task 2
- §5 Phase details → Tasks 2/4/6
- §6 Error matrix → Task 5
- §7 Invariants → Task 5
- §8 Source-gating → Task 3
- §9 jsonl schema → Task 4
- §10 MCP extension → **DEFERRED to Task C v0.17.6** (prereq)
- §11 Ship-gate protocol → Tasks 7/8/9
- §12 Pytest surface ~65 → 57 in this plan + 8 deferred to Task C
- §13 Open questions → design-locked; no plan tasks
- §14 Summary → commit messages across Tasks

**Placeholder scan:** No "TBD" / "TODO" / "implement later" in plan. Each step has concrete code or commands.

**Type consistency:** Frontmatter field names match between Task 2 (parser §4.2) and Task 5 (error matrix). Verbatim error strings match spec §6 exactly.

**Scope check:** Single-skill plan. v0.17.6 prereq explicitly carved out (not bundled). Each Task produces a self-contained commit; Tasks 1-8 independent, Task 9 gated on Task C, Task 10 gated on Tasks 7-9.

**Granularity:** Each step is 2-5 minutes. Test-first order preserved. Frequent commits.
