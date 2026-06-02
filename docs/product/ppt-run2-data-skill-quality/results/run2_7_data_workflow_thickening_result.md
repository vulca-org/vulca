# Run 2.7 Data Workflow Thickening Result

Status: rerun_completed_public_blocked.

Run 2.7 reran the same four-arm experiment as a same-stage data/workflow thickening pass, not as Run 3.0:

- `prompt_only`
- `run1_5_skill`
- `run2_7_full_skill`
- `bad_workflow_memory`

The purpose was to make the full product loop visible in generated native PPT:

`real commercial usecase -> multimodal tutorial/case database -> design memory -> skill workflow -> code-generated native PPT`.

The full arm uses `run2_7_commercial_usecase.json`, `run2_7_multimodal_source_records.json`, `run2_7_design_memory.json`, and `run2_7_workflow_policy.json`. The visible output now includes source-record routing, workflow gates, design-memory traces, and a native editable proof object. The controls preserve their boundaries: prompt-only only receives the commercial case, Run 1.5 only receives the prior product-lab context, and bad-workflow receives valid data plus the negative-control replacement memory while forbidding good Run 2.7 design/workflow memory.

Two mandatory images were generated locally:

- Four-arm sheet: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-7-four-arm-contact-sheet.png`
- Full-skill-series sheet: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

Gemini artifact reviews at `.gemini-agent/artifacts/2026-06-02T025308959Z-artifacts.json` and `.gemini-agent/artifacts/2026-06-02T025321445Z-artifacts.json` judged Run 2.7 full stronger on hierarchy, contrast, source-record routing, workflow gates, and editable proof-object composition. The same reviews keep the result public blocked because small text is hard to inspect at contact-sheet scale, Run 2.5/2.6 differences are still subtle in the series view, the exact design-memory schema needs clearer evidence, and palette differences may bias the comparison.

## QA Summary

- Layout QA reported six files, zero errors, and zero warnings for all four Run 2.7 arms.
- Delivery QA returned `internal-demo-ok-public-blocked` for all four arms.
- Arm isolation guard passed.
- Native guard reported zero media entries and zero picture shapes for all four arms.
- Native shape counts: prompt-only 200, Run 1.5 200, Run 2.7 full 260, bad-workflow 216.
- Generated outputs remain untracked and are not committed.

## Decision

Run 2.7 is the current best internal proof that data and workflow can affect code-generated native PPT, but it is not a final product output and not a public-video-ready presentation.

The next pass should continue the same five layers: make the real usecase sharper, thicken multimodal/video tutorial decomposition, make design memory more specific, enforce workflow gates more strictly, and improve editorial typography, spacing, and climax composition before rerunning the same four arms.

Do not advance to Run 3.0.
