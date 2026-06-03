# PPT Run 2.15 Layout Selector Design

Status: draft-for-user-review.

## Context

Run 2.14 is the latest internal generated PPT result. It corrected the Run 2.13 regression by restoring the Run 2.10 visual-system aesthetic shell while keeping Run 2.13 thick data/workflow trace in manifest/viewer/QA.

That is real progress, but it is still not a product-grade capability. The stronger Run 2.14 slides are still too dependent on handpicked composition code. The system does not yet prove that it can select a layout module from content, slide role, text length, product-demo need, and trace visibility policy.

The current product loop remains:

`real commercial usecase -> multimodal tutorial/case database -> design memory -> skill workflow -> code-generated native PPT -> baseline/ablation/evaluation`

Run 2.15 stays inside the same loop. It does not advance to Run 3.0 and does not claim public readiness.

## Goal

Run 2.15 should turn the Run 2.14 aesthetic recovery into a reusable data/workflow layer before the next PPT generation pass.

The target is not "make 2.14 prettier." The target is to define and validate the selector logic that decides which editorial/native PPT module should be used for each slide role, while keeping workflow proof out of the public slide surface.

## Options Considered

### Option A: Directly Tune The Run 2.14 Generator

This would edit `scripts/generate_ppt_run2_14_aesthetic_trace_arms.mjs` to improve spacing, text size, product blocks, and climax composition.

Trade-off: it may create a better screenshot quickly, but it would not prove product learning. It risks another pass where the slide looks different because the code was manually styled.

### Option B: Add More Tutorial/Video Records First

This would expand the multimodal database before any new workflow layer.

Trade-off: useful, but source count alone is not the weakness. The current weak point is that observations do not yet become a robust module-selection workflow.

### Option C: Build A Layout Module Selector Layer First

This creates a Run 2.15 source pack, executable layout-module memory, and selector gate matrix. It defines how slide role, content burden, visual intent, trace policy, and product-demo need select native PPT composition modules.

This is the recommended path because it thickens the product mechanism before the next visual rerun.

## Chosen Design

Run 2.15 is a same-stage layout-selector data/workflow pass. It should not generate a new PPT deck yet.

It should create three new core artifacts:

- `docs/product/ppt-run2-data-skill-quality/run2_15_layout_selector_sources.json`
- `docs/product/ppt-run2-data-skill-quality/run2_15_layout_module_memory.json`
- `docs/product/ppt-run2-data-skill-quality/run2_15_layout_selector_gate_matrix.json`

It should also create result documentation:

- `docs/product/ppt-run2-data-skill-quality/results/run2_15_layout_selector_result.json`
- `docs/product/ppt-run2-data-skill-quality/results/run2_15_layout_selector_result.md`

The next generation pass after this will be Run 2.16 or a Run 2.15 rerun, depending on whether the selector artifacts pass review. The important boundary is that this pass creates the selector data/workflow layer, not the PPT output.

## Layout Selector Source Layer

The source layer should convert existing Run 2.10, Run 2.12, Run 2.13, and Run 2.14 learning into selector-oriented derived observations.

Each source record should include:

- `record_id`
- `source_family`
- `derived_from_run_ids`
- `modality_mix`
- `commercial_need`
- `design_observation`
- `layout_selector_obligation`
- `typography_obligation`
- `spacing_obligation`
- `product_theater_obligation`
- `motion_beat_obligation`
- `trace_visibility_obligation`
- `anti_copy_boundary`

The source records should be derived observations only. They must not copy screenshots, source layouts, logos, raw frames, transcripts, or brand-specific media.

## Layout Module Memory

The memory layer should define reusable native-PPT module candidates. Each memory record should be specific enough that a generator can decide when to use it.

Each memory record should include:

- `module_id`
- `module_family`
- `slide_roles`
- `source_record_ids`
- `selection_trigger`
- `composition_contract`
- `typography_contract`
- `spacing_contract`
- `asset_contract`
- `trace_visibility_contract`
- `fallback_contract`
- `native_ppt_obligations`
- `forbidden_patterns`

Initial module families:

- `editorial_cover_field`
- `product_theater_stage`
- `before_after_route`
- `metric_reveal_stage`
- `quiet_release_handoff`
- `dense_evidence_compression`

These are not final visual templates. They are selector targets that the next generator must bind to actual native PPT code modules.

## Selector Gate Matrix

The gate matrix should decide which module family is allowed for each slide role before generation.

Each gate record should include:

- `gate_id`
- `slide_role`
- `candidate_module_ids`
- `required_selector_inputs`
- `selection_rules`
- `rejection_rules`
- `trace_fields`
- `layout_budget`
- `text_resilience_probe`
- `product_surface_probe`
- `bad_control_probe`

Required gates:

- `gate_2_15_role_to_module_selection`
- `gate_2_15_text_resilience`
- `gate_2_15_trace_hidden_from_surface`
- `gate_2_15_product_theater_realism`
- `gate_2_15_bad_selector_control_boundary`

## Workflow Contract

Run 2.15 must enforce this order:

1. Select slide role.
2. Estimate text/content burden.
3. Decide whether the slide needs product theater, before/after, metric reveal, or quiet handoff.
4. Select layout module memory ids.
5. Apply typography and spacing constraints.
6. Decide trace visibility: manifest/viewer only unless the slide is an internal diagnostic.
7. Record selection evidence for the next generator.

The future full arm must be able to prove:

- selected source record ids;
- selected module memory ids;
- selected gate ids;
- actual native code module ids;
- text resilience result;
- trace visibility result;
- bad-control boundary.

## Viewer And Reporting

The HTML viewer should expose Run 2.15 as a data/workflow layer in the Data / Skill area. It should not pretend a new PPT deck exists.

Result docs should state:

- what selector artifacts were added;
- which prior runs they learn from;
- why this pass does not generate PPT;
- what exact gate must pass before the next rerun;
- why public release remains blocked.

## QA

Required checks:

- Focused tests for the three Run 2.15 artifacts.
- Tests that source records include anti-copy boundaries and selector obligations.
- Tests that every memory record maps to source records and slide roles.
- Tests that every selector gate maps to candidate memory modules and required trace fields.
- Tests that `skill_workflow.json`, result docs, and viewer references point to Run 2.15 as a data/workflow pass.
- Case-pack validator with `--profile run2`.
- `git diff --check`.

## Non-Goals

- Do not generate a new PPT deck in this pass.
- Do not advance to Run 3.0.
- Do not claim public readiness.
- Do not copy source screenshots, source layouts, logos, video frames, audio, long prose, or full transcripts.
- Do not satisfy the pass by adding more files without selector obligations.
- Do not make workflow proof visible on public slides.
- Do not weaken the Run 2.14 trace truthfulness boundary.

## Success Criteria

Run 2.15 is successful if:

1. The selector source, memory, and gate artifacts exist and validate.
2. The artifacts explain how Run 2.14 should become reusable rather than hardcoded.
3. The viewer and result docs make clear that Run 2.15 is data/workflow-only.
4. The next generation pass has concrete selector fields to trace and ablate.
5. Public release remains blocked unless render, source-brand, and human approval gates pass.
