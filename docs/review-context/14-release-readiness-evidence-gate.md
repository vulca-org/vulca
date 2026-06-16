# Release Readiness Evidence Gate

Vault status: protected release-readiness gate.

## Purpose

This file defines M5: the evidence gate for moving VULCA work from preview or
internal proof toward release-ready claims.

Release readiness is not copy polish. It requires implementation evidence,
review evidence, public-example evidence, and human release decisions.

The gate covers:

```text
Workspace persistence
  -> real artifact ingestion
  -> evidence-pack rendering
  -> human release workflow
  -> public example quality gates
  -> claim-spine review
  -> release status decision
```

Until those gates pass, VULCA should keep using preview, internal proof,
public blocked, or human review required language.

## Current Status

As of the current vault state:

- `master` README exposes the Workspace direction.
- Workspace preview implements review triage, asset review, context drawer,
  checks, decisions, manual upload intake, and visible release boundaries.
- SDK/MCP has implemented execution capabilities and case/evidence substrates.
- The artifact bridge, demo path, and website/PPT claim spine are specified in
  protected vault documents.
- RR1 has a fixed release-readiness report template in
  `release-readiness/TEMPLATE.md`.
- RR2 has a protected M3 bridge fixture in
  `artifact-bridge/m3-demo-bridge-fixture.json`.
- RR3 has a protected durable review fixture in
  `workspace-durable/m3-durable-review-fixture.json`.
- RR4 has a protected public example gate in
  `public-examples/m3-public-example-gate.json`.
- RR5 has a protected website/PPT copy gate in
  `copy-gates/website-ppt-copy-gate.json`.
- M5 closeout is recorded in
  `release-readiness/m5-closeout-summary.json`.
- Production Workspace persistence design is specified in
  `15-workspace-production-persistence-spec.md`.
- PPT proof lab remains public blocked by the latest remembered Run 2.93 gate.

Still missing for product release readiness:

- persistent Creative Repo storage;
- real SDK/MCP artifact ingestion into Workspace;
- durable EvidencePack rendering;
- human-owned release workflow with audit trail;
- public example visual quality gates;
- copy reviewed against claim boundaries after implementation evidence lands.

Closeout note:

- The current protected vault closeout supports R4 example-specific public copy
  only. Product-level R5 remains blocked.

## Release Levels

Use these release levels across code, docs, website, PPT, and internal planning.

| Level | Name | Meaning | Public copy |
| --- | --- | --- | --- |
| R0 | internal draft | incomplete or exploratory work | do not publish |
| R1 | internal proof | useful evidence, not public-ready | internal only |
| R2 | preview-gated | coherent demo or preview workflow | allowed with preview qualifier |
| R3 | internal pilot ready | human-reviewed internal workflow | allowed with internal qualifier |
| R4 | public example ready | specific public example passed evidence and quality gates | example-specific public use |
| R5 | product release ready | repeated implementation, persistence, review, and release evidence | product-level public claim |

Default state for Workspace, PPT, and provider-backed visual examples is R2 or
lower unless fresh evidence proves otherwise.

## Required Gates

### Gate 1: Workspace Persistence

Required evidence:

- Creative Repo data persists beyond browser session;
- review item state persists;
- version history persists;
- blockers and decisions persist;
- release gate state persists;
- access boundaries are defined for reviewers and release owners.

Minimum verification:

- backend or durable local storage implementation evidence;
- tests for create, reload, update, and recover workflows;
- migration or seed-data story for demo objects;
- failure behavior when persistence fails.

Current evidence:

- Platform PR #32 adds local durable review state and release-owner audit trail
  persistence for the Workspace preview.
- Platform PR #34 adds a shared in-process backend review-state API and
  frontend Workspace load/save mirroring, with backend-side
  `public_ready=false` locking.
- Platform PR #35 upgrades that compatibility endpoint from process memory to
  SQLAlchemy-backed database persistence for the whole review-state snapshot.
- Platform PR #36 adds revision metadata, optional `baseRevision` 409 conflict
  checks, stale-after-clear protection, write/delete row locking, and
  append-only save/clear audit events for the compatibility snapshot route.
- Platform PR #37 adds a trusted actor/role gate for the compatibility route,
  production fail-closed save/clear behavior without trusted upstream actor
  headers, clear restricted to `release_owner`, `repo_owner`, or `system`, and
  actor id/role metadata in save/clear audit events.
- Platform PR #39 adds database-backed `workspace_review_memberships` and
  requires production save/clear operations on the compatibility route to
  match an active repo membership for the trusted actor id and role.
- Platform PR #40 extends trusted actor and active membership checks to
  production load operations on the compatibility route, so load/save/clear
  all fail closed without trusted actor and matching active membership.
- Platform PR #41 adds trusted `system` actor routes to provision and
  deactivate the `workspace_review_memberships` rows used by the compatibility
  route gates, with role validation and membership admin audit events.
- Platform PR #45 adds typed Workspace core records behind the same
  compatibility route, including bounded typed sync into Creative Repo, review
  item, evidence pack, release gate, and typed audit tables; typed overlay
  load with release-gate safety; archive/reactivate lifecycle; rollback,
  conflict, idempotency, stale-child cleanup, production membership, and
  OpenAPI stability tests.
- `15-workspace-production-persistence-spec.md` defines the product design for
  database-backed storage, authorization, conflict handling, audit events, and
  multi-instance behavior.

Remaining boundary:

- PR #45 proves a typed core foundation under the compatibility route, but it
  does not prove full user/JWT authentication, end-user or repo-owner
  self-service membership management UI, operation-specific frontend writes,
  real SDK/MCP artifact ingestion into typed records, release-owner human
  workflow semantics, ingress header-stripping configuration, multi-instance
  acceptance behavior, or product-level R5.

Blocked until:

- the typed core foundation is supplemented by production-grade access
  boundaries beyond trusted headers and system-admin compatibility-route
  membership checks, operation-specific frontend writes, real artifact
  ingestion, release-owner human workflow semantics, and multi-instance
  evidence for the demo path.

### Gate 2: Artifact Ingestion

Required evidence:

- SDK/MCP outputs enter Workspace through the artifact bridge;
- bridge records preserve source operation, artifact paths, provider/model
  metadata, warnings, claim state, and review labels;
- generated/imported assets become `VisualVariant` records;
- tool executions become `AgentRun` records;
- case records remain evidence substrate, not human labels.

Minimum verification:

- bridge schema or adapter tests;
- ingestion tests for `generate_image`, `layers_split`, `layers_redraw`, and
  `evaluate_artwork`;
- negative test that automated evidence cannot set final public release;
- fixture showing the M3 demo path imported into Workspace.

Blocked until:

- the M2 bridge spec has a real adapter and Workspace import preview.

### Gate 3: EvidencePack Rendering

Required evidence:

- EvidencePack renders brief, motif, artifact, provider, prompt, layer,
  evaluation, warning, and source refs;
- reviewers can inspect evidence on demand;
- missing evidence is visible as a blocker, not silently ignored;
- evidence packs link back to bridge records or source artifacts.

Minimum verification:

- component tests for EvidencePack rendering;
- fixture with complete and partial evidence;
- UI test that context drawer or evidence surface is hidden until requested but
  available before decision;
- source-boundary copy for incomplete evidence.

Blocked until:

- reviewers can see enough evidence to decide without opening raw logs first.

### Gate 4: Human Release Workflow

Required evidence:

- release owner role exists;
- human decision actions are explicit;
- request-changes, block-release, and internal-approval paths are represented;
- public-release state cannot be set by agent/system/external checks;
- decision history records actor, action, summary, and timestamp;
- release gate blockers remain visible.

Minimum verification:

- tests proving agent/system checks have `canSetPublicReady = false`;
- tests for decision state transitions;
- tests for blocker persistence;
- audit/history fixture for human decisions;
- copy review that distinguishes internal approval from public release.

Blocked until:

- human release decisions are durable and auditable.

### Gate 5: Public Example Quality

Required evidence for any public visual example:

- source artifacts are preserved;
- final preview image or artifact is inspectable;
- visual quality review passes for the specific example;
- cultural/evidence review is qualified and source-backed;
- release owner signs off for that example;
- claims attached to the example match evidence.

Minimum verification:

- public-example checklist;
- screenshot or artifact review;
- visual quality gate result;
- evidence-pack review;
- release decision record;
- no stale `public blocked` result is reused as a public-ready proof.

Blocked until:

- each public example has fresh, specific evidence. One cleared example does
  not clear all provider-backed or PPT examples.

### Gate 6: Website/PPT Claim Review

Required evidence:

- copy follows `13-website-ppt-claim-spine.md`;
- website, README, and PPT use the same product spine;
- preview/internal/public-blocked status is preserved;
- public examples trace to the M3 demo path or equivalent source-backed path;
- translations preserve the same claim level.

Minimum verification:

- copy checklist review;
- forbidden-claim search;
- bilingual claim-level check when applicable;
- source index links for proof claims;
- explicit downgrade language for incomplete evidence.

Blocked until:

- implementation evidence exists first. Copy cannot upgrade a preview system.

## Release Decision Matrix

| Evidence state | Allowed status | Required wording |
| --- | --- | --- |
| docs/spec only | R0/R1 | planned, specified, protected context |
| frontend-only preview | R2 | preview-gated, browser/session-local if relevant |
| durable demo with imported artifacts | R2/R3 | preview workflow or internal pilot |
| human-reviewed internal workflow | R3 | internal pilot ready, human reviewed |
| one public example cleared | R4 | public example ready, example-specific |
| repeated persisted workflows with release audit | R5 | product release ready |

If evidence is mixed, use the lowest applicable status.

## Required Artifacts For M5 Completion

M5 is complete only when these artifacts exist and are source-backed:

- release readiness implementation report;
- artifact bridge adapter test report;
- Workspace persistence test report;
- EvidencePack rendering test report;
- human release workflow test report;
- public example gate report;
- website/PPT copy review report;
- release decision record with human owner.

These can live outside the vault in product or platform branches, but the vault
must index them before any status upgrade is treated as durable memory.

## Implementation Sequence

### RR1: Static Release Gate Checklist

Create a machine-readable checklist or Markdown report template for the M5
gates.

Status: represented by `release-readiness/TEMPLATE.md`.

Acceptance:

- includes Gates 1-6;
- records evidence links;
- records reviewer/owner;
- defaults public release to blocked when evidence is missing.

### RR2: Bridge Adapter And Fixture

Implement or document one real bridge adapter path for the M3 demo.

Status: represented by `artifact-bridge/m3-demo-bridge-fixture.json`.

Acceptance:

- generated or imported asset becomes a bridge record;
- bridge record projects into Workspace objects;
- missing evidence remains visible.

### RR3: Workspace Durable Review Path

Implement persistence or a clearly bounded durable demo store.

Status: represented by `workspace-durable/m3-durable-review-fixture.json`.

Acceptance:

- reload preserves review item, evidence, blocker, and decision state;
- agent/system checks cannot finalize public release;
- human decision history is auditable.

### RR4: Public Example Gate

Run one example through visual, evidence, copy, and release review.

Status: represented by `public-examples/m3-public-example-gate.json`.

Acceptance:

- evidence pack exists;
- visual quality is reviewed;
- release owner records decision;
- public copy remains example-specific.

### RR5: Website/PPT Copy Gate

Apply the M4 claim spine to website and deck copy after implementation evidence
exists.

Status: represented by `copy-gates/website-ppt-copy-gate.json`.

Acceptance:

- public copy uses R-level status accurately;
- proof-lab outputs remain internal or public blocked unless cleared;
- translations do not upgrade claims.

## Non-Negotiable Boundaries

- Release readiness cannot be inferred from a passing unit test alone.
- Public copy cannot upgrade a missing implementation.
- Agent/system checks cannot clear public release.
- Case records are evidence substrate until reviewed.
- Public examples are cleared one at a time.
- PPT proof-lab outputs remain blocked until their own fresh gates pass.
- A human release owner must record final release decisions.

## Sources

- `docs/review-context/09-claim-boundaries.md`
- `docs/review-context/10-integration-spine.md`
- `docs/review-context/11-artifact-bridge-spec.md`
- `docs/review-context/12-complete-demo-path.md`
- `docs/review-context/13-website-ppt-claim-spine.md`
- `docs/review-context/15-workspace-production-persistence-spec.md`
- `origin/master:docs/product/workspace-current-state-audit.md`
- `docs/platform/release-readiness-status.md`
- Platform Workspace baseline `6efef07 fix: align workspace context review controls`
- Latest merged Workspace platform state
  `d06a713bf490ad870fe9273f933c310e2955b4e9`
- PPT proof lab source index entry and Run 2.93 public-blocked gate
