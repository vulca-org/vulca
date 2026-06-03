# Results

Status: data-workflow-audited-public-blocked.

## Latest Result: Run 2.11

Run 2.11 is a data/workflow audit pass, not a new PPT rerun. It adds `run2_11_data_workflow_audit.json` and `run2_11_data_workflow_audit.md`, then shows the audit in the HTML viewer's `Data/Workflow Audit` tab.

Current gate: `weak_pass_internal_only_public_blocked`. The audit proves trace-grounded chains for Runs 2.8, 2.9, and 2.10, but it also records that the multimodal tutorial/video database is still too compact for the next visual rerun to claim stronger learning quality.

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

Generated decks, contact sheets, previews, trace manifests, layout JSON, and delivery reports remain local under `outputs/` unless the user explicitly approves release packaging.

The latest generated internal result is still Run 2.10, a same-stage visual-system rerun after the Run 2.9 full-series diagnosis that Runs 2.7-2.9 still shared a similar rectangle-led visual family. Run 2.11 does not create new PPTX artifacts; it audits whether the data/workflow chain behind Runs 2.8, 2.9, and 2.10 is trace-grounded enough to justify the next rerun.

Run 2.10 uses `run2_10_visual_system_sources.json`, `run2_10_visual_system_memory.json`, and `run2_10_visual_system_gate_matrix.json`, then calls the `drawRun210...` native visual-system modules in `ppt-run2-10-full-vulca`. The required comparison images are `run2-10-four-arm-contact-sheet` and `run2-full-skill-series-horizontal`.

`run2_10_full_skill` is now the best internal arm for proving the product loop because the trace records actual visual-system module calls (`drawRun210EditorialTypeSystem`, `drawRun210FullBleedVisualField`, `drawRun210ProductTheater`, `drawRun210NonRectangularProofPath`, `drawRun210KineticSequence`, and `drawRun210CinematicClimax`) rather than only recording memory membership. The result remains public blocked pending native render inspection, source-brand sanitization review, Gemini and human visual review, motion/render support, and human approval.

`audit_review.md` is the prior release audit. `run2_1_readiness.md` records the Run 2.1 rerun result. `run2_2_rerun_result.md` records the Run 2.2 rerun result. `run2_3_rerun_result.md` records the Run 2.3 native-component rerun result. `run2_4_rerun_result.md` records the Run 2.4 motion-sequence rerun result. `run2_5_rerun_result.md` records the Run 2.5 production-design rerun result. `run2_6_rerun_result.md` records the Run 2.6 data/workflow-policy rerun result. `run2_6r_visual_repair_result.md` records the Run 2.6R same-stage visual repair result. `run2_7_data_workflow_thickening_result.md` records the Run 2.7 same-stage data/workflow thickening result. `run2_8_executable_design_memory_result.md` records the Run 2.8 executable-design-memory rerun result. `run2_9_visual_primitive_repair_result.md` records the Run 2.9 visual primitive data repair. `run2_9_visual_primitive_rerun_result.md` records the Run 2.9 visual-primitive generator rerun. `run2_10_visual_system_rerun_result.md` records the Run 2.10 visual-system generator rerun. `run2_11_data_workflow_audit.md` records the Run 2.11 data/workflow audit. `run2_8_visual_qa_gate.json` records the current visual public-blocking gate. Public publishing remains blocked because native or cross-platform render inspection, human approval, finished motion/render support, source-brand sanitization approval, and a public-demo-grade visual pass are still missing.
