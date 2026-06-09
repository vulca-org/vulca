# Run 2.72 Shape-Bound Text Rerun

Status: four-arm rerun completed, public blocked.

Run 2.72 consumes Run 2.71 component semantics plus Run 2.66 design grammar before native PPT drawing, then records component bbox and text bbox geometry for component-level labels.

## Arms

- `prompt_only`
- `run1_5_skill`
- `run2_72_full_shape_bound_text`
- `bad_run2_72_without_shape_bound_text`

## Result

Best internal arm: `run2_72_full_shape_bound_text`.

Quality delta: `run2_72_shape_bound_text_geometry`. The full arm must expose component bbox, text bbox, and an inside the component bounds pass for the target slides.

The bad control can reuse Run 2.71 component semantics, but it fails the Run 2.72 shape-bound text geometry layer.

Bug notes: target slides 03, 04, and 05 now record text bbox geometry against the component bbox before drawing.

Component notes: component manifest, text-to-component binding, component bbox, text bbox, containment status, and non-rectangular primitives are all trace-visible.

Public release remains blocked pending visual review.

## Required Images

- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-72-four-arm-contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

Do not advance to Run 3.0.
