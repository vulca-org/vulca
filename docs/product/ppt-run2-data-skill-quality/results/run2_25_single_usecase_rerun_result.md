# Run 2.25 Single-Usecase Rerun Result

Status: rerun completed, public blocked.

Run 2.25 is the generated four-arm rerun that consumes Run 2.24 single-usecase content memory, visual evidence asset memory, and content/visual workflow gates before native PPT code generation. It repeats the same five layers and does not advance to Run 3.0.

The generator is `scripts/generate_ppt_run2_25_single_usecase_arms.mjs`.

## Arms

- `prompt_only`
- `run1_5_skill`
- `run2_25_full_single_usecase_content_visual`
- `bad_content_visual_memory`

The negative control `bad_content_visual_memory` may receive the selected usecase label, but it is blocked from reading Run 2.24 content memory, visual evidence assets, and workflow gates.

## Result

Best internal arm: `run2_25_full_single_usecase_content_visual`.

Verdict: `run2_24_pack_executed_before_native_ppt_generation`.

Public release remains blocked. This proves single-usecase content/visual pack execution, not final public-video-grade visual quality.

Remaining public release gates: human visual review, native or cross-platform render inspection, motion/video review, source-boundary review, and human release approval.

## Required Images

- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-25-four-arm-contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

Do not advance to Run 3.0.
