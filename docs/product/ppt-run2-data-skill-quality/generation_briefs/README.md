# Generation Briefs

Status: not-run.

Run 2.0 compares four arms: `prompt_only`, `run1_5_skill`, `run2_skill`, and `bad_aesthetic_memory`.

Each arm must use the same commercial case and six-slide target unless the arm definition explicitly excludes a data layer. Generated decks, previews, contact sheets, and layout JSON remain local under `outputs/`.

## Arm Isolation Matrix

| Arm | Allowed inputs | Forbidden inputs | Attribution question |
| --- | --- | --- | --- |
| `prompt_only` | `commercial_case.md` only | source cards, video cards, evidence memory, aesthetic memory, asset memory, narrative spine, slide archetypes, Run 1.5 skill, Run 2.0 skill | What does the commercial brief alone produce? |
| `run1_5_skill` | `commercial_case.md` plus prior Run 1.5 product-lab workflow files | Run 2.0 source cards, video cards, evidence memory, aesthetic memory, asset memory, narrative spine, slide archetypes, Run 2.0 skill | What does the prior evidence-heavy workflow produce without the new aesthetic layer? |
| `run2_skill` | full Run 2.0 package and staged deck-director skill | copied source visuals, unapproved release assets, post-training or fine-tuning claims | What does the thickened data/memory/skill workflow produce? |
| `bad_aesthetic_memory` | commercial case, source cards, video cards, evidence memory, asset memory, narrative spine, Run 2.0 skill, and `bad_aesthetic_memory_replacement.json` | the good `aesthetic_memory.json` and good `slide_archetypes.json` | Does bad aesthetic memory degrade an otherwise valid workflow? |

Each arm must write a local `trace_manifest.json` under `outputs/` before scoring.
