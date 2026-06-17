# Run 2.47 Composition Grammar Rerun

Status: four-arm rerun completed, public blocked.

Run 2.47 consumes Run 2.46 before native PPT drawing. The full arm binds visual object grammar, multimodal composition decomposition, and composition workflow gates, then replaces Run 2.44 slot-based geometry with composed object scenes.

This fixes the next suspected workflow bug: the generator must not merely carry Run 2.46 files as notes. The generated full arm carries `run2_46_visual_object_grammar_id`, `run2_46_multimodal_composition_decomposition_id`, `run2_46_composition_gate_id`, and `run2_46_slot_based_geometry_replaced` in trace.

## Arms

- `prompt_only`
- `run1_5_skill`
- `run2_47_full_composition_grammar_compiler`
- `bad_run2_46_missing_composition_grammar`

## Result

Best internal arm: `run2_47_full_composition_grammar_compiler`.

Quality delta: `composition_grammar_binding`. All six full-arm slides contain Run 2.46 visual object grammar ids and mark slot-based geometry replaced.

The negative control `bad_run2_46_missing_composition_grammar` can reuse Run 2.44 geometry slots, but it has no Run 2.46 visual object grammar id, no decomposition id, and no composition gate id.

Public release remains blocked. This proves composition grammar consumption, not final public-video-grade aesthetics.

## Required Images

- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-47-four-arm-contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

Do not advance to Run 3.0.
