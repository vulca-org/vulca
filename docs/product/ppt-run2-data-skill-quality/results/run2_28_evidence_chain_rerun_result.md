# Run 2.28 Evidence Chain Rerun Result

Status: rerun completed, public blocked.

Run 2.28 is the generated four-arm rerun that consumes Run 2.28 evidence chain data, Run 2.24 single-usecase content memory, visual evidence asset memory, content/visual workflow gates, and the Run 2.27 rerun result before native PPT code generation. It repeats the same five layers and does not advance to Run 3.0.

The generator is `scripts/generate_ppt_run2_28_evidence_chain_arms.mjs`.

## Arms

- `prompt_only`
- `run1_5_skill`
- `run2_28_full_evidence_chain`
- `bad_evidence_chain_memory`

The negative control `bad_evidence_chain_memory` may receive the selected usecase label, but it is blocked from reading Run 2.28 evidence chain data, Run 2.24 content memory, visual evidence assets, workflow gates, and the Run 2.27 rerun result.

## Result

Best internal arm: `run2_28_full_evidence_chain`.

Verdict: `source_rule_workflow_output_chain_rendered_before_native_ppt_generation`.

Evidence-chain delta: every full-arm slide now exposes `source evidence`, `extracted design rule`, `workflow decision`, and `generated slide surface` as traceable native PPT objects.

Public release remains blocked. This proves evidence-chain execution, not final public-video-grade visual quality or high-aesthetic human approval.

Remaining public release gates: human visual review, native or cross-platform render inspection, motion/video review, source-boundary review, and human release approval.

## Required Images

- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-28-four-arm-contact-sheet.png`
- `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

Do not advance to Run 3.0.
