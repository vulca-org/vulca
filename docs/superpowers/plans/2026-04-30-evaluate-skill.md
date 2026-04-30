# Evaluate Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `/evaluate` as a minimal user-facing skill over existing `evaluate_artwork`, closing the Discover -> Spec -> Generate/Edit -> Evaluate loop.

**Architecture:** This is a skill/docs/test packaging change. It adds `.agents` and `.claude` skill files, updates the Vulca skill router, updates README/product roadmap wording, and adds contract tests. It does not change runtime scoring code, provider code, redraw code, or evaluation algorithms.

**Tech Stack:** Markdown skills, pytest doc/skill contract tests, existing MCP `evaluate_artwork`, existing `view_image` and `get_tradition_guide`.

---

## Task 1: Add Evaluate Skill Contract Tests

**Files:**
- Create: `tests/test_evaluate_skill_contract.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_evaluate_skill_contract.py` with:

```python
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
AGENTS_SKILL = ROOT / ".agents" / "skills" / "evaluate" / "SKILL.md"
CLAUDE_SKILL = ROOT / ".claude" / "skills" / "evaluate" / "SKILL.md"
AGENTS_ROUTER = ROOT / ".agents" / "skills" / "using-vulca-skills" / "SKILL.md"
CLAUDE_ROUTER = ROOT / ".claude" / "skills" / "using-vulca-skills" / "SKILL.md"


def test_evaluate_skill_exists_and_wraps_existing_tool():
    body = AGENTS_SKILL.read_text(encoding="utf-8")

    assert "name: evaluate" in body
    assert "evaluate_artwork" in body
    assert "view_image" in body
    assert "get_tradition_guide" in body
    assert "L1-L5" in body
    assert "evaluation.md" in body
    assert "evaluation.json" in body


def test_evaluate_skill_bans_generation_and_layer_tools():
    body = AGENTS_SKILL.read_text(encoding="utf-8")

    assert "`generate_image`" in body
    assert "`create_artwork`" in body
    assert "`generate_concepts`" in body
    assert "`inpaint_artwork`" in body
    assert "`layers_*`" in body
    assert "must not execute pixel edits" in body.lower()


def test_router_invokes_evaluate_for_scoring_requests():
    body = AGENTS_ROUTER.read_text(encoding="utf-8")

    assert "evaluate an existing image" in body
    assert "`evaluate`" in body
    assert "L1-L5" in body
    assert "文化评分" in body


def test_claude_mirror_matches_evaluate_routing():
    skill = CLAUDE_SKILL.read_text(encoding="utf-8")
    router = CLAUDE_ROUTER.read_text(encoding="utf-8")

    assert "name: evaluate" in skill
    assert "evaluate_artwork" in skill
    assert "evaluation.md" in skill
    assert "evaluate an existing image" in router
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
PYTHONPATH=src pytest tests/test_evaluate_skill_contract.py -q
```

Expected: failure because the evaluate skill files do not exist.

---

## Task 2: Add `/evaluate` Skill

**Files:**
- Create: `.agents/skills/evaluate/SKILL.md`
- Create: `.claude/skills/evaluate/SKILL.md`

- [ ] **Step 1: Create the skill body**

Create `.agents/skills/evaluate/SKILL.md` with:

```markdown
---
name: evaluate
description: Evaluate an existing visual artifact against a tradition, intent, and L1-L5 cultural/visual rubric.
---

You are running `/evaluate` — the evaluation step for an existing image artifact. Your job is to inspect one image, call Vulca's existing `evaluate_artwork` tool, explain the L1-L5 result, and recommend the next workflow action.

## Triggers

- Slash command: `/evaluate <image_path>` or `/evaluate <slug>`
- Chinese aliases: `评价这张图`, `文化评分`, `L1-L5 评分`, `帮我判断这张图`
- Intent auto-match: the user asks whether an image fits a tradition, brief, culture, or visual direction; asks for cultural critique; asks for L1-L5 scoring; or asks what to improve after generation.

## Scope

Evaluate one existing image. Do not generate, edit, redraw, decompose, or composite images.

## Inputs

- Required: `image_path` or `slug`.
- Optional: `tradition`, `intent`, `mode`, `mock`, `vlm_model`, `write_artifacts`.
- `mode`: `strict`, `reference`, or `rubric_only`.
- `mock`: only for no-cost shape checks and tests. Never present mock scores as real quality evidence.

## Path Resolution

If the user provides a file path, verify it exists before calling any tool.

If the user provides a slug, search in this order:

1. `docs/visual-specs/<slug>/iters/**/gen_*`
2. `docs/visual-specs/<slug>/iters/**/*.{png,jpg,jpeg,webp}`
3. `docs/visual-specs/<slug>/source.{png,jpg,jpeg,webp}`

If more than one image is found, ask the user which image to evaluate.

## Allowed Tools

- `view_image`
- `get_tradition_guide`
- `evaluate_artwork`
- Read/write project docs

## Forbidden Tools

- `generate_image`
- `create_artwork`
- `generate_concepts`
- `inpaint_artwork`
- `layers_*`

If the evaluation recommends an edit, explain the next action. You must not execute pixel edits from this skill.

## Workflow

1. Resolve and verify the image path.
2. If a tradition is provided, call `get_tradition_guide(tradition)` and use it to explain L1-L5 context.
3. Call `view_image(image_path)` when visual grounding is useful.
4. Call `evaluate_artwork(image_path, tradition=<tradition>, intent=<intent>, mode=<mode>, mock=<mock>, vlm_model=<vlm_model>)`.
5. Extract `score`, `tradition`, `dimensions`, `rationales`, `recommendations`, `risk_flags`, and `risk_level`.
6. If all L1-L5 scores are zero or missing, mark the result as suspect and recommend rerunning with a real VLM or checking credentials.
7. Explain strongest dimensions, weakest dimensions, and concrete next action.
8. When a slug is known or `write_artifacts=true`, write:
   - `docs/visual-specs/<slug>/evaluation.md`
   - `docs/visual-specs/<slug>/evaluation.json`

## User-Facing Response

Include:

- image path
- tradition and mode
- overall score
- L1-L5 summary
- strongest dimensions
- weakest dimensions
- recommendations
- risk flags
- next action

Next action must be one of:

- `accept`
- `revise prompt`
- `rerun /visual-plan`
- `redraw target after v0.22 route is available`
- `run /visual-discovery`

## Artifact Contract

`evaluation.md`:

```markdown
# Evaluation: <slug or image stem>

## Status
evaluated

## Image
<path>

## Tradition
<tradition>

## Mode
<mode>

## Overall Score
<score or unavailable>

## L1-L5
<table>

## Recommendations
<bullets>

## Risk Flags
<bullets or none>

## Next Action
<decision>
```

`evaluation.json`:

```json
{
  "schema_version": "0.1",
  "image_path": "...",
  "tradition": "...",
  "mode": "...",
  "intent": "...",
  "evaluate_artwork": {}
}
```
```

Copy the same file to `.claude/skills/evaluate/SKILL.md`.

- [ ] **Step 2: Run tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_evaluate_skill_contract.py -q
```

Expected: router tests still fail until Task 3.

---

## Task 3: Route `/evaluate`

**Files:**
- Modify: `.agents/skills/using-vulca-skills/SKILL.md`
- Modify: `.claude/skills/using-vulca-skills/SKILL.md`

- [ ] **Step 1: Update router frontmatter description**

Change description to include:

```text
discovery -> brainstorm -> spec -> plan -> evaluate chain
```

- [ ] **Step 2: Add route row**

Add this row before `/visual-plan`:

```markdown
| evaluate an existing image against a tradition/brief, ask for L1-L5 scoring, cultural critique, "评价这张图", "文化评分"; image already exists | `evaluate` |
```

- [ ] **Step 3: Add reference**

Add `.agents/skills/evaluate/SKILL.md` and `.claude/skills/evaluate/SKILL.md` to each router reference list respectively.

- [ ] **Step 4: Run tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_evaluate_skill_contract.py tests/test_visual_discovery_skill_contract.py -q
```

Expected: pass.

---

## Task 4: Update README and Product Roadmap

**Files:**
- Modify: `README.md`
- Modify: `docs/product/roadmap.md`
- Modify: `tests/test_visual_discovery_docs_truth.py`

- [ ] **Step 1: Add doc truth assertions**

Extend `tests/test_visual_discovery_docs_truth.py` with:

```python
def test_readme_and_roadmap_mark_evaluate_skill_current():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "product" / "roadmap.md").read_text(
        encoding="utf-8"
    )

    assert "✅ `/evaluate`" in readme
    assert "`/evaluate`: user-facing evaluation skill" in roadmap
    assert "/evaluate` skill packaging" not in roadmap
```

- [ ] **Step 2: Run tests and confirm failure**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_docs_truth.py -q
```

Expected: failure until README/roadmap are updated.

- [ ] **Step 3: Update README**

In README:

- Change Evaluate row in "What Vulca takes off your agent's hands" from Roadmap to `✅ /evaluate`.
- In the Evaluate details section, replace "No agent skill yet — `/evaluate` is next on the roadmap" with "The `/evaluate` skill wraps `evaluate_artwork` for agent-led critique and next-action guidance."
- In the top capability matrix, change Evaluate status from "Tool current, skill next" to "Current".

- [ ] **Step 4: Update roadmap**

In `docs/product/roadmap.md`:

- Add current bullet: `` `/evaluate`: user-facing evaluation skill over existing `evaluate_artwork`. ``
- Remove the "Next" bullet for `/evaluate` skill packaging.

- [ ] **Step 5: Run docs tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_docs_truth.py -q
```

Expected: pass.

---

## Task 5: Final Verification and Commit

**Files:**
- All above.

- [ ] **Step 1: Run focused tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_evaluate_skill_contract.py tests/test_visual_discovery_skill_contract.py tests/test_visual_discovery_docs_truth.py tests/test_evaluate.py tests/test_mcp_v2.py tests/test_mcp_server.py -q
```

Expected: pass.

- [ ] **Step 2: Scan for unfinished markers**

Run:

```bash
grep -RInE "TB[D]|TO[D]O|lo[r]em|coming soo[n]" .agents/skills/evaluate .claude/skills/evaluate docs/superpowers/specs/2026-04-30-evaluate-skill-design.md docs/superpowers/plans/2026-04-30-evaluate-skill.md README.md docs/product/roadmap.md
```

Expected: no matches.

- [ ] **Step 3: Commit**

Run:

```bash
git add .agents/skills/evaluate/SKILL.md .claude/skills/evaluate/SKILL.md .agents/skills/using-vulca-skills/SKILL.md .claude/skills/using-vulca-skills/SKILL.md README.md docs/product/roadmap.md docs/superpowers/specs/2026-04-30-evaluate-skill-design.md docs/superpowers/plans/2026-04-30-evaluate-skill.md tests/test_evaluate_skill_contract.py tests/test_visual_discovery_docs_truth.py
git commit -m "feat: add evaluate skill"
```
