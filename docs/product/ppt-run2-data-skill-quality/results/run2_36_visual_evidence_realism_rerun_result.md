# Run 2.36 Visual Evidence Realism Rerun Result

Status: rerun completed, public blocked.

Run 2.36 is the generated four-arm rerun that consumes the Run 2.35 visual evidence realism workflow before native PPT code generation. The full arm reads Run 2.35 realism memory, editorial composition memory, and workflow gates; the negative control receives only the usecase label. It repeats the same five layers and does not advance to Run 3.0.

The generator is `scripts/generate_ppt_run2_36_visual_evidence_realism_arms.mjs`.

## Arms

- `prompt_only`
- `run1_5_skill`
- `run2_36_full_visual_evidence_realism`
- `bad_visual_evidence_realism_memory`

The negative control `bad_visual_evidence_realism_memory` may receive the selected usecase label, but it is blocked from reading the Run 2.35 realism memory, editorial composition memory, workflow gates, Run 2.34 audit, and Run 2.33 rerun result.

## Result

Best internal arm: `run2_36_full_visual_evidence_realism`.

Verdict: `usecase_specific_visual_evidence_asset_realism_and_editorial_composition_consumed_before_native_ppt_generation`.

Quality delta: `usecase_specific_visual_evidence_asset_realism_and_editorial_composition`. The full arm adds `drawRun236RealisticProductState`, `drawRun236EditorialAnchorObject`, and `drawRun236RealismGateRibbon` so each slide binds Run 2.35 realism ids, composition ids, and gate ids before native drawing.

Public release remains blocked. This proves Run 2.35 workflow consumption, not final public-video-grade visual quality or high-aesthetic human approval.

Remaining public release gates: human visual review, native or cross-platform render inspection, motion/video review, source-boundary review, and human release approval.

## Required Images

- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-36-four-arm-contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

Do not advance to Run 3.0.
