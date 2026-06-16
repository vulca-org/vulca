# M5 Closeout

Vault status: protected release-readiness closeout.

This closeout records the current M5 evidence state after RR1-RR5.

It does not mark VULCA as product-level release ready. It records that the
protected vault now has a complete review scaffold for release-readiness
assessment, while product-level R5 remains blocked until production evidence
and a human release owner decision exist.

## Current Decision

- Maximum supported public level from the protected vault evidence: R4,
  example-specific.
- Product-level R5 release state: blocked.
- Human release owner decision for product-level release: not recorded.
- Required boundary: public copy may cite the example-specific gate only when
  it preserves the R4 scope.

## Current Platform Merge State

As of 2026-06-16:

- Platform PR #31, `[codex] Workspace review product shell`, merged to
  `master` at `6810e67ca967a47782b5d9f83d751148d1eb6d26`. Its PR gate
  includes `tests/e2e/specs/workspace.spec.ts`, while the legacy full E2E suite
  is manual advisory because it still covers retired `/login` and `/canvas`
  flows.
- Platform PR #32, `[codex] Durable workspace review persistence`, merged to
  `master` at `61da8e9f296b7c1e66f61720e487e8e42d4eb6ce`. It implements local
  durable review state and the release-owner audit trail, with local
  verification plus remote `Run Tests` and `security` gates.
- Platform PR #34, `[codex] Shared Workspace review persistence`, merged to
  `master` at `d06a713bf490ad870fe9273f933c310e2955b4e9` from head
  `c6604cc3d59fb93f10c3267dc4ee4816bc63fc9e`. It implements a shared
  `/api/v1/workspace/review-state/{repo_id}` API, frontend Workspace load/save
  mirroring, backend-side `public_ready=false` locking, OpenAPI/module-boundary
  updates, and E2E isolation for shared review state. Its PR gate passed
  remote `Run Tests` and `security`.
- Platform PR #35, `feat: persist workspace review state in db`, merged to
  `master` at `24efaab5101494cfa7777aa3ded6d8c27e923870` from head
  `563e1dd`. It replaces the #34 in-process store with a SQLAlchemy
  `workspace_review_states` table behind the existing compatibility endpoint,
  preserves backend-side `public_ready=false` locking, and adds tests for
  cross-client DB persistence, process-local reset survival, table
  registration, clearing, OpenAPI contract stability, and DB dependency
  fallback. Its PR gate passed remote `Run Tests` and `security`.
- Platform PR #36, `feat: add workspace review revision conflicts`, merged to
  `master` at `3310093131132268ec9658736d3bd172ecccbe58` from head
  `2c1bd63`. It adds revision metadata, optional `baseRevision` 409 conflict
  checks, stale-after-clear protection, write/delete row locking, append-only
  save/clear audit events, and an Alembic migration for the audit table. Its
  PR gate passed remote `Run Tests` and `security`.
- Platform PR #37, `feat: gate workspace review actors`, merged to `master`
  at `0faf8748181c4d65f83b22b9a0b6ecfb10409b14` from head `b536d7e`. It adds
  trusted actor/role gating for the compatibility endpoint, production
  fail-closed save/clear behavior without trusted upstream actor headers, clear
  restricted to `release_owner`, `repo_owner`, or `system`, actor id/role audit
  metadata, and deployment notes for
  `WORKSPACE_REVIEW_ACTOR_HEADER_SECRET`. Its PR gate passed remote
  `Run Tests` and `security`.
- Platform PR #39, `feat: add workspace review memberships`, merged to
  `master` at `dff2331f95161ec909a07b76ef7e94ae7def3cfe` from head
  `b793c50`. It adds database-backed `workspace_review_memberships`, enforces
  active repo membership and role matching for production save/clear on the
  compatibility endpoint, and documents the fail-closed deployment boundary.
  Its PR gate passed remote `Run Tests` and `security`.
- Platform PR #40, `feat: gate workspace review reads`, merged to `master` at
  `d31e9bf8f6139c60ee10605337c32221a5098b8b` from head `e0a0bae`. It extends
  trusted actor and active membership checks to production load operations on
  the compatibility endpoint, making load/save/clear fail closed without a
  trusted actor and matching active membership. Its PR gate passed remote
  `Run Tests` and `security`.
- Platform PR #41, `feat: add workspace membership admin routes`, merged to
  `master` at `becbb072434bd4e0d9241e11a87717c7891926b5` from head
  `e196a3d`. It adds trusted `system` actor routes to provision and deactivate
  Workspace review memberships on the compatibility surface, including role
  validation, deactivate-with-history behavior, stable error responses,
  membership admin audit events, and deployment notes. Its PR gate passed
  remote `Run Tests` and `security`.
- Platform PR #45, `feat: add workspace typed production core`, merged to
  `master` at `530ecb8fc80a93756f96cba75ecdd9991bcb8db4` from head
  `97a001a`. It adds typed Workspace core persistence tables behind the
  existing compatibility API, bounded typed sync from compatibility saves,
  typed overlay load, archive/reactivate lifecycle, typed audit events,
  rollback/conflict safety, production membership integration, OpenAPI
  stability, and README boundary notes. Its PR gate passed remote `Run Tests`
  and `security`.

These PRs improve R5 evidence, but they do not change the product-level
decision above.

The next product-design reference for closing the remaining persistence
blocker is `15-workspace-production-persistence-spec.md`.

## Indexed Evidence

- RR1 checklist/report template:
  `release-readiness/TEMPLATE.md`
- RR2 bridge adapter fixture:
  `artifact-bridge/m3-demo-bridge-fixture.json`
- RR3 durable review fixture:
  `workspace-durable/m3-durable-review-fixture.json`
- RR4 public example gate:
  `public-examples/m3-public-example-gate.json`
- RR5 website/PPT copy gate:
  `copy-gates/website-ppt-copy-gate.json`
- Machine-readable closeout:
  `release-readiness/m5-closeout-summary.json`
- Production Workspace persistence spec:
  `15-workspace-production-persistence-spec.md`

## Remaining R5 Blockers

- production-grade Workspace persistence beyond the DB-backed compatibility
  snapshot and typed core foundation, including full user/JWT authorization,
  end-user or repo-owner self-service membership management UI beyond the
  system-only compatibility admin route, operation-specific frontend writes,
  real artifact ingestion into typed records, release-owner human workflow
  semantics, ingress header-stripping proof, and multi-instance behavior;
- repeated bridge ingestion across more than one workflow;
- production EvidencePack rendering evidence;
- human-owned release workflow implementation evidence;
- release owner decision for product-level release.

## Sources

- `docs/review-context/14-release-readiness-evidence-gate.md`
- `docs/review-context/15-workspace-production-persistence-spec.md`
- `docs/review-context/release-readiness/TEMPLATE.md`
- `docs/review-context/artifact-bridge/m3-demo-bridge-fixture.json`
- `docs/review-context/workspace-durable/m3-durable-review-fixture.json`
- `docs/review-context/public-examples/m3-public-example-gate.json`
- `docs/review-context/copy-gates/website-ppt-copy-gate.json`
- `yha9806/vulca-platform` PR #31.
- `yha9806/vulca-platform` PR #32.
- `yha9806/vulca-platform` PR #34.
- `yha9806/vulca-platform` PR #35.
- `yha9806/vulca-platform` PR #36.
- `yha9806/vulca-platform` PR #37.
- `yha9806/vulca-platform` PR #39.
- `yha9806/vulca-platform` PR #40.
- `yha9806/vulca-platform` PR #41.
- `yha9806/vulca-platform` PR #45.
