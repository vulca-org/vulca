# Workspace Production Persistence Spec

Vault status: protected product persistence spec.

## Purpose

This file defines the product design for production-grade Workspace
persistence. It turns the current Workspace preview and shared review-state
slice into a durable, multi-user Creative Repo product layer.

This is a product spec, not only a backend implementation note. It defines what
must be saved, who may change it, how concurrent review work is resolved, and
which evidence is required before VULCA can claim product-level release
readiness.

## Current Baseline

The current platform state has three relevant merged slices:

- PR #31 adds the Workspace review product shell.
- PR #32 adds local durable review state and release-owner audit trail
  persistence.
- PR #34 adds a shared in-process backend review-state API at
  `/api/v1/workspace/review-state/{repo_id}` and frontend Workspace load/save
  mirroring.

The baseline proves the product direction and a shared API surface. It does not
prove production persistence, authorization, conflict handling, or
multi-instance behavior.

## Product Position

Production persistence belongs to the Workspace / Creative Repo product layer.

```text
VULCA Product
  -> Workspace / Creative Repo
     -> Review UI
     -> EvidencePack / Artifact Bridge
     -> Decision / ReleaseGate
     -> Production Persistence and Collaboration Layer
```

The persistence layer is successful only if a reviewer can leave, reload,
switch device, or collaborate with another reviewer without losing review
items, evidence, decisions, blocker state, release gates, or audit history.

## Non-Goals

- Do not treat process memory as production storage.
- Do not let client-side normalization be the only release safety boundary.
- Do not let agents or system checks finalize public release.
- Do not use this spec to upgrade product-level R5 until implementation
  evidence and a human release owner decision exist.
- Do not turn Workspace into a generic file drive or editor replacement.

## Product Objects

Production persistence must preserve these objects independently, not only as a
single opaque JSON blob:

| Object | Product meaning | Persistence requirement |
| --- | --- | --- |
| `CreativeRepo` | One project source of truth | Durable repo identity, owner, status, timestamps |
| `Brief` | Business, visual, and cultural task | Versioned brief text and source references |
| `MotifBranch` | Creative direction under review | Branch identity, status, parent repo, versions |
| `VisualVariant` | Generated/imported candidate or version | Artifact refs, provenance, visible labels |
| `AgentRun` | Execution trace inside the repo | Tool name, model/provider, warnings, outputs |
| `EvidencePack` | Proof bundle for a decision | Source refs, checks, missing evidence, timestamps |
| `ReviewItem` | Unit of review work | Assignee, mode, status, selected artifact, blocker state |
| `Decision` | Human or advisory review decision | Actor, role, action, reason, revision |
| `ReleaseGate` | Product release boundary | Public release blocked unless human release owner clears it |
| `AuditEvent` | Durable history entry | Append-only actor, action, target, before/after revision |

The compatibility snapshot can still exist for frontend convenience, but it
must be derived from these durable records.

## Roles And Authorization

Every persistence operation must resolve the actor and role before reading or
writing Workspace state.

| Role | May read | May write | May release |
| --- | --- | --- | --- |
| `repo_owner` | Own repos | Repo metadata, members, archive state | No by default |
| `reviewer` | Assigned review items | Review decisions, comments, evidence notes | No |
| `release_owner` | Release queue and all evidence | Final release decision and gate notes | Yes, with audit |
| `agent` | Assigned execution context | AgentRun, advisory checks, evidence drafts | No |
| `system` | Operational metadata | migrations, derived indexes, health state | No |

Authorization rules:

- A user cannot read a repo without membership or owner access.
- A reviewer cannot change repo membership or release-owner status.
- An agent can append evidence and advisory checks, but cannot clear the
  release gate.
- A release-owner action must create an append-only `AuditEvent`.
- Failed authorization must return a stable 403 response and must not mutate
  state.

## Persistence Architecture

The production backend should store Workspace state in a database-backed model,
not process memory.

Required storage properties:

- database-backed state survives backend restart;
- state is shared across backend instances;
- write operations are atomic at the review item or repo revision boundary;
- audit events are append-only;
- artifact files are referenced by durable object storage paths, not embedded
  in the review-state snapshot;
- each mutable aggregate has a revision number.

Recommended aggregate boundaries:

- `CreativeRepo` aggregate: repo metadata, members, current revision.
- `ReviewItem` aggregate: review status, selected variant, staged decision,
  blocker state.
- `EvidencePack` aggregate: source refs, check outputs, missing evidence.
- `ReleaseGate` aggregate: current gate state and release-owner decision.
- `AuditEvent` stream: immutable change history across all aggregates.

## API Contract

The existing endpoint remains the compatibility route:

```text
GET    /api/v1/workspace/review-state/{repo_id}
PUT    /api/v1/workspace/review-state/{repo_id}
DELETE /api/v1/workspace/review-state/{repo_id}
```

Production behavior changes:

- `GET` returns a snapshot derived from durable database records.
- `PUT` validates actor permissions, checks revision, writes durable records,
  and appends audit events.
- `DELETE` is test/admin-only outside production user flows.
- Every response includes the latest repo revision.

New production routes should be added around explicit operations:

```text
POST /api/v1/workspace/repos
GET  /api/v1/workspace/repos/{repo_id}
POST /api/v1/workspace/repos/{repo_id}/review-items
PUT  /api/v1/workspace/repos/{repo_id}/review-items/{item_id}/decision
POST /api/v1/workspace/repos/{repo_id}/evidence-packs
PUT  /api/v1/workspace/repos/{repo_id}/release-gate
GET  /api/v1/workspace/repos/{repo_id}/audit-events
```

The compatibility route can call these service-layer operations internally.

## Conflict Model

The production product must not silently overwrite another reviewer.

Required behavior:

- every mutable response includes `revision`;
- every write sends the base `revision`;
- stale writes return 409 with the latest revision and changed fields;
- frontend shows a conflict state instead of discarding local edits;
- non-overlapping evidence additions may be merged by the backend when the
  service can prove the merge is safe;
- release-owner decisions never auto-merge.

Minimum conflict policy:

```text
if request.base_revision != current_revision:
  reject with 409
  return current_revision
  return changed_fields
else:
  commit write
  append audit event
  increment revision
```

## Release-Gate Safety

Release safety must be enforced in the backend service layer.

Rules:

- Stored release gates default to public blocked.
- Incoming client snapshots cannot upgrade release state without a
  release-owner operation.
- AgentRun and system-derived checks may add advisory evidence only.
- Release-owner decisions must reference current EvidencePack revisions.
- A release-owner decision must include actor, role, timestamp, rationale, and
  current repo revision.

## Migration From Current Slice

Migration from PR #34 should be staged:

1. Keep the existing review-state endpoint as the frontend compatibility route.
2. Add database tables and service-layer operations behind the endpoint.
3. Store the current sample Workspace repo as seeded database data.
4. Convert frontend saves from whole-snapshot writes to operation-specific
   writes.
5. Keep snapshot loading for initial page hydration until the UI reads specific
   objects directly.
6. Add authorization and revision checks before any public demo uses shared
   production data.

## Acceptance Gates

Production persistence is not accepted until these gates pass:

- Backend unit tests prove release gate normalization and authorization.
- Backend integration tests prove database persistence across app restart.
- Multi-client tests prove two reviewers see the same committed state.
- Conflict tests prove stale writes return 409 without mutation.
- Multi-instance tests prove state is shared outside one process.
- Frontend tests prove conflict UI and sync failure behavior.
- E2E tests prove create, reload, update, decision, audit, and release-gate
  flows through the database-backed API.
- A release-readiness report records the human release owner decision.

## R-Level Effect

This spec does not upgrade current release status by itself.

- Current maximum from protected vault evidence remains R4, example-specific.
- Product-level R5 remains blocked.
- R5 can be reconsidered only after production persistence, artifact ingestion,
  EvidencePack rendering, human release workflow, public example quality, and
  website/PPT copy gates all have implementation evidence and a human release
  owner decision.

## Sources

- `docs/review-context/07-workspace-product-model.md`
- `docs/review-context/11-artifact-bridge-spec.md`
- `docs/review-context/12-complete-demo-path.md`
- `docs/review-context/14-release-readiness-evidence-gate.md`
- `docs/review-context/workspace-durable/README.md`
- `docs/review-context/release-readiness/M5-CLOSEOUT.md`
- `yha9806/vulca-platform` PR #31.
- `yha9806/vulca-platform` PR #32.
- `yha9806/vulca-platform` PR #34.
