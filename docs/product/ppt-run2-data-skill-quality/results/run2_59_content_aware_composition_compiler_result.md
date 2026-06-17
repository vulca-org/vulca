# Run 2.59 Content-Aware Composition Compiler

## Status
data/workflow-only; public blocked

## Why This Exists
Run 2.58 made product content visible, but it still let content thickness and layout module memory drift apart. The result was readable but report-like: repeated cards, title collisions, and too much trace/QA material on the public slide.

Run 2.59 fixes that failure mode by adding a content-aware composition compiler before any new PPT generation.

## Output Chain
- `run2_59_content_composition_contracts.json`
- `run2_59_layout_capacity_model.json`
- `run2_59_content_to_layout_selector.json`
- `run2_59_public_surface_trace_policy.json`
- `run2_59_composition_workflow_gates.json`

## What Changes
- Public slide content is split from trace/viewer detail.
- Run 2.15 layout modules get explicit capacity limits.
- Run 2.57 message contracts become public claims, proof objects, evidence chips, trace-only details, and speaker notes.
- Run 2.60 must choose a layout module from content burden and capacity, not only from slide role.
- The public slide / trace viewer split becomes an explicit workflow policy.

## Boundary
Run 2.59 does not generate a new PPT deck. The latest generated run remains Run 2.58 until Run 2.60 exists.

Do not advance to Run 3.0.

## Next Required Action
Run 2.60 must generate a four-arm PPT rerun that consumes Run 2.59 before native PPT drawing: `run2_60_generate_four_arm_ppt_consuming_run2_59_composition_compiler`.
