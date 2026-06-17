# Run 2.5 Rerun Result

Status: rerun_completed_public_blocked.

Run 2.5 reran the same four arms after adding production-design data and modules:

- `prompt_only`
- `run1_5_skill`
- `run2_5_full_skill`
- `bad_aesthetic_memory`

The useful result is narrower and stronger than Run 2.4: `run2_5_full_skill` now shows that production-design data can affect the generated deck, not only the trace. It consumes `production_reference_decompositions.json`, `aesthetic_memory_v2.json`, and `visual_production_modules.json`, then renders visible native modules: a cinematic cover field, product mini-preview, editorial before/after delta, proof route, climax hero object, and release handoff.

The control boundary also held. `prompt_only` and `run1_5_skill` record empty production-reference, aesthetic-v2, and visual-module fields. `bad_aesthetic_memory` receives production references but does not receive the good `aesthetic_memory_v2.json` or `visual_production_modules.json`, so it remains a negative control rather than a second full-product arm.

This is stronger than Run 2.4. Run 2.4 proved that video/tutorial-derived rhythm can sequence a deck. Run 2.5 proves that decomposed production references and code-generation modules can change the visual construction of the generated PPT.

The limitation remains important: this is still public blocked. Gemini contact-sheet review judged the full arm a clear move away from the engineering-report look, but also flagged theme generalization, older PPT rendering risk, and aesthetic-memory drift. Native render inspection and human approval have not passed.

## QA Summary

- Four arms generated locally under `outputs/`.
- Delivery QA returned `internal-demo-ok-public-blocked` for all four arms.
- Layout QA reported zero errors and zero warnings for all four Run 2.5 arms.
- Trace manifests were refreshed after delivery/layout QA.
- The `run2_5_full_skill` trace records `production_reference_ids`, `aesthetic_memory_v2_ids`, `visual_production_module_ids`, `fallback_policy`, and `visual_validation_probe`.
- Gemini reviewed the four-arm contact sheet and judged the full arm visibly stronger than the controls while still not public-release proof.
- Generated outputs remain untracked and are not committed.

## Decision

Run 2.5 proves that the tutorial/case database has started to become an executable production-design workflow. It does not prove final public aesthetic quality.

## Next Required Action

Do not advance to Run 3.0.

The next pass should first run native render and human review on Run 2.5. If those fail, repeat the same five-layer loop again and thicken:

- typography system and spacing precision;
- public-grade climax editorial composition;
- high-fidelity native mini-previews;
- theme selection for dark and light commercial contexts;
- motion/render support that survives PowerPoint, Keynote, and Google Slides inspection.
