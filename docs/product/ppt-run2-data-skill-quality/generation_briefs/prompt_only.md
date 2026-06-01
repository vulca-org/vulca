# Prompt Only

Arm id: `prompt_only`.

Use the commercial brief only. Do not use evidence memory, aesthetic memory, asset memory, source cards, video cards, Run 1.5 skill files, or Run 2.0 skill files.

This arm tests whether a prompt alone can produce a commercially specific, editable, public-demo-quality six-slide deck. It is not allowed to borrow the structured memory layer after generation starts.

## Allowed Inputs

- `commercial_case.md`

## Forbidden Inputs

- `sources.json`
- `source_cards/`
- `video_cards/`
- `evidence_memory.json`
- `aesthetic_memory.json`
- `asset_memory.json`
- `narrative_spine.json`
- `slide_archetypes.json`
- `vulca_ppt_skill.md`
- Run 1.5 product-lab skill files

## Trace Output

Write `trace_manifest.json` under the arm's local `outputs/` directory with the prompt, slide ids, native-editability checks, and release-gate status.
