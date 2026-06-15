# Artifact Bridge Specification

Vault status: protected integration specification.

## Purpose

This file defines how VULCA SDK/MCP outputs become VULCA Workspace review
objects. It is the M2 bridge underneath the integration spine.

The bridge has one job:

```text
SDK/MCP artifact or case record
  -> normalized bridge record
  -> Workspace object projection
  -> review request and evidence pack
  -> release gate remains human-controlled
```

The bridge must preserve evidence. It must not turn tool output, agent
recommendations, or automated evaluation into final human release approval.

## Boundary

The bridge is a specification for product integration. It is not yet a backend
implementation, file store, hosted API, or production Workspace ingestion
system.

Current status:

- SDK/MCP outputs are source-backed in the `vulca` repository.
- Workspace review objects are source-backed in the `vulca-platform` preview.
- `master` documents Workspace direction and current boundaries.
- RR2 has a protected M3 demo fixture at
  `artifact-bridge/m3-demo-bridge-fixture.json`.
- Real artifact ingestion into Workspace remains a next implementation step.

## Bridge Envelope

Every SDK/MCP output that enters Workspace should first normalize into a bridge
record. The record is an evidence envelope, not a UI object.

Minimum record:

```json
{
  "schema_version": 1,
  "bridge_record_id": "bridge_...",
  "created_at": "2026-06-15T00:00:00Z",
  "source_system": "vulca-sdk-mcp",
  "source_operation": "layers_redraw",
  "source_refs": {
    "repo": "vulca",
    "commit": "",
    "tool": "layers_redraw",
    "case_id": "",
    "case_log_path": "",
    "agent_session_id": ""
  },
  "workspace_targets": {
    "creative_repo_id": "",
    "brief_id": "",
    "motif_branch_id": "",
    "visual_variant_id": "",
    "review_request_id": "",
    "release_gate_id": ""
  },
  "operation": {
    "kind": "redraw",
    "input_summary": "",
    "instruction": "",
    "tradition": "",
    "provider": "",
    "model": "",
    "route": "",
    "parameters": {}
  },
  "artifacts": {
    "primary_asset_path": "",
    "manifest_path": "",
    "layer_paths": [],
    "mask_paths": [],
    "composite_path": "",
    "pasteback_path": "",
    "debug_paths": []
  },
  "evidence": {
    "prompt_refs": [],
    "semantic_paths": [],
    "quality": {},
    "evaluation": {},
    "warnings": [],
    "risk_flags": []
  },
  "review": {
    "human_accept": null,
    "agent_recommendation": "",
    "failure_type": "",
    "preferred_action": "",
    "reviewer": "",
    "reviewed_at": ""
  },
  "claim_state": {
    "status": "preview_gated",
    "public_ready": false,
    "boundary_notes": ""
  }
}
```

Rules:

- Paths stay as path strings. Do not embed image bytes or base64 in the bridge
  record.
- Empty strings mean unavailable or not yet linked. Do not guess paths, model
  names, review labels, or human approval.
- `public_ready` defaults to `false` and can only change through a human-owned
  release workflow that is not implemented in the observed Workspace preview.
- Tool warnings, quality advisory fields, risk flags, and failure labels must
  remain visible to Workspace review.

## Operation Mapping

| SDK/MCP operation | Bridge `operation.kind` | Required evidence |
| --- | --- | --- |
| `/visual-discovery` | `discovery` | direction record, taste/culture profile, sketch prompt refs |
| `/visual-brainstorm` | `brainstorm` | `proposal.md`, options, constraints, L1-L5 rubric |
| `/visual-spec` | `visual_spec` | `design.md`, source confidence, prompt derivation |
| `/visual-plan` | `visual_plan` | `plan.md`, execution gates, intended artifacts |
| `generate_image` | `generate` | `image_path`, provider, metadata, prompt, generation parameters |
| `layers_split` | `decompose` | `manifest_path`, `layers`, semantic paths, detection report |
| `layers_redraw` | `redraw` | redrawn layer path, pasteback path, advisory fields, case record when enabled |
| `inpaint_artwork` | `inpaint` | source image, mask path, output path, provider/model |
| `layers_composite` | `composite` | manifest path, composite path, visible layers |
| `evaluate_artwork` | `evaluate` | score, dimensions, rationales, recommendations, risk flags |
| `archive_session` | `archive` | session artifact paths and metadata |
| `redraw_case` | `case_record` | case id, JSONL path, quality, route, review labels |
| `decompose_case` | `case_record` | case id, JSONL path, output manifest, quality, review labels |
| `layer_generate_case` | `case_record` | case id, manifest, generated layers, prompt stack, review labels |

## Workspace Projection

The bridge record projects into Workspace objects. Projection is lossy for UI,
but the original bridge record must stay linkable as evidence.

### `Brief`

Create or update a `Brief` from:

- user intent;
- business/audience context;
- source constraints;
- success criteria;
- public claim candidates;
- cultural or visual tradition context.

Bridge sources:

- visual discovery records;
- brainstorm proposals;
- visual specs;
- manual upload intake brief text.

### `MotifBranch`

Create or update a `MotifBranch` from:

- direction options;
- motif contract;
- prompt policy;
- visual language;
- changed-from-main rationale.

Bridge sources:

- `/visual-brainstorm`;
- `/visual-spec`;
- `/visual-plan`;
- prompt composition records;
- tradition guides and L1-L5 rubrics.

### `VisualVariant`

Create or update a `VisualVariant` for any candidate asset or version.

Required fields:

- variant id;
- title;
- source tool;
- provenance;
- linked `AgentRun`;
- source boundary;
- internal review status;
- primary asset path or manifest path;
- current version metadata.

Bridge sources:

- `generate_image.image_path`;
- `layers_split.manifest_path`;
- `layers_redraw.file`;
- `layers_redraw.source_pasteback_path`;
- `layers_composite` output path;
- manual upload metadata.

### `AgentRun`

Create an `AgentRun` for each tool or agent execution that produced evidence.

Required fields:

- agent or tool name;
- action;
- output artifact paths;
- provider/model when available;
- parameters that affect output;
- warnings and errors;
- cost and latency when available.

Bridge sources:

- MCP tool payloads;
- provider metadata;
- case ids;
- prompt refs;
- debug artifact paths.

### `EvidencePack`

Create an `EvidencePack` from the evidence fields that reviewers need before
deciding.

Required fields:

- protocol refs;
- artifact refs;
- prompt refs;
- provider/model refs;
- L1-L5 snapshot when evaluation exists;
- quality advisory fields;
- boundary notes;
- accept/reject rationale when available.

Bridge sources:

- `evaluate_artwork` result fields;
- `layers_split.detection_report`;
- `layers_redraw.redraw_advisory`;
- case record quality and review fields;
- source-index links for claim provenance.

### `ReviewRequest`

Create a `ReviewRequest` when an artifact needs human review.

Required fields:

- title;
- linked variant;
- required reviewers or roles;
- required checks;
- current blocker;
- decision state;
- human override note.

Bridge sources:

- Workspace `ReviewItem`;
- bridge `claim_state`;
- evidence blockers;
- manual upload intake;
- release gate blockers.

### `ReleaseGate`

Create or update a `ReleaseGate` only as a blocker and decision surface.

Required fields:

- `publicReady: false` by default;
- release label;
- blockers;
- final approver role;
- boundary notes.

Bridge sources:

- evaluation risk flags;
- claim boundaries;
- review checks;
- human release decision.

Automated tools and agent findings may add blockers or recommendations. They
must not clear public release by themselves.

## Case Record Bridge

Case records are especially important because they preserve future learning
evidence. The bridge should treat them as evidence substrate, not human labels.

### `redraw_case`

Map to:

- `VisualVariant`: redrawn layer and pasteback preview;
- `AgentRun`: redraw execution;
- `EvidencePack`: route, geometry, quality, refinement, artifacts;
- `ReviewRequest`: human accept/reject pending.

Important preserved fields:

- `case_id`;
- `artwork_dir`;
- `source_image`;
- layer id/name/semantic path;
- instruction;
- provider/model;
- route requested/chosen;
- geometry;
- quality gate result;
- source/redrawn/pasteback paths;
- review labels.

### `decompose_case`

Map to:

- `VisualVariant`: decomposed layer stack;
- `EvidencePack`: manifest, layers, residual, detection report, debug artifacts;
- `AgentRun`: split/decompose execution;
- `ReviewRequest`: editability review pending.

Important preserved fields:

- `case_id`;
- source image;
- requested mode/provider/model/tradition;
- target layer hints;
- output directory;
- manifest path;
- layer list;
- residual and composite paths;
- detection report;
- quality metrics;
- review labels.

### `layer_generate_case`

Map to:

- `Brief`: user intent and constraints;
- `MotifBranch`: layer plan and prompt policy;
- `VisualVariant`: generated layered artifact;
- `AgentRun`: provider generation run;
- `EvidencePack`: prompt stack, layer manifest, generated layers, composite;
- `ReviewRequest`: generation quality review pending.

Important preserved fields:

- `case_id`;
- user intent;
- tradition;
- style constraints;
- layer plan;
- prompt stack paths and hashes;
- provider/model;
- output artifact directory;
- layer manifest;
- composite and preview paths;
- review labels.

## Review Check Bridge

Workspace `ReviewCheck` objects should be generated from evidence, but their
release behavior must stay conservative.

| Evidence source | Review mode | Check source | Release behavior |
| --- | --- | --- | --- |
| visual QA or layer quality warnings | `visual-qa` | `agent` or `system` | may warn or block |
| L1-L5 evaluation | `cultural-review` | `agent` or `system` | may warn or block |
| manual evidence review | `release-review` | `human` | may approve internally or block |
| external tool import | `visual-qa` | `external` | must preserve provenance |
| legal/commercial claim review | `release-review` | `human` | human-owned |

`canSetPublicReady` must remain `false` for agent, system, and external checks
in the observed Workspace model.

## Claim State

Use this bounded claim-state vocabulary in bridge records:

- `draft`: artifact is still being formed.
- `preview_gated`: artifact can be reviewed in Workspace but is not production
  ingestion or public release evidence.
- `internal_review`: artifact is ready for human internal review.
- `internal_blocked`: internal blockers exist.
- `internal_approved`: a human has approved internal use with boundary notes.
- `public_blocked`: public release is blocked.

Do not introduce a public approval state until the Workspace has a real human
release workflow, persistence, and source-backed release audit trail.

## Minimal Demo Path

The complete demo standard lives in `12-complete-demo-path.md`. The
implementation demo should use one path end to end:

```text
Brief
  -> visual plan
  -> generate or manual upload
  -> decompose or redraw evidence
  -> evaluate
  -> bridge record
  -> Workspace ReviewItem
  -> EvidencePack
  -> human decision
  -> ReleaseGate remains blocked or internally approved
```

The demo should prove linkage and review flow, not production readiness.

## Implementation Milestones

### AB1: Bridge Schema

Define the bridge record as a versioned JSON schema and add validator tests.

Minimum acceptance:

- validates required envelope fields;
- rejects missing source operation;
- preserves path refs as strings;
- rejects automated public-release approval;
- allows empty human review labels.

### AB2: SDK/MCP Export Adapter

Add a small adapter that converts existing MCP payloads into bridge records.

Minimum acceptance:

- `generate_image` -> bridge record;
- `layers_split` -> bridge record;
- `layers_redraw` -> bridge record;
- `evaluate_artwork` -> bridge record;
- case record -> bridge record.

### AB3: Workspace Import Preview

Add a frontend/session-local Workspace import path for bridge records.

Minimum acceptance:

- creates or updates a `ReviewItem`;
- links a `VisualVariant`;
- renders an `EvidencePack`;
- shows release boundary;
- preserves agent/system checks as advisory.

### AB4: One Complete Scenario

Create the first full demo path from brief to blocked or internally approved
release gate, using `12-complete-demo-path.md` as the product standard.

Minimum acceptance:

- all artifacts are traceable;
- evidence is visible on demand;
- agent findings cannot finalize public release;
- human decision remains explicit.

## Non-Goals

- Do not implement a backend by editing this spec.
- Do not store binary image data in bridge records.
- Do not use the bridge to claim production Workspace readiness.
- Do not collapse `redraw_case`, `decompose_case`, and `layer_generate_case`
  into one schema.
- Do not turn review labels into human-confirmed labels unless a human review
  workflow writes them.

## Sources

- `docs/review-context/10-integration-spine.md`
- `docs/review-context/02-capability-map.md`
- `docs/review-context/07-workspace-product-model.md`
- `docs/review-context/09-claim-boundaries.md`
- `src/vulca/mcp_server.py`
- `docs/superpowers/specs/2026-05-05-vulca-learning-loop-v0-design.md`
- `docs/superpowers/specs/2026-05-05-decompose-case-design.md`
- `docs/superpowers/specs/2026-05-05-layer-generate-case-design.md`
- Platform Workspace file:
  `/Users/yhryzy/.config/superpowers/worktrees/vulca-platform/workspace-interactive-demo/wenxin-moyun/src/content/workspaceDemo.ts`
- `origin/master:docs/product/workspace-current-state-audit.md`
