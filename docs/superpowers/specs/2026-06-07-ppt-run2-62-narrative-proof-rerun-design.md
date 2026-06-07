# PPT Run 2.62 Narrative Proof Rerun Design

Status: approved-by-continuation.

## Context

Run 2.61 created the missing data/workflow layer: per-slide narrative proof contracts that join reader questions, required answers, proof payloads, visual carrier selection, text socket fusion, density budgets, public proof replacement, source references, and workflow gates.

The next step is not more source collection. The next step is to prove whether those contracts actually change the generated deck.

## Goal

Run 2.62 generates a new four-arm PPT experiment that consumes Run 2.61 before native PPT drawing.

The full arm must expose Run 2.61 consumption in:

- every slide trace record;
- visible slide notes/profile artifacts;
- the Run 2.62 result JSON/MD;
- the HTML viewer four-arm comparison;
- the full-skill horizontal comparison.

## Non-Goals

- Do not add more tutorial, video, or case data in this run.
- Do not advance to Run 3.0.
- Do not claim public release readiness.
- Do not copy source visuals, screenshots, video frames, or brand layouts.
- Do not solve the problem by making slides text-heavy.

## Chosen Approach

Create a Run 2.62 generator based on the Run 2.60 four-arm structure, but replace the main consumed layer:

`Run 2.60 full arm consumes Run 2.59 composition compiler`

becomes:

`Run 2.62 full arm consumes Run 2.61 narrative proof contracts`

The bad control should still use the prior generated path but must not read or emit Run 2.61 contract fields.

## Four Arms

- `prompt_only`
- `run1_5_skill`
- `run2_62_full_narrative_proof`
- `bad_run2_60_without_run2_61_narrative_proof_dataset`

## Required Full-Arm Trace Fields

Every full-arm slide must include:

- `run2_61_narrative_proof_id`
- `run2_61_visual_carrier_selector_id`
- `run2_61_text_socket_fusion_contract_id`
- `run2_61_public_proof_replacement_id`
- `run2_61_narrative_workflow_gate_id`
- `run2_62_narrative_proof_consumption_status`
- `run2_62_socket_binding_count`
- `run2_62_public_proof_object_count`
- `run2_62_required_answer_visible`

The bad-control arm must leave the Run 2.61 IDs empty and mark the missing-contract status.

## Visual Contract

Run 2.62 does not promise final aesthetics. It promises that the generated slides are driven by richer contracts:

- headline and subhead come from `copy_units`;
- proof badges and annotations come from Run 2.61;
- the primary proof object comes from `proof_payload.primary_evidence_object`;
- the carrier type comes from `visual_carrier_type`;
- visible density stays within `density_budget.maximum_public_visible_words`;
- public proof replacement appears as an editable proxy, not copied source media.

## Success Criteria

- New generator creates four arms, trace manifests, contact sheets, and result docs.
- Viewer latest generated run becomes `2.62`.
- Full arm has six slides with all Run 2.61 IDs and socket counts.
- Bad control has six slides without Run 2.61 IDs and with the expected failure status.
- Full-skill series includes Run 2.62.
- Relevant tests, lint, py_compile, generated viewer, and browser DOM checks pass.

