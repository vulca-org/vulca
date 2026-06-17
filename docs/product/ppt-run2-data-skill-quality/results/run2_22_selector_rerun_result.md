# Run 2.22 Selector Rerun Result

Status: rerun completed, public blocked.

Run 2.22 is the generated four-arm rerun that consumes Run 2.21 visual-decision memory, per-role selector gates, and the evidence rejection matrix before native PPT code generation. It repeats the same five layers and does not advance to Run 3.0.

The generator is `scripts/generate_ppt_run2_22_selector_memory_arms.mjs`.

## Arms

- `prompt_only`
- `run1_5_skill`
- `run2_22_full_selector_memory`
- `bad_selector_memory`

The negative control `bad_selector_memory` may read Run 2.21 visual-decision memory, but it is blocked from reading selector gates and the rejection matrix.

## Result

Best internal arm: `run2_22_full_selector_memory`.

Verdict: `selector_memory_executed_before_native_ppt_generation`.

Public release remains blocked. This proves selector-memory execution, not final public-video-grade visual quality.

Remaining public release gates: human visual review, native or cross-platform render inspection, motion/video review, source-boundary review, and human release approval.

## Required Images

- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-22-four-arm-contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

Do not advance to Run 3.0.
