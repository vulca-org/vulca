# `/evaluate` Skill Design Spec

**Date:** 2026-04-30
**Status:** Approved minimal v1 design
**Depends on:** `codex/product-positioning-plan`
**Scope:** Agent skill packaging for existing `evaluate_artwork`; no runtime scoring changes

`/evaluate` closes the first product loop after `/visual-discovery` and `/visual-plan`: a user can score an existing image, understand L1-L5 strengths and failures, and choose the next action. The skill exposes the existing `evaluate_artwork` MCP tool as a disciplined agent workflow rather than adding a new scoring implementation.

---

## 1. Product Role

`/evaluate` is the first user-facing evaluation skill. It completes this loop:

```text
Discover -> Spec -> Generate/Edit -> Evaluate -> Iterate
```

It should be positioned as:

```text
Evaluate a finished or intermediate visual artifact against a tradition, intent,
and L1-L5 cultural/visual rubric.
```

The skill turns numeric scoring into product behavior: accept, revise prompt, redraw a target, or rerun a plan.

---

## 2. Scope

### In Scope

- Evaluate one existing image path.
- Support `tradition`, `intent`, `mode`, `mock`, and `vlm_model` options.
- Call `view_image` before scoring when image grounding is useful.
- Call `get_tradition_guide` when a tradition is supplied.
- Call `evaluate_artwork`.
- Summarize score, L1-L5 dimensions, rationales, recommendations, risk flags, and next action.
- Optionally write an evaluation artifact beside a visual project:
  - `docs/visual-specs/<slug>/evaluation.md`
  - `docs/visual-specs/<slug>/evaluation.json`

### Out of Scope

- Changing `evaluate_artwork` scoring behavior.
- Running generation.
- Running layer tools, redraw, inpaint, or composite.
- Running cultural-term efficacy benchmarks.
- Comparing multiple candidate images in v1.
- Updating `plan.md` or `design.md`.

---

## 3. Triggering

Explicit:

- `/evaluate <image_path>`
- `/evaluate <slug>`

Chinese aliases:

- `评价这张图`
- `文化评分`
- `L1-L5 评分`
- `帮我判断这张图`

Intent auto-match:

- user asks whether an image fits a tradition/brief;
- user asks for L1-L5 score;
- user asks for cultural critique of a generated image;
- user asks what to improve after generation.

If the user asks to run a generation loop, route to `/visual-plan`, not `/evaluate`.

---

## 4. Inputs

Required:

- `image_path`, or a `slug` that can resolve to a recent image artifact.

Optional:

- `tradition`: default auto-detect / `default`.
- `intent`: user's brief or desired expression.
- `mode`: `strict`, `reference`, or `rubric_only`.
- `mock`: explicit no-cost scoring mode for tests/demos.
- `vlm_model`: override VLM model.
- `write_artifacts`: default true when slug is known, false for ad hoc image paths.

Path rule:

- Reject missing image paths before calling `evaluate_artwork`.
- If slug is provided, search in this order:
  - `docs/visual-specs/<slug>/iters/**/gen_*`
  - `docs/visual-specs/<slug>/iters/**/*.{png,jpg,jpeg,webp}`
  - `docs/visual-specs/<slug>/source.{png,jpg,jpeg,webp}`

---

## 5. Tool Policy

Allowed:

- `view_image`
- `get_tradition_guide`
- `evaluate_artwork`
- read/write project docs

Forbidden:

- `generate_image`
- `create_artwork`
- `generate_concepts`
- `inpaint_artwork`
- any `layers_*` tool
- modifying `design.md` or `plan.md`

If evaluation recommends an edit, the skill should produce next-action guidance only. It must not execute pixel edits.

---

## 6. Output Contract

The user-facing response must include:

- image path;
- tradition and mode;
- overall score if present;
- L1-L5 summary;
- strongest dimensions;
- weakest dimensions;
- recommendations;
- risk flags if any;
- next action:
  - `accept`
  - `revise prompt`
  - `rerun /visual-plan`
  - `redraw target after v0.22 route is available`
  - `run /visual-discovery` if the brief is unclear

Artifact markdown should include:

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

JSON artifact should preserve the raw `evaluate_artwork` return plus metadata:

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

---

## 7. Error Handling

- Missing image path: stop and ask for a path or slug.
- Image file does not exist: stop before tool call and show exact path checked.
- Unknown tradition: call `list_traditions` or ask the user to choose a supported tradition.
- `evaluate_artwork` returns error: show the error and recommend `mock=True` only for no-cost shape checks.
- All-zero scores: mark result as suspect and recommend rerunning with a real VLM or checking provider credentials.

---

## 8. Acceptance Criteria

- `.agents/skills/evaluate/SKILL.md` exists.
- `.claude/skills/evaluate/SKILL.md` mirror exists.
- `using-vulca-skills` routes evaluation requests to `evaluate`.
- Skill bans generation and layer tools.
- README says `/evaluate` is current, not next.
- Product roadmap lists `/evaluate` as current.
- Tests verify skill contract and router mirror.
- Existing `evaluate_artwork` tests still pass.
