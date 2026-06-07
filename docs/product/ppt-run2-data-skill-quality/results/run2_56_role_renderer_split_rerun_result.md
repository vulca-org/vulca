# Run 2.56 Role Renderer Split Rerun

Status: four-arm rerun completed, public blocked.

Run 2.56 consumes Run 2.55 before native PPT redraw. The full arm keeps the Run 2.55 text-shape pass, then redraws the public surface with role-specific renderer modules and layout signatures.

This fixes the visible renderer bug: Run 2.55 proved text and shape binding, but the page could still read as one repeated stage-side template. Run 2.56 records six unique role renderer ids, six unique layout signatures, visual sameness bucket, anchor region, role-specific geometry count, text collision risk, overflow risk, and archetype binding status in trace.

## Arms

- `prompt_only`
- `run1_5_skill`
- `run2_56_full_role_renderer_split`
- `bad_run2_55_reused_single_template`

## Result

Best internal arm: `run2_56_full_role_renderer_split`.

Quality delta: `role_specific_renderer_variation_and_layout_qa`. All six full-arm slides have six unique role renderer ids, six unique layout signatures, pass archetype binding, no text collision risk, and no text overflow risk.

The negative control `bad_run2_55_reused_single_template` can reuse the Run 2.55 generated result, but it fails role-renderer split and keeps the reused Run 2.55 stage-side template signature.

Public release remains blocked. This proves measurable role-renderer variation, not final public-video-grade aesthetics.

## Required Images

- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-56-four-arm-contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

Do not advance to Run 3.0.
