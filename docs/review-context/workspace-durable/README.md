# Workspace Durable Review Fixtures

Vault status: protected durable-review reference.

This folder contains protected fixtures for RR3: the bounded durable Workspace
review path for the M3 demo.

The fixture is a durability contract, not a production storage implementation.
Product branches may implement it with a backend, database, local durable demo
store, or test fixture, but they must preserve the same review evidence,
blocker, decision-state, and human-audit boundaries.

## Product Implementation Status

As of 2026-06-16, the platform implementation has ten merged PRs on
`yha9806/vulca-platform` `master`:

- PR #31, `[codex] Workspace review product shell`, merged at
  `6810e67ca967a47782b5d9f83d751148d1eb6d26`. Its PR gate blocked on
  TypeScript, quiet ESLint, frontend unit tests, backend tests, backend
  coverage, and `tests/e2e/specs/workspace.spec.ts`.
- PR #32, `[codex] Durable workspace review persistence`, merged at
  `61da8e9f296b7c1e66f61720e487e8e42d4eb6ce`. It adds local durable review
  state, staged decision persistence, advisory-agent completion persistence,
  and the release-owner audit trail.
- PR #34, `[codex] Shared Workspace review persistence`, merged at
  `d06a713bf490ad870fe9273f933c310e2955b4e9`. It adds
  `/api/v1/workspace/review-state/{repo_id}`, frontend load/save mirroring for
  the Workspace page, backend-side `public_ready=false` normalization, and
  E2E isolation for the shared review-state API.
- PR #35, `feat: persist workspace review state in db`, merged at
  `24efaab5101494cfa7777aa3ded6d8c27e923870`. It adds a SQLAlchemy
  `workspace_review_states` table behind the existing compatibility endpoint,
  preserves backend-side release gate normalization, and adds SQLite-backed
  tests for cross-client persistence, process-local reset survival, table
  registration, and clearing.
- PR #36, `feat: add workspace review revision conflicts`, merged at
  `3310093131132268ec9658736d3bd172ecccbe58`. It adds revision metadata,
  optional `baseRevision` 409 conflict checks, stale-after-clear protection,
  row locking on write/delete paths, append-only save/clear audit events, and
  an Alembic migration for the audit table.
- PR #37, `feat: gate workspace review actors`, merged at
  `0faf8748181c4d65f83b22b9a0b6ecfb10409b14`. It adds a trusted actor/role
  gate for the compatibility endpoint, production fail-closed save/clear
  behavior without a trusted upstream actor secret, clear restricted to
  `release_owner`, `repo_owner`, or `system`, audit metadata for actor id and
  role, and deployment notes for `WORKSPACE_REVIEW_ACTOR_HEADER_SECRET`.
- PR #39, `feat: add workspace review memberships`, merged at
  `dff2331f95161ec909a07b76ef7e94ae7def3cfe`. It adds the
  `workspace_review_memberships` table and requires production save/clear
  operations on the compatibility endpoint to match an active repo membership
  for the trusted actor id and role.
- PR #40, `feat: gate workspace review reads`, merged at
  `d31e9bf8f6139c60ee10605337c32221a5098b8b`. It extends the same trusted
  actor and active membership checks to production load operations, so
  load/save/clear all fail closed without a trusted actor and matching active
  membership.
- PR #41, `feat: add workspace membership admin routes`, merged at
  `becbb072434bd4e0d9241e11a87717c7891926b5`. It adds trusted `system` actor
  routes to provision and deactivate Workspace review memberships on the
  compatibility surface, including role validation, deactivate-with-history,
  stable error responses, membership admin audit events, and deployment notes.
- PR #45, `feat: add workspace typed production core`, merged at
  `530ecb8fc80a93756f96cba75ecdd9991bcb8db4`. It adds typed Workspace core
  tables behind the existing compatibility route, bounded typed sync from
  compatibility snapshots, typed overlay load, archive/reactivate lifecycle,
  typed audit events, rollback/conflict gates, idempotency and stale-child
  cleanup tests, production membership integration, OpenAPI stability, and
  README boundary notes.

PR #32 is intentionally a local durability slice. PR #34 is intentionally a
shared in-process backend slice. PR #35 upgrades that compatibility route to
database-backed snapshot persistence. PR #36 adds compatibility-route revision
conflict checks and snapshot audit events. PR #37 adds a trusted-header actor
gate for that compatibility route. PR #39 adds an active-membership check for
production save/clear on that same route. PR #40 extends that check to
production load. PR #41 adds system-only provisioning/deactivation for the
membership rows used by those gates. PR #45 adds the first typed core
foundation behind that compatibility route. Together they improve Workspace
persistence and compatibility-route authorization evidence, but they do not
certify the full production model: user/JWT identity, end-user or repo-owner
self-service membership management UI, operation-specific frontend writes,
real SDK/MCP artifact ingestion into typed records, release-owner human
workflow semantics, multi-instance acceptance, ingress header-stripping proof,
or product-level release readiness.

Use `../15-workspace-production-persistence-spec.md` for the product design
that turns these slices into the full production persistence model.

## Current Fixtures

- `m3-durable-review-fixture.json`: RR3 reference fixture showing the M3
  review item, EvidencePack, blocker, decision state, release gate, and human
  decision history surviving reload.

## Rules

- Reload must preserve the review item.
- Reload must preserve the EvidencePack and its source refs.
- Reload must preserve blockers and decision state.
- Agent/system checks cannot set public release state.
- Human decision history must be auditable.
- This fixture does not certify product release readiness by itself.

## Sources

- `docs/review-context/07-workspace-product-model.md`
- `docs/review-context/12-complete-demo-path.md`
- `docs/review-context/14-release-readiness-evidence-gate.md`
- `docs/review-context/15-workspace-production-persistence-spec.md`
- `docs/review-context/artifact-bridge/m3-demo-bridge-fixture.json`
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
