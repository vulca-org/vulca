# Run 2.8 Executable Design Memory Result

Status: rerun_completed_public_blocked.

Run 2.8 reran the same four-arm experiment as a same-stage executable-memory pass, not as Run 3.0:

- `prompt_only`
- `run1_5_skill`
- `run2_8_full_skill`
- `bad_memory_schema`

The purpose was to make the product loop stricter:

`real commercial usecase -> multimodal tutorial/case database -> executable design memory -> workflow gate matrix -> code-generated native PPT`.

The full arm uses `run2_8_tutorial_decomposition.json`, `run2_8_executable_design_memory.json`, and `run2_8_workflow_gate_matrix.json`. The visible output now includes selected type/spacing modules, before-after delta modules, workflow gates, and a climax hero object. More importantly, the trace no longer infers code bindings from memory membership: `run2_8_code_binding_ids` is populated from actual native module calls recorded during rendering, then checked against each slide's required gate-matrix bindings.

Two mandatory images were generated locally:

- Four-arm sheet: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-8-four-arm-contact-sheet.png`
- Full-skill-series sheet: `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/run2-full-skill-series-horizontal.png`

Gemini artifact reviews at `.gemini-agent/artifacts/2026-06-02T043532104Z-artifacts.json` and `.gemini-agent/artifacts/2026-06-02T043547016Z-artifacts.json` judged Run 2.8 full stronger on hierarchy, cleaner layout, high-contrast hero-object emphasis, and data-to-memory-to-gate-to-native-PPT routing. The same reviews keep the result public blocked because contact-sheet scale makes small typography hard to inspect and native render/human approval gates are still incomplete.

## QA Summary

- Layout QA reported six files, zero errors, and zero warnings for all four Run 2.8 arms.
- Delivery QA returned `internal-demo-ok-public-blocked` for all four arms.
- Arm isolation guard passed.
- Trace truthfulness guard passed: all full-arm required code bindings were present in actual native module calls.
- Native guard reported zero media entries and zero picture shapes for all four arms.
- Native shape counts: prompt-only 200, Run 1.5 200, Run 2.8 full 266, bad-memory-schema 225.
- Generated outputs remain untracked and are not committed.

## Decision

Run 2.8 is the current best internal proof that tutorial decomposition and executable design memory can change code-generated native PPT while preserving trace truthfulness.

It is not a final public presentation. The next pass should continue the same five layers by making tutorial/video decomposition deeper, design memory more specific, workflow gates stricter, and typography/spacing/climax composition more public-video-grade.

Do not advance to Run 3.0.
