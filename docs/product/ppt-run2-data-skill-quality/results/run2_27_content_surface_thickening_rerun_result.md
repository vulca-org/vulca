# Run 2.27 Content Surface Thickening Rerun Result

Status: rerun completed, public blocked.

Run 2.27 is the generated four-arm rerun that consumes Run 2.24 single-usecase content memory, visual evidence asset memory, content/visual workflow gates, and the Run 2.26 visual module quality audit before native PPT code generation. It repeats the same five layers and does not advance to Run 3.0.

The generator is `scripts/generate_ppt_run2_27_content_surface_thickening_arms.mjs`.

## Arms

- `prompt_only`
- `run1_5_skill`
- `run2_27_full_content_surface_thickening`
- `bad_surface_thickening_memory`

The negative control `bad_surface_thickening_memory` may receive the selected usecase label, but it is blocked from reading Run 2.24 content memory, visual evidence assets, workflow gates, and the Run 2.26 visual module quality audit.

## Result

Best internal arm: `run2_27_full_content_surface_thickening`.

Verdict: `run2_26_audit_target_executed_before_native_ppt_generation`.

Quality delta: `drawRun225ContentEvidenceSurface` is replaced by `drawRun227ContentEvidenceSurface`; setup, contrast, and close now require three visible proof rows without compressed proof-surface carryover.

Public release remains blocked. This proves content surface thickening pack execution, not final public-video-grade visual quality or high-aesthetic human approval.

Remaining public release gates: human visual review, native or cross-platform render inspection, motion/video review, source-boundary review, and human release approval.

## Required Images

- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-27-four-arm-contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

Do not advance to Run 3.0.
