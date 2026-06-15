# Workspace Durable Review Fixtures

Vault status: protected durable-review reference.

This folder contains protected fixtures for RR3: the bounded durable Workspace
review path for the M3 demo.

The fixture is a durability contract, not a production storage implementation.
Product branches may implement it with a backend, database, local durable demo
store, or test fixture, but they must preserve the same review evidence,
blocker, decision-state, and human-audit boundaries.

## Product Implementation Status

As of 2026-06-15, the platform implementation is split into two protected PRs:

- PR #31, `[codex] Workspace review product shell`, is ready for review on
  `yha9806/vulca-platform` with head `codex/workspace-interactive-demo`.
  Its PR gate blocks on TypeScript, quiet ESLint, frontend unit tests, backend
  tests, backend coverage, and `tests/e2e/specs/workspace.spec.ts`.
- PR #32, `[codex] Durable workspace review persistence`, is a stacked draft
  on `codex/workspace-interactive-demo` with head
  `codex/vulca-workspace-durable-review`. It adds local durable review state,
  staged decision persistence, advisory-agent completion persistence, and the
  release-owner audit trail.

PR #32 is intentionally a local durability slice. It does not certify shared
production persistence or product-level release readiness.

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
- `docs/review-context/artifact-bridge/m3-demo-bridge-fixture.json`
- `yha9806/vulca-platform` PR #31.
- `yha9806/vulca-platform` PR #32.
