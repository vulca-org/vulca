# PPT Run 2.11 Data Workflow Audit Design

Status: draft-for-user-review.

## Context

Run 2.10 is the latest internal PPT run. It proved that the full arm can route visual-system data into native code-generated PPT and record actual module calls in trace. The four-arm review improved, but the full-skill series still looks too similar across Runs 2.7-2.10.

The next decision should not chase visual polish first. The more important question is whether the product has a strong enough data and workflow loop:

`real commercial usecase -> multimodal tutorial/case database -> design memory -> skill workflow -> code-generated native PPT -> baseline/ablation/evaluation`

Run 2.11 stays inside the same five product layers. It does not advance to Run 3.0 and does not claim public readiness.

## Goal

Run 2.11 should make the data and workflow progress inspectable. It should answer:

1. Which source observations exist?
2. Which observations became tutorial decompositions, memory records, gate rules, and code-module obligations?
3. Which obligations actually appeared in generated trace manifests?
4. Which links are only documented, weakly connected, missing, or proven by controls?
5. Whether the system is ready for another PPT rerun or needs more data/workflow thickening first.

The success target is evidence quality, not prettier slides.

## Options Considered

### Option A: Continue Visual Reruns

This would generate Run 2.11 as another four-arm visual pass immediately.

Trade-off: it may produce visible changes, but it would not answer whether the data and workflow layer is genuinely improving. It also risks adding another version where files increase but product proof remains unclear.

### Option B: Add More Source Data First

This would expand tutorial, video, and commercial case records before creating another viewer or audit gate.

Trade-off: more data is useful, but without an audit surface it remains hard to know which records are executable, which records are decorative, and which records actually affect generated output.

### Option C: Build A Data/Workflow Audit Pass First

This creates a Run 2.11 audit artifact, viewer tab, and validation tests before the next generation pass. It treats Runs 2.7-2.10 as evidence and checks the source-to-slide chain.

This is the recommended path. It directly supports the product thesis: Vulca should learn from real usecases and multimodal design material, then convert that learning into auditable skill workflow and code-generated PPT.

## Chosen Design

Run 2.11 is a same-stage data/workflow audit pass. It should not create a new deck first. It should create an audit board that explains and validates what has already been built from Runs 2.7-2.10.

The audit board should cover:

- source and tutorial records;
- tutorial/video decomposition units;
- design or visual-system memory records;
- workflow gate records;
- generator module obligations;
- actual trace fields from generated full arms and control arms;
- pass, weak, missing, or blocked outcomes;
- recommended next action.

## New Audit Artifact

Create:

- `docs/product/ppt-run2-data-skill-quality/results/run2_11_data_workflow_audit.json`

The artifact should be machine-readable and viewer-friendly.

Required top-level fields:

- `schema_version`
- `status`
- `stage_policy`
- `audit_scope`
- `source_inventory`
- `workflow_inventory`
- `chain_records`
- `arm_trace_evidence`
- `negative_control_checks`
- `gate_summary`
- `next_required_action`

Each `chain_records` item should describe one auditable chain:

- `chain_id`
- `run_id`
- `layer`
- `source_ids`
- `decomposition_ids`
- `memory_ids`
- `gate_ids`
- `required_code_module_ids`
- `actual_code_module_ids`
- `slide_roles`
- `trace_manifest_paths`
- `control_boundary`
- `status`: `pass`, `weak`, `missing`, or `blocked`
- `reason`
- `next_fix`

The audit must distinguish these states:

- `pass`: data, memory, gate, required module, actual trace evidence, and control isolation are all present.
- `weak`: the link exists but is too vague, too sparse, or not strong enough to prove learning quality.
- `missing`: an expected link does not exist.
- `blocked`: the link cannot be promoted because render review, source-brand sanitization, human approval, or public-demo gates are missing.

## Viewer Changes

Update the existing HTML viewer with a new tab:

- `Data/Workflow Audit`

The tab should show three compact sections:

1. `2.7-2.10 Progress`: a run-by-run inventory of data, memory, workflow, and trace evidence.
2. `Source-To-Slide Chains`: a table or chain board showing source -> decomposition -> memory -> gate -> module -> trace -> outcome.
3. `Gaps Before Next Rerun`: the weak/missing/blocked records and the next required action.

The viewer should keep the existing tabs:

- Four arms
- Full skill series
- Sheets
- Data / Skill

The viewer should not require generated Run 2.11 PPT images. Run 2.11 is an audit layer first.

## Workflow Gate Changes

The audit should add a gate concept without changing the product architecture:

`data_workflow_chain_gate`

This gate passes only if:

- every selected source has a derived observation and anti-copy boundary;
- every selected observation maps to a memory or decomposition record;
- every selected memory maps to a workflow gate;
- every workflow gate declares required code modules or generation obligations;
- the full arm trace records actual code modules when required;
- control arms do not contain forbidden full-arm-only Run 2.8, 2.9, or 2.10 fields;
- blocked public-release gates remain blocked unless human approval exists.

This gate should be reported in result docs. It should not automatically mark the deck public-ready.

## Tests

Add focused tests for the audit artifact and viewer integration.

Required assertions:

- `run2_11_data_workflow_audit.json` exists and has the required top-level fields.
- At least one chain covers Run 2.8 tutorial decomposition, executable memory, workflow gate, and actual trace evidence.
- At least one chain covers Run 2.9 visual primitives, executable visual modules, visual gate, and actual trace evidence.
- At least one chain covers Run 2.10 visual-system sources, memory, gate matrix, and actual trace evidence.
- Every chain has a valid `status`.
- Weak or missing chains include `next_fix`.
- Control-boundary checks are represented for prompt-only, Run 1.5, and negative-control arms.
- The HTML viewer includes the `Data/Workflow Audit` tab and can render the audit artifact.

## Result Reporting

Create:

- `docs/product/ppt-run2-data-skill-quality/results/run2_11_data_workflow_audit.md`

Update:

- `docs/product/ppt-run2-data-skill-quality/results/README.md`
- `docs/product/ppt-run2-data-skill-quality/results/comparison_report.md`
- `docs/product/ppt-run2-data-skill-quality/results/delivery_gate.md`

The report should state plainly:

- what data/workflow progress is already proven;
- what is merely documented but weak;
- what is missing before the next rerun;
- whether Run 2.12 should add more data, strengthen workflow gates, or rerun four arms.

## Non-Goals

- Do not generate a new PPT deck in this pass.
- Do not advance to Run 3.0.
- Do not claim public readiness.
- Do not copy screenshots, source layouts, logos, video frames, audio, long prose, or full transcripts.
- Do not treat source count as quality by itself.
- Do not treat a trace field as proof unless it corresponds to an actual generator obligation or recorded module call.
- Do not weaken existing public-blocked gates.

## Success Criteria

Run 2.11 is successful if:

1. The audit artifact proves which data/workflow chains are pass, weak, missing, or blocked.
2. The viewer shows data/workflow progress clearly enough to inspect without reading every JSON file.
3. Tests enforce the source-to-memory-to-gate-to-trace chain for Runs 2.8, 2.9, and 2.10.
4. The result recommends the next action based on audit evidence rather than aesthetic preference.
5. Public release remains blocked unless render, source-brand, and human approval gates pass.
