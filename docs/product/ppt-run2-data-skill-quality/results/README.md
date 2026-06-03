# Results

Status: rerun-completed-public-blocked.

## Latest Result: Run 2.13

Run 2.13 is the latest generated PPT rerun. It uses the Run 2.12 thick evidence, design memory seeds, and workflow gate seeds in a new four-arm experiment, then updates the HTML viewer to latest `2.13`.

Current gate: `thick_data_memory_and_workflow_visible_but_not_public_release_ready`. Run 2.13 keeps the project public blocked because Gemini and local review still flag thumbnail-scale text/readability risk and no human release approval is recorded.

Local pilot arms from Run 2.0 through Run 2.10 were generated under `outputs/019e7d9c-532a-70b3-8892-fa3ae42baef2/presentations/`:

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
- `ppt-run2-9-prompt-only`
- `ppt-run2-9-run1-5-skill`
- `ppt-run2-9-full-vulca`
- `ppt-run2-9-bad-visual-primitive-memory`
- `ppt-run2-10-prompt-only`
- `ppt-run2-10-run1-5-skill`
- `ppt-run2-10-full-vulca`
- `ppt-run2-10-bad-visual-system-memory`
- `ppt-run2-13-prompt-only`
- `ppt-run2-13-run1-5-skill`
- `ppt-run2-13-full-vulca`
- `ppt-run2-13-bad-thick-data-memory`

Generated decks, contact sheets, previews, trace manifests, layout JSON, and delivery reports remain local under `outputs/` unless the user explicitly approves release packaging.

The latest generated internal result is Run 2.13, a same-stage thick-data rerun after Run 2.12. Run 2.11 and Run 2.12 do not create new PPTX artifacts; they audit and thicken the data/workflow chain behind Run 2.13.

Run 2.13 uses `run2_12_thick_multimodal_evidence.json`, `run2_12_design_memory_seed.json`, and `run2_12_workflow_gate_seed.json`, then calls the `drawRun213...` native modules in `ppt-run2-13-full-vulca`. The required comparison images are `run2-13-four-arm-contact-sheet` and `run2-full-skill-series-horizontal`.

`run2_13_full_skill` is now the best internal arm for proving the product loop because the trace records actual thick-data module calls (`drawRun213LaunchArcRoute`, `drawRun213TypeWhitespaceSystem`, `drawRun213ProductDemoSequence`, `drawRun213MetricClimaxObject`, and `drawRun213WorkflowGateRail`) and the `bad_thick_data_memory` negative control is evidence-only. The result remains public blocked pending thumbnail-scale typography fixes, native render inspection, source-brand sanitization review, Gemini and human visual review, motion/render support, and human approval.

Run 2.10 remains the prior generated visual-system result. It uses `run2_10_visual_system_sources.json`, `run2_10_visual_system_memory.json`, and `run2_10_visual_system_gate_matrix.json`, then calls the `drawRun210...` native visual-system modules in `ppt-run2-10-full-vulca`. The required comparison images are `run2-10-four-arm-contact-sheet` and `run2-full-skill-series-horizontal`.

`audit_review.md` is the prior release audit. `run2_1_readiness.md` records the Run 2.1 rerun result. `run2_2_rerun_result.md` records the Run 2.2 rerun result. `run2_3_rerun_result.md` records the Run 2.3 native-component rerun result. `run2_4_rerun_result.md` records the Run 2.4 motion-sequence rerun result. `run2_5_rerun_result.md` records the Run 2.5 production-design rerun result. `run2_6_rerun_result.md` records the Run 2.6 data/workflow-policy rerun result. `run2_6r_visual_repair_result.md` records the Run 2.6R same-stage visual repair result. `run2_7_data_workflow_thickening_result.md` records the Run 2.7 same-stage data/workflow thickening result. `run2_8_executable_design_memory_result.md` records the Run 2.8 executable-design-memory rerun result. `run2_9_visual_primitive_repair_result.md` records the Run 2.9 visual primitive data repair. `run2_9_visual_primitive_rerun_result.md` records the Run 2.9 visual-primitive generator rerun. `run2_10_visual_system_rerun_result.md` records the Run 2.10 visual-system generator rerun. `run2_11_data_workflow_audit.md` records the Run 2.11 data/workflow audit. `run2_12_data_thickening_result.md` records the Run 2.12 data/workflow thickening pass. `run2_13_thick_data_rerun_result.md` records the Run 2.13 thick-data generator rerun. `run2_8_visual_qa_gate.json` records the current visual public-blocking gate. Public publishing remains blocked because native or cross-platform render inspection, human approval, finished motion/render support, source-brand sanitization approval, and a public-demo-grade visual pass are still missing.
