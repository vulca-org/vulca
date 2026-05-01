---
name: evaluate
description: Evaluate an existing visual artifact against a tradition, intent, and L1-L5 cultural/visual rubric.
---

You are running `/evaluate` - the evaluation step for an existing image artifact. Your job is to inspect one image, call Vulca's existing `evaluate_artwork` tool, explain the L1-L5 result, and recommend the next workflow action.

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
- `redraw target with dogfooded v0.22 route`
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
