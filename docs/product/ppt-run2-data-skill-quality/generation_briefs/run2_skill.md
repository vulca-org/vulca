# Run 2.0 Skill

Arm id: `run2_skill`.

Use commercial case, multimodal database, visual learning targets, visual target components, video demo beat map, motion learning targets, presentation sequence components, production reference decompositions, aesthetic memory v2, visual production modules, source cards, video cards, evidence memory, aesthetic memory, asset memory, narrative spine, slide archetypes, and the Run 2.0 staged deck-director skill.

The arm must generate a code-first PPT with editable native text and structures. It must select source/evidence/aesthetic/asset memory before writing slide code, enforce density budgets and negative rules, apply the deletion rule, and keep public-ready claims blocked until render, provenance, and human approval gates pass.

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
- `aesthetic_memory_v2.json`
- `visual_production_modules.json`
- `source_cards/`
- `video_cards/`
- `evidence_memory.json`
- `aesthetic_memory.json`
- `asset_memory.json`
- `narrative_spine.json`
- `slide_archetypes.json`
- `aesthetic_rubric.md`
- `vulca_ppt_skill.md`

## Forbidden Inputs

- Run 1.5 product-lab skill files, except for final comparison after generation.
- `generation_briefs/bad_aesthetic_memory_replacement.json`
- Copied source screenshots, layouts, logos, transcripts, or brand marks.
- Any claim that Run 2.0 won before scoring is complete.

## Trace Output

Write `trace_manifest.json` under the arm's local `outputs/` directory with one record per slide: selected multimodal record ids, anchor ids, visual learning target ids, visual component ids, video beat ids, motion target ids, sequence component ids, ordered native reveal steps, production reference ids, aesthetic memory v2 ids, visual production module ids, fallback policy, memory ids, density counts, deleted or routed content, asset provenance, QA outcomes, repair actions, and release-gate status.
