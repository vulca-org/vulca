# VULCA Workspace Current-State Audit

**Status:** Preview product audit
**Date:** 2026-06-15

VULCA Workspace is the product center for VULCA's broader system: a Creative
Repo surface where AI-native visual work can be reviewed, assigned, evidenced,
and blocked before public release.

This audit is source-backed from the local platform repository. The user-cited
baseline was:

- `6efef07 fix: align workspace context review controls`

The latest observed local Workspace state was:

- `/Users/yhryzy/.config/superpowers/worktrees/vulca-platform/workspace-interactive-demo`
- branch `master`
- head `5f4a666 feat: add manual upload intake workflow`

`6efef07` is treated as the context-review-control baseline. `5f4a666` is
treated as the latest observed local preview state.

## Product Thesis

The Workspace turns VULCA from an agent/MCP toolchain into a product surface:

```text
Creative Repo
  -> Review Inbox
  -> Single Asset Review
  -> Context Drawer
  -> Review Checks
  -> Decision Panel
  -> Release Gate
```

The SDK/MCP layer still owns execution: discovery, prompts, provider routing,
decomposition, redraw, inpaint, evaluation, artifacts, and case records. The
Workspace should organize those outputs into reviewable product objects.

## Current Implemented Surface

The latest observed Workspace preview includes:

- `WorkspaceShell`: session-local review workflow orchestration.
- `ReviewInbox`: triage queue with filters for all, my queue, blocked, needs
  changes, and waiting evidence.
- `NewReviewDialog`: frontend-only creation of review items, including manual
  upload metadata, brief text, source tool, work type, lifecycle stage, and
  initial owner.
- `SingleAssetReview`: asset-first review surface with version context,
  typed visual pins, manual upload intake strip, and visible release boundary.
- `ContextDrawer`: focused context panel for Brief, Evidence, History, and
  Manual.
- `ReviewChecksPanel`: grouped Visual QA, Cultural Review, and Release Review
  checks with human, agent, system, or external sources.
- `DecisionPanel`: owner/blocker controls, advisory agent review entrypoint,
  and decision actions.
- `WorkspaceManualPage`: explanation surface for product education; the
  primary `/workspace` surface stays operational.

## Product Objects Present In Code

The local Workspace content model includes:

- `CreativeRepo`
- `Brief`
- `MotifBranch`
- `VisualVariant`
- `ReviewRequest`
- `EvidencePack`
- `ReleaseGate`
- `AgentRun`
- `ReviewItem`
- `AssetVersion`
- `ReviewCheck`
- `ReviewPin`
- `ReviewIntake`

This matches the protected context vault's product model. The important
integration point is that the Workspace should not invent a second product
ontology; it should become the review surface for the SDK/MCP artifacts.

## Current Strengths

- The first screen is now operational review triage, not product explanation.
- Review items carry work type, lifecycle stage, typed review modes, owner,
  freshness, blockers, and current version.
- Evidence stays hidden until the reviewer asks for context.
- Agents are represented as advisory reviewers, not final approvers.
- `public_ready=false` is visible throughout the queue and review surface.
- Manual upload intake lets a user create a frontend-only review package with
  brief and asset metadata.
- The manual page carries product education and keeps the main review surface
  focused.

## Current Boundaries

The current Workspace is a preview surface, not a full production system.

- It is frontend/session-local in the observed branch.
- It does not yet persist Creative Repos to a backend.
- It does not yet ingest real SDK/MCP `AgentRun`, `EvidencePack`, or
  `ReleaseGate` artifacts directly.
- Manual upload records file metadata in the browser session; it is not real
  file storage.
- Agent findings are advisory and cannot set a public-release approval state.
- Human review remains required for release claims.

## Test Evidence

The observed Workspace test suite covers:

- default Review Triage entry state;
- frontend-only review creation;
- manual upload campaign review with brief and asset metadata;
- queue status updates after decisions;
- queue filters by operational status;
- current-blocker assignment controls;
- separation of manual/product education from the operational workspace;
- asset-first review surface with versions and decisions;
- typed visual pin filters;
- pin resolve/reopen state;
- review checks before decision actions;
- context drawer hidden until requested;
- agent checks as advisory and unable to approve release;
- `public_ready=false` invariant.

Primary source files:

- `wenxin-moyun/src/content/workspaceDemo.ts`
- `wenxin-moyun/src/components/workspace/WorkspaceShell.tsx`
- `wenxin-moyun/src/components/workspace/ReviewInbox.tsx`
- `wenxin-moyun/src/components/workspace/NewReviewDialog.tsx`
- `wenxin-moyun/src/components/workspace/SingleAssetReview.tsx`
- `wenxin-moyun/src/components/workspace/ContextDrawer.tsx`
- `wenxin-moyun/src/components/workspace/ReviewChecksPanel.tsx`
- `wenxin-moyun/src/components/workspace/DecisionPanel.tsx`
- `wenxin-moyun/src/__tests__/pages/WorkspacePage.test.tsx`
- `wenxin-moyun/src/__tests__/content/workspaceDemo.test.ts`

## Integration With VULCA Mainline

The main `vulca` repository should describe the relationship this way:

- VULCA SDK/MCP is the execution engine.
- VULCA Workspace is the product review surface.
- The website is the public trust and acquisition surface.
- PPT/deck work is an internal proof lab until quality gates pass.
- The protected context vault preserves long-lived project memory on
  `codex/vulca-context-vault`.

The README now exposes the Workspace direction without claiming that the
preview is a hosted production product.

## Recommended Next Milestones

### M1: Integration Spine

Write `docs/product/vulca-integration-spine.md` to make the product system
explicit:

- Workspace objects;
- SDK/MCP capabilities;
- website role;
- PPT proof-lab role;
- claim boundaries;
- release gates.

### M2: Artifact Bridge

Define how SDK/MCP outputs map into Workspace objects:

- `/visual-discovery`, `/visual-brainstorm`, `/visual-spec`, `/visual-plan`
  -> `Brief` and `MotifBranch`;
- generation/decompose/redraw/inpaint -> `VisualVariant` and `AgentRun`;
- evaluation and case records -> `EvidencePack`;
- claim/release blockers -> `ReleaseGate`.

### M3: Demo Path

Create one complete preview scenario:

```text
brief
  -> generated/imported visual
  -> agent review
  -> evidence pack
  -> human decision
  -> release remains blocked or internally approved
```

This should remain preview-gated until persistence, real artifact ingestion,
and human release workflow are implemented.

## Claim Boundary

Allowed:

- VULCA is moving toward a Workspace / Creative Repo product model.
- The observed Workspace preview implements review triage, asset review,
  evidence context, decision controls, and manual upload intake.
- The release boundary remains `public_ready=false`.

Not allowed without stronger evidence:

- Workspace is production-ready.
- Workspace persists real customer review workflows.
- Agent review can approve public release.
- VULCA replaces Figma, Canva, Adobe, Runway, FLORA, Krea, or similar tools.

## Sources

- Local platform worktree:
  `/Users/yhryzy/.config/superpowers/worktrees/vulca-platform/workspace-interactive-demo`
- User-cited baseline commit:
  `6efef07 fix: align workspace context review controls`
- Latest observed local preview commit:
  `5f4a666 feat: add manual upload intake workflow`
- Protected context vault:
  `codex/vulca-context-vault`
