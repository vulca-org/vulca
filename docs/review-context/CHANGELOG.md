# Review Context Changelog

Vault status: append-only change log.

## 2026-06-16

### Recorded Platform Review Revision Conflict And Audit Merge

- Recorded platform PR #36 as merged to `master` with revision metadata,
  optional `baseRevision` 409 conflict checks, and append-only save/clear audit
  events for the existing Workspace review-state compatibility endpoint.
- Clarified that #36 strengthens the DB-backed snapshot route from #35, but
  still does not complete full production persistence: authorization, typed
  object aggregates, release-owner audit semantics, operation-specific writes,
  and multi-instance acceptance evidence remain gated.
- Updated the source index, durable Workspace status, M5 closeout, release
  readiness gate, production persistence spec, and manifest so future sessions
  inherit the correct boundary.

Source basis:

- `yha9806/vulca-platform` PR #36.
- Merge commit `3310093131132268ec9658736d3bd172ecccbe58`.
- Remote checks: `Run Tests` and `security` passed on PR #36.

### Recorded Platform DB-Backed Workspace Review-State Merge

- Recorded platform PR #35 as merged to `master` with database-backed
  Workspace review-state compatibility persistence behind the existing
  `/api/v1/workspace/review-state/{repo_id}` endpoint.
- Clarified that #35 upgrades the #34 in-process store to a SQLAlchemy-backed
  snapshot table, but does not complete the full production persistence spec:
  authorization, conflict handling, typed object aggregates, append-only audit
  events, and multi-instance acceptance evidence remain gated.
- Updated the source index, durable Workspace status, M5 closeout, release
  readiness gate, and manifest so future sessions inherit the correct
  implementation boundary.

Source basis:

- `yha9806/vulca-platform` PR #35.
- Merge commit `24efaab5101494cfa7777aa3ded6d8c27e923870`.
- Remote checks: `Run Tests` and `security` passed on PR #35.

### Added Workspace Production Persistence Spec

- Added `15-workspace-production-persistence-spec.md` as the protected product
  design for database-backed Workspace persistence, authorization, conflict
  handling, audit history, and multi-instance behavior.
- Wired the spec into the README read order, manifest, validator, source index,
  Workspace product model, durable review status, release-readiness gate, and
  M5 closeout.
- Preserved the boundary that this spec does not upgrade product-level R5
  without implementation evidence and a human release owner decision.

Source basis:

- `docs/review-context/07-workspace-product-model.md`.
- `docs/review-context/14-release-readiness-evidence-gate.md`.
- `docs/review-context/release-readiness/M5-CLOSEOUT.md`.
- `yha9806/vulca-platform` PR #34.

### Recorded Platform Shared Workspace Review-State Merge

- Recorded platform PR #34 as merged to `master` with shared backend
  review-state API evidence for the Workspace page.
- Clarified that #34 is an in-process shared persistence slice, not
  production-grade database-backed, authorized, conflict-safe, or
  multi-instance Workspace persistence.
- Updated the M5 closeout, source index, manifest, and release-readiness gate
  so future sessions inherit the same status boundary.

Source basis:

- `yha9806/vulca-platform` PR #34.
- Merge commit `d06a713bf490ad870fe9273f933c310e2955b4e9`.
- Remote checks: `Run Tests` and `security` passed on PR #34.

## 2026-06-15

### Recorded Platform CI Hygiene Merge

- Recorded platform PR #33 as merged to `master` with Node 24-compatible
  GitHub Actions pins for checkout, setup-node, setup-python, and
  gitleaks-action.
- Recorded that #33 passed `Run Tests` and `security`; the deploy job remained
  skipped for the PR event.

Source basis:

- `yha9806/vulca-platform` PR #33.
- GitHub latest-release API checks for the upgraded actions on 2026-06-15.

### Recorded Platform PR And Protection Status

- Recorded platform PR #31 as merged to `master` with a Workspace-focused PR
  gate and legacy full E2E suite moved to manual advisory.
- Recorded platform PR #32 as merged to `master`, including local durable
  review state, staged decision persistence, advisory agent completion
  persistence, and release-owner audit trail scope.
- Clarified that these PRs improve R5 evidence but do not change product-level
  release readiness, which remains blocked.
- Recorded the GitHub protection limitation for the private
  `yha9806/vulca-platform` repository and the temporary no-direct-master
  operational rule until GitHub branch protection becomes available.

Source basis:

- `yha9806/vulca-platform` PR #31.
- `yha9806/vulca-platform` PR #32.
- GitHub ruleset/protection API checks on 2026-06-15.
- Local verification for `codex/vulca-workspace-durable-review`.

### Added M5 Closeout Summary

- Added `release-readiness/M5-CLOSEOUT.md` and
  `release-readiness/m5-closeout-summary.json` as the protected closeout index
  for RR1-RR5.
- Wired the closeout into the README read order, manifest, source index,
  release-readiness gate, validator, and vault tests.
- Preserved the boundary that current evidence supports R4 example-specific
  public copy only, while product-level R5 remains blocked.

Source basis:

- `docs/review-context/14-release-readiness-evidence-gate.md`.
- `docs/review-context/release-readiness/TEMPLATE.md`.
- `docs/review-context/artifact-bridge/m3-demo-bridge-fixture.json`.
- `docs/review-context/workspace-durable/m3-durable-review-fixture.json`.
- `docs/review-context/public-examples/m3-public-example-gate.json`.
- `docs/review-context/copy-gates/website-ppt-copy-gate.json`.

### Added Website And PPT Copy Gate

- Added `copy-gates/README.md` and
  `copy-gates/website-ppt-copy-gate.json` as the protected RR5 reference for
  website, README, PPT, and translation claim-level alignment.
- Wired the gate into the README read order, manifest, source index,
  website/PPT claim spine, release-readiness gate, validator, and vault tests.
- Preserved the boundary that translations cannot upgrade claim level and PPT
  proof-lab outputs remain bounded unless separately cleared.

Source basis:

- `docs/review-context/13-website-ppt-claim-spine.md`.
- `docs/review-context/14-release-readiness-evidence-gate.md`.
- `docs/review-context/public-examples/m3-public-example-gate.json`.

### Added Public Example Gate

- Added `public-examples/README.md` and
  `public-examples/m3-public-example-gate.json` as the protected RR4 reference
  for clearing one public example without upgrading product-level claims.
- Wired the gate into the README read order, manifest, source index,
  website/PPT claim spine, release-readiness gate, validator, and vault tests.
- Preserved the boundary that a public example decision is example-specific
  and cannot be reused for PPT proof-lab or product-level claims.

Source basis:

- `docs/review-context/12-complete-demo-path.md`.
- `docs/review-context/13-website-ppt-claim-spine.md`.
- `docs/review-context/14-release-readiness-evidence-gate.md`.
- `docs/review-context/workspace-durable/m3-durable-review-fixture.json`.

### Added Workspace Durable Review Fixture

- Added `workspace-durable/README.md` and
  `workspace-durable/m3-durable-review-fixture.json` as the protected RR3
  reference for reload-preserved Workspace review state.
- Wired the fixture into the README read order, manifest, source index,
  Workspace product model, demo path, release-readiness gate, validator, and
  vault tests.
- Preserved the boundary that agent/system checks cannot set public release
  state and human decision history must remain auditable.

Source basis:

- `docs/review-context/07-workspace-product-model.md`.
- `docs/review-context/12-complete-demo-path.md`.
- `docs/review-context/14-release-readiness-evidence-gate.md`.
- `docs/review-context/artifact-bridge/m3-demo-bridge-fixture.json`.

### Added M3 Bridge Fixture

- Added `artifact-bridge/README.md` and
  `artifact-bridge/m3-demo-bridge-fixture.json` as the protected RR2 reference
  fixture for projecting SDK/MCP artifacts into Workspace review objects.
- Wired the fixture into the README read order, manifest, source index,
  artifact bridge spec, complete demo path, release-readiness gate, validator,
  and vault tests.
- Preserved the boundary that missing evidence remains visible and public
  release remains blocked.

Source basis:

- `docs/review-context/11-artifact-bridge-spec.md`.
- `docs/review-context/12-complete-demo-path.md`.
- `docs/review-context/14-release-readiness-evidence-gate.md`.

### Added Release Readiness Report Template

- Added `release-readiness/README.md` and
  `release-readiness/TEMPLATE.md` as the protected RR1 checklist/report format
  for M5 release-readiness reviews.
- Wired the template into the README read order, manifest, source index,
  validator, and vault tests.
- Updated the M5 gate record so RR1 now points to the fixed report template.

Source basis:

- `docs/review-context/14-release-readiness-evidence-gate.md`.
- `docs/review-context/13-website-ppt-claim-spine.md`.
- `docs/review-context/09-claim-boundaries.md`.

### Added Release Readiness Evidence Gate

- Added `14-release-readiness-evidence-gate.md` as the protected M5 standard
  for upgrading preview/internal/public-blocked work toward release-ready
  claims.
- Wired the release gate into the README read order, manifest, source index,
  validator, and vault tests.
- Updated the integration spine and website/PPT claim spine so M5 points to the
  dedicated evidence-gate document.

Source basis:

- `docs/review-context/09-claim-boundaries.md`.
- `docs/review-context/10-integration-spine.md`.
- `docs/review-context/11-artifact-bridge-spec.md`.
- `docs/review-context/12-complete-demo-path.md`.
- `docs/review-context/13-website-ppt-claim-spine.md`.
- `docs/platform/release-readiness-status.md`.
- `origin/master:docs/product/workspace-current-state-audit.md`.

### Added Website And PPT Claim Spine

- Added `13-website-ppt-claim-spine.md` as the protected M4 standard for
  website, README-facing copy, public decks, and PPT proof-lab summaries.
- Wired the claim spine into the README read order, manifest, source index,
  validator, and vault tests.
- Updated the integration spine so M4 points to the dedicated claim-spine
  document and M5 becomes the next release-readiness milestone.

Source basis:

- `docs/review-context/08-website-and-ppt-boundaries.md`.
- `docs/review-context/09-claim-boundaries.md`.
- `docs/review-context/12-complete-demo-path.md`.
- Platform website content and homepage plans at commit `5dc32cd`.
- PPT proof lab source index entry and Run 2.93 public-blocked gate.

### Added Complete Demo Path Standard

- Added `12-complete-demo-path.md` as the protected M3 standard for one
  complete VULCA preview scenario from brief to evidence pack and release gate.
- Wired the demo path into the README read order, manifest, source index,
  validator, and vault tests.
- Updated the integration spine and artifact bridge spec so M3 points to the
  dedicated demo-path standard.

Source basis:

- `docs/review-context/10-integration-spine.md`.
- `docs/review-context/11-artifact-bridge-spec.md`.
- `origin/master:docs/product/workspace-current-state-audit.md`.
- Workspace `workspaceDemo.ts` object model.

### Added Artifact Bridge Specification

- Added `11-artifact-bridge-spec.md` as the protected M2 specification for
  mapping SDK/MCP outputs into Workspace objects.
- Wired the bridge spec into the README read order, manifest, source index,
  validator, and vault tests.
- Updated `10-integration-spine.md` so M2 points to the dedicated bridge spec
  and M3 becomes the next demo-path milestone.

Source basis:

- `src/vulca/mcp_server.py` MCP payloads.
- Learning Loop, decompose case, and layer-generate case schema specs.
- Workspace `workspaceDemo.ts` object model.
- `origin/master:docs/product/workspace-current-state-audit.md`.

### Added Integration Spine

- Added `10-integration-spine.md` as the routing layer across Workspace,
  SDK/MCP, website, PPT proof lab, and protected vault context.
- Updated the vault manifest, README read order, source index, and validator
  tests so future sessions can find and gate the integration spine.
- Recorded the `master` README alignment merge commit
  `cb6d52fe docs: surface VULCA Workspace product direction`.
- Updated Workspace source memory to distinguish the user-cited baseline
  `6efef07` from the latest observed local preview `5f4a666`.

Source basis:

- `origin/master` commit `cb6d52fe`.
- `origin/master:docs/product/workspace-current-state-audit.md`.
- Platform Workspace baseline `6efef07` and observed preview `5f4a666`.

### Confirmed Branch-Only Protection

- Recorded the human decision to keep the vault only on
  `codex/vulca-context-vault`.
- Added `PROTECTION.md` as the local record for GitHub rulesets, branch
  boundary, request workflow, and emergency bypass requirements.
- Scoped `.github/workflows/review-context.yml` to
  `codex/vulca-context-vault` only.
- Fixed governance ownership text to use the valid GitHub owner `@yha9806`.

Source basis:

- Human decision in the current session: option B, keep the vault only on
  `codex/vulca-context-vault`.
- Live GitHub rulesets verified through the GitHub API on 2026-06-15.

### Initialized Context Vault

- Created protected `docs/review-context/` structure on branch
  `codex/vulca-context-vault`.
- Recorded the core VULCA historical workstreams:
  image layering, decomposition, prompt control, visual skills,
  layer redraw, mask-aware routing, target-aware refinement, learning loop,
  Workspace product model, website, and PPT proof lab.
- Added governance rules requiring request packets for future modifications.
- Added local validation gate:
  `docs/review-context/gates/validate_review_context.py`.
- Added repository guardrails: CODEOWNERS path ownership, review-context CI, and
  validator tests.

Source basis:

- Current SDK/MCP mainline at `origin/master` commit `d6b8b559`.
- Workspace product branch at platform commit `6efef07`.
- Website film-led homepage branch at platform commit `5dc32cd`.
- PPT case-pack branch `codex/vulca-ppt-case-pack`, especially Run 2.93
  visual quality evaluation.
