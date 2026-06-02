# Results

Status: rerun-reviewed-public-blocked.

Local pilot arms from Run 2.0 through Run 2.8 were generated under `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/`:

- `ppt-run2-prompt-only`
- `ppt-run2-run1-5-skill`
- `ppt-run2-full-vulca`
- `ppt-run2-bad-aesthetic-memory`
- `ppt-run2-1-prompt-only`
- `ppt-run2-1-run1-5-skill`
- `ppt-run2-1-full-vulca`
- `ppt-run2-1-bad-aesthetic-memory`
- `ppt-run2-2-prompt-only`
- `ppt-run2-2-run1-5-skill`
- `ppt-run2-2-full-vulca`
- `ppt-run2-2-bad-aesthetic-memory`
- `ppt-run2-3-prompt-only`
- `ppt-run2-3-run1-5-skill`
- `ppt-run2-3-full-vulca`
- `ppt-run2-3-bad-aesthetic-memory`
- `ppt-run2-4-prompt-only`
- `ppt-run2-4-run1-5-skill`
- `ppt-run2-4-full-vulca`
- `ppt-run2-4-bad-aesthetic-memory`
- `ppt-run2-5-prompt-only`
- `ppt-run2-5-run1-5-skill`
- `ppt-run2-5-full-vulca`
- `ppt-run2-5-bad-aesthetic-memory`
- `ppt-run2-6-prompt-only`
- `ppt-run2-6-run1-5-skill`
- `ppt-run2-6-full-vulca`
- `ppt-run2-6-bad-aesthetic-memory`
- `ppt-run2-6r-prompt-only`
- `ppt-run2-6r-run1-5-skill`
- `ppt-run2-6r-full-vulca`
- `ppt-run2-6r-bad-aesthetic-memory`
- `ppt-run2-7-prompt-only`
- `ppt-run2-7-run1-5-skill`
- `ppt-run2-7-full-vulca`
- `ppt-run2-7-bad-workflow-memory`
- `ppt-run2-8-prompt-only`
- `ppt-run2-8-run1-5-skill`
- `ppt-run2-8-full-vulca`
- `ppt-run2-8-bad-memory-schema`

Generated decks, contact sheets, previews, trace manifests, layout JSON, and delivery reports remain local under `outputs/` unless the user explicitly approves release packaging.

The latest data/workflow repair is Run 2.9. It does not generate a new PPT yet; it repairs the data layer after the Run 2.8 visual diagnosis that the output still reads as boxes, cards, equal panels, and engineering-report composition. Run 2.9 adds `run2_9_visual_primitive_repair.json`, `run2_9_executable_visual_modules.json`, and `run2_9_visual_gate_matrix.json`, then exposes them in the HTML viewer `Data / Skill` tab. The next step is a four-arm generator rerun that actually calls the `drawRun29...` modules.

The latest reviewed generated internal result remains Run 2.8, a same-stage executable-design-memory pass after Run 2.7 data/workflow thickening. `run2_8_full_skill` is now the best internal arm for proving the product loop because `run2_8_tutorial_decomposition.json`, `run2_8_executable_design_memory.json`, and `run2_8_workflow_gate_matrix.json` route into code-generated native PPT, and the trace records actual native module calls rather than inferred memory membership. The required comparison images are `run2-8-four-arm-contact-sheet` and `run2-full-skill-series-horizontal`. The result remains public blocked pending native render inspection, source-brand sanitization review, and human approval.

`audit_review.md` is the prior release audit. `run2_1_readiness.md` records the Run 2.1 rerun result. `run2_2_rerun_result.md` records the Run 2.2 rerun result. `run2_3_rerun_result.md` records the Run 2.3 native-component rerun result. `run2_4_rerun_result.md` records the Run 2.4 motion-sequence rerun result. `run2_5_rerun_result.md` records the Run 2.5 production-design rerun result. `run2_6_rerun_result.md` records the Run 2.6 data/workflow-policy rerun result. `run2_6r_visual_repair_result.md` records the Run 2.6R same-stage visual repair result. `run2_7_data_workflow_thickening_result.md` records the Run 2.7 same-stage data/workflow thickening result. `run2_8_executable_design_memory_result.md` records the Run 2.8 executable-design-memory rerun result. `run2_9_visual_primitive_repair_result.md` records the Run 2.9 visual primitive data repair. `run2_8_visual_qa_gate.json` records the current visual public-blocking gate. Public publishing remains blocked because native or cross-platform render inspection, human approval, finished motion/render support, source-brand sanitization approval, and a public-demo-grade visual pass are still missing.
