# Run 2.65 Renderer Composition Rerun

Status: four-arm rerun completed, public blocked.

Run 2.65 consumes Run 2.64 before native PPT drawing. The full arm binds dynamic socket, semantic diagram, text-fit, and dry-run renderer contracts on every slide.

## Arms

- `prompt_only`
- `run1_5_skill`
- `run2_65_full_renderer_composition_repair`
- `bad_run2_64_without_renderer_composition_repair`

## Result

Best internal arm: `run2_65_full_renderer_composition_repair`.

Quality delta: `run2_64_renderer_composition_repair_consumed`. Full-arm slides consume dynamic socket, semantic diagram, text-fit, and dry-run binding records.

The negative control `bad_run2_64_without_renderer_composition_repair` can reuse Run 2.62 generated proof, but it fails the Run 2.64 renderer composition repair layer.

Public release remains blocked pending visual review.

## Required Images

- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-65-four-arm-contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

Do not advance to Run 3.0.
