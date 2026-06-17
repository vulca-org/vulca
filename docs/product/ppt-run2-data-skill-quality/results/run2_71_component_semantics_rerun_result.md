# Run 2.71 Component Semantics Rerun

Status: four-arm rerun completed, public blocked.

Run 2.71 consumes Run 2.70 high-fidelity mock output plus Run 2.66 design grammar before native PPT drawing, then binds text into explicit product components instead of filling generic boxes.

## Arms

- `prompt_only`
- `run1_5_skill`
- `run2_71_full_component_semantics`
- `bad_run2_70_without_component_semantics`

## Result

Best internal arm: `run2_71_full_component_semantics`.

Quality delta: `run2_70_component_semantics_content_binding`. The full arm must expose a component manifest, text-to-component binding, and non-rectangular primitives for the target slides.

The bad control can reuse Run 2.70 mock surfaces, but it fails the Run 2.71 component semantics layer.

Bug notes: target slides 03, 04, and 05 now register semantic product components before drawing.

Component notes: component manifest, text-to-component binding, non-rectangular primitives, and weakness repair status are all trace-visible.

Public release remains blocked pending visual review.

## Required Images

- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-71-four-arm-contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

Do not advance to Run 3.0.
