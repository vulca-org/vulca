# Generation Briefs

Status: not-run.

Run 2.5 keeps the same four-arm comparison: `prompt_only`, `run1_5_skill`, `run2_skill`, and `bad_aesthetic_memory`.

Each arm must use the same commercial case and six-slide target unless the arm definition explicitly excludes a data layer. Generated decks, previews, contact sheets, and layout JSON remain local under `outputs/`.

Run every arm under `generation_protocol.md` with a fresh prompt/context, separate output directory, and explicit allowed/forbidden input manifest. Do not reuse generated slide code, cached summaries, layout JSON, SVG assets, screenshots, or repair notes across arms.

## Arm Isolation Matrix

| Arm | Allowed inputs | Forbidden inputs | Attribution question |
| --- | --- | --- | --- |
| `prompt_only` | `commercial_case.md` only | multimodal database, visual learning targets, visual target components, video demo beat map, motion learning targets, presentation sequence components, production reference decompositions, aesthetic memory v2, visual production modules, source cards, video cards, evidence memory, aesthetic memory, asset memory, narrative spine, slide archetypes, Run 1.5 skill, Run 2.0 skill | What does the commercial brief alone produce? |
| `run1_5_skill` | `commercial_case.md` plus prior Run 1.5 product-lab workflow files | Run 2.5 multimodal database, visual learning targets, visual target components, video demo beat map, motion learning targets, presentation sequence components, production reference decompositions, aesthetic memory v2, visual production modules, source cards, video cards, evidence memory, aesthetic memory, asset memory, narrative spine, slide archetypes, Run 2.0 skill | What does the prior evidence-heavy workflow produce without the new multimodal/aesthetic/motion/production layer? |
| `run2_skill` | full Run 2.5 package, including `multimodal_database.json`, `visual_learning_targets.json`, `visual_target_components.json`, `video_demo_beat_map.json`, `motion_learning_targets.json`, `presentation_sequence_components.json`, `production_reference_decompositions.json`, `aesthetic_memory_v2.json`, `visual_production_modules.json`, and staged deck-director skill | copied source visuals, raw audio/video/transcripts, screenshots, brand marks, unapproved release assets, post-training or fine-tuning claims | What does the thickened multimodal data/memory/skill/production workflow produce? |
| `bad_aesthetic_memory` | commercial case, multimodal database, visual learning targets, visual target components, video demo beat map, motion learning targets, presentation sequence components, production reference decompositions, source cards, video cards, evidence memory, asset memory, narrative spine, Run 2.0 skill, and `bad_aesthetic_memory_replacement.json` | the good `aesthetic_memory.json`, good `aesthetic_memory_v2.json`, good `visual_production_modules.json`, and good `slide_archetypes.json` | Does bad aesthetic memory degrade an otherwise valid multimodal, motion, and production-reference workflow? |

Each arm must write a local `trace_manifest.json` under `outputs/` before scoring. The manifest must prove runtime isolation, native PPT object counts, raster-image limits, layout geometry checks, and release-gate status.
