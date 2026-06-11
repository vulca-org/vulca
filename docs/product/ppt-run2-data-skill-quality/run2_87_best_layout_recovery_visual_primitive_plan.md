# Run 2.87 Best Layout Recovery

Part R is a plan-only bridge from Q to the next renderer rerun. It does not generate PPT, HTML, or public release output.

## Verdict

- Status: `run2_87_best_layout_recovery_visual_primitive_plan_ready_public_blocked`
- Strategy: historical best layout recovery before new visual primitive drawing.
- Boundary: public blocked; visual quality verdict deferred to the rerun evaluation.

## Page Recovery

- Slide 1 `cover`: editorial product-theater hero from Run 2.10/2.67 with one dominant product surface -> `primitive_2_87_product_theater_surface`
- Slide 2 `setup`: text-heavy editorial field plus anchored operating-loop stage from Run 2.16/2.68 -> `primitive_2_87_editorial_text_field`
- Slide 3 `contrast`: before/after theater from Run 2.16/2.67 with enlarged after-state product surface -> `primitive_2_87_before_after_surface`
- Slide 4 `proof`: inspectable modular evidence workspace from Run 2.10/2.68 with unequal matrix hierarchy -> `primitive_2_87_modular_matrix_workspace`
- Slide 5 `climax`: cinematic climax stage plus overlay sticker stack from Run 2.9/2.10/2.67 -> `primitive_2_87_overlay_sticker_stack`
- Slide 6 `close`: release decision board from Run 2.16/2.68 with fewer nodes and a larger verdict branch -> `primitive_2_87_decision_map_board`

## Visual Primitive Contracts

- `primitive_2_87_product_theater_surface` uses `drawRun287ProductTheaterSurface`.
- `primitive_2_87_editorial_text_field` uses `drawRun287EditorialTextField`.
- `primitive_2_87_before_after_surface` uses `drawRun287BeforeAfterSurface`.
- `primitive_2_87_modular_matrix_workspace` uses `drawRun287ModularMatrixWorkspace`.
- `primitive_2_87_overlay_sticker_stack` uses `drawRun287OverlayStickerStack`.
- `primitive_2_87_decision_map_board` uses `drawRun287DecisionMapBoard`.

## Next

Run 2.88 must consume Part R and produce four arms, including a bad arm without best-layout visual primitives.

Next required action: `part_s_renderer_rerun_from_run2_87_best_layout_visual_primitive_plan`.
