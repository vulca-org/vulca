# Bad Aesthetic Memory

Arm id: `bad_aesthetic_memory`.

Use valid evidence memory but intentionally weak aesthetic memory: repeated dashboard grids, dense tables, small labels, low rhythm variance, no visual climax, and no low-density high-impact slides. This is the negative control for the aesthetic layer.

The arm should remain traceable enough to avoid becoming a random failure. Its purpose is to test whether bad aesthetic memory degrades an otherwise valid evidence, multimodal, motion grammar, and production-reference workflow.

## Allowed Inputs

- `commercial_case.md`
- `sources.json`
- `multimodal_database.json`
- `visual_learning_targets.json`
- `visual_target_components.json`
- `video_demo_beat_map.json`
- `motion_learning_targets.json`
- `presentation_sequence_components.json`
- `production_reference_decompositions.json`
- `source_cards/`
- `video_cards/`
- `evidence_memory.json`
- `asset_memory.json`
- `narrative_spine.json`
- `vulca_ppt_skill.md`
- `generation_briefs/bad_aesthetic_memory_replacement.json`

## Forbidden Inputs

- Good `aesthetic_memory.json`
- Good `aesthetic_memory_v2.json`
- Good `visual_production_modules.json`
- Good `slide_archetypes.json`
- Run 1.5 product-lab skill files
- Any manual aesthetic repair that restores low density, cinematic opening, rhythm variance, or a visual climax before scoring.

## Replacement Memory

Use `bad_aesthetic_memory_replacement.json` as the exact replacement for `aesthetic_memory.json`. Do not treat this as a loose prose prompt. The arm is valid only if the trace manifest records the replacement move ids used on each slide.

## Trace Output

Write `trace_manifest.json` under the arm's local `outputs/` directory with one record per slide: bad replacement move ids, visual component ids, video beat ids, motion target ids, sequence component ids, density counts, repeated-template evidence, asset provenance, QA outcomes, and release-gate status.
