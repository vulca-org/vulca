# Run 1.5 Skill

Arm id: `run1_5_skill`.

Use the previous evidence-heavy product-lab workflow as the current baseline. This arm is expected to be more traceable than prompt-only but more report-like than Run 2.0.

Do not use Run 2.2 multimodal database, visual learning targets, aesthetic memory, asset memory, video cards, or slide archetypes. Preserve the older workflow's emphasis on evidence traceability so the comparison can isolate whether the new multimodal, aesthetic, and asset layers matter.

## Allowed Inputs

- `commercial_case.md`
- Prior Run 1.5 product-lab workflow files under `docs/product/ppt-run1-5-product-lab/`

## Forbidden Inputs

- `source_cards/`
- `multimodal_database.json`
- `visual_learning_targets.json`
- `video_cards/`
- `evidence_memory.json`
- `aesthetic_memory.json`
- `asset_memory.json`
- `narrative_spine.json`
- `slide_archetypes.json`
- `vulca_ppt_skill.md`
- `generation_briefs/run2_skill.md`
- `generation_briefs/bad_aesthetic_memory_replacement.json`

## Trace Output

Write `trace_manifest.json` under the arm's local `outputs/` directory with the Run 1.5 evidence ids used, slide density counts, native-editability checks, and release-gate status.
