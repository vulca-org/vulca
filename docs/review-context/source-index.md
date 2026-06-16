# Source Index

Vault status: source references.

This file anchors vault claims to concrete repository evidence. It is not an
exhaustive bibliography; it is the minimum evidence map a future session should
check before changing high-level VULCA claims.

## SDK / MCP Mainline

- Mainline reference:
  - `origin/master` commit `cb6d52fe docs: surface VULCA Workspace product
    direction`
  - Public README now includes the Workspace product direction and links to
    `docs/product/workspace-current-state-audit.md` on `master`.
- `README.md`
  - Product thesis: fuzzy visual intent to controlled creative production.
  - Workspace framing: SDK/MCP is the execution layer; Workspace is the
    Creative Repo review surface.
  - Workflow: discovery, brainstorm, spec, plan, generate, decompose, edit,
    evaluate, archive.
  - Decompose and layer-edit examples.
- `CHANGELOG.md`
  - v0.17.14 native mask inpaint, `layers_redraw`, `layers_paste_back`.
  - v0.18 redraw default flip and multi-instance split.
  - v0.20 mask-aware redraw routing.
  - v0.21 redraw recontract.
  - v0.22 target-aware mask refinement.
  - v0.23 provider SDKs, visual workflow skills, telemetry and platform work.
- `src/vulca/mcp_server.py`
  - MCP tool surface.
- `src/vulca/layers/`
  - Layering, decompose, prompt, redraw, mask refinement, pasteback, composite.
- `src/vulca/providers/`
  - OpenAI, Gemini, ComfyUI, mock, retry, and capability behavior.
- `.claude/skills/` and `.agents/skills/`
  - User-facing visual workflow skills.

## Layering And Decompose

- `docs/superpowers/specs/2026-04-08-layers-redesign-design.md`
  - Dual-path layer architecture: generated layered output vs external-image
    split path.
- `docs/agent-native-workflow.md`
  - Agent-native plan/manifest contract, residual quality signal, rescue
    patterns.
- `docs/superpowers/specs/2026-05-05-decompose-case-design.md`
  - `decompose_case` learning schema.
- Tests:
  - `tests/test_layers_v2_split.py`
  - `tests/test_decompose_cases.py`
  - `tests/test_mcp_layers_decompose_case.py`

## Prompt Control And Visual Skills

- `docs/superpowers/specs/2026-04-11-prompt-engineering-experiment-design.md`
  - English-first prompt rescue, negative prompt controls, SDXL subject fidelity.
- `docs/superpowers/specs/2026-04-21-visual-brainstorm-skill-design.md`
  - `proposal.md`, scope, L1-L5 rubric.
- `docs/superpowers/specs/2026-04-21-visual-spec-skill-design.md`
  - `design.md`, prompt derivation, source confidence.
- `docs/superpowers/specs/2026-04-23-visual-plan-skill-design.md`
  - `plan.md`, execution loop, gates.
- Tests:
  - `tests/test_prompting.py`
  - `tests/test_visual_plan_execution_loop.py`
  - `tests/test_visual_spec_schema_invariants.py`
  - `tests/test_visual_brainstorm_discovery_integration.py`

## Redraw, Mask, Pasteback

- `docs/superpowers/specs/2026-04-26-v0.18-layers-redraw-split-design.md`
  - Safer `layers_redraw` defaults and multi-instance `layers_split`.
- `docs/superpowers/specs/2026-04-27-v0.20-mask-aware-redraw-routing-design.md`
  - Sparse-alpha drift diagnosis and mask-aware routing.
- `docs/superpowers/specs/2026-04-30-v0.22-target-aware-mask-refinement-design.md`
  - Target-aware child mask refinement.
- `docs/superpowers/specs/2026-05-05-vulca-learning-loop-v0-design.md`
  - `redraw_case` logging and failure taxonomy.
- Tests:
  - `tests/test_layers_redraw.py`
  - `tests/test_layers_redraw_mask_aware.py`
  - `tests/test_layers_redraw_crop_pipeline.py`
  - `tests/test_layers_redraw_quality_gates.py`
  - `tests/test_mask_refine.py`
  - `tests/test_paste_back.py`

## Product Positioning

- `docs/product/2026-04-30-product-positioning-brief.md`
  - Agent-native visual control layer.
- `docs/product/roadmap.md`
  - Current, next, in parallel, later, non-goals.
- `docs/product/provider-capabilities.md`
  - Agent surfaces and provider capability matrix.
- `docs/platform/release-readiness-status.md`
  - Public claim boundaries and manual gates.
- `docs/review-context/14-release-readiness-evidence-gate.md`
  - Protected M5 release-readiness gate for Workspace persistence, artifact
    ingestion, evidence rendering, human release workflow, public examples,
    and website/PPT copy review.
- `docs/review-context/15-workspace-production-persistence-spec.md`
  - Protected product spec for production Workspace database persistence,
    authorization, conflict handling, audit history, and multi-instance
    behavior.
- `docs/review-context/release-readiness/TEMPLATE.md`
  - Protected RR1 report template for recording evidence links, reviewer/owner
    fields, Gate 1-6 status, and release decisions.

## Artifact Bridge

- `docs/review-context/11-artifact-bridge-spec.md`
  - Protected bridge spec for SDK/MCP outputs entering Workspace review.
- `docs/review-context/artifact-bridge/m3-demo-bridge-fixture.json`
  - Protected RR2 fixture showing a generated key visual and layer split
    projected into Workspace objects with missing evidence visible.
- `docs/review-context/12-complete-demo-path.md`
  - Protected M3 standard for the brief-to-evidence-to-release-gate preview
    scenario.
- `src/vulca/mcp_server.py`
  - `generate_image` returns `image_path`, cost, latency, provider, MIME, and
    provider metadata.
  - `layers_split` returns manifest path, layers, split mode, optional
    detection report, optional palette debug paths, and optional case logging
    fields.
  - `layers_redraw` returns redrawn layer path, source pasteback path,
    advisory fields, and optional `redraw_case` logging fields.
  - `evaluate_artwork` returns score, dimensions, rationales,
    recommendations, deviation types, risk flags, and risk level.
- Case schema specs:
  - `docs/superpowers/specs/2026-05-05-vulca-learning-loop-v0-design.md`
  - `docs/superpowers/specs/2026-05-05-decompose-case-design.md`
  - `docs/superpowers/specs/2026-05-05-layer-generate-case-design.md`
- Workspace source:
  - `/Users/yhryzy/.config/superpowers/worktrees/vulca-platform/workspace-interactive-demo/wenxin-moyun/src/content/workspaceDemo.ts`
  - Defines `Brief`, `MotifBranch`, `VisualVariant`, `AgentRun`,
    `EvidencePack`, `ReviewRequest`, `ReviewItem`, `ReviewCheck`,
    `ReviewIntake`, and `ReleaseGate`.
- Durable review fixture:
  - `docs/review-context/workspace-durable/m3-durable-review-fixture.json`
  - Protected RR3 reference for reload-preserved review item, EvidencePack,
    release blockers, decision state, and human decision history.
  - Platform PR #34 adds shared in-process backend review-state API evidence
    for the Workspace page, while production persistence remains gated.
  - Platform PR #35 upgrades the compatibility review-state endpoint to a
    SQLAlchemy-backed `workspace_review_states` table, while full production
    authorization, conflict handling, typed aggregates, append-only audit
    events, and multi-instance acceptance remain gated.
  - Platform PR #36 adds revision metadata, optional `baseRevision` stale-write
    409 checks, and append-only save/clear audit events for that compatibility
    snapshot route, while authorization, typed aggregates, release-owner audit
    semantics, operation-specific writes, and multi-instance acceptance remain
    gated.
  - Platform PR #37 adds a trusted actor/role gate for the same compatibility
    route, including production fail-closed save/clear behavior without
    trusted upstream headers, clear restricted to `release_owner`,
    `repo_owner`, or `system`, and actor metadata in audit events. Full
    user/JWT identity, repo membership, typed aggregates, release-owner human
    semantics, operation-specific writes, ingress header stripping, and
    multi-instance acceptance remain gated.
  - Platform PR #39 adds `workspace_review_memberships` and requires
    production save/clear operations on the compatibility route to match an
    active repo membership for the trusted actor id and role. Full user/JWT
    identity, read authorization, membership management APIs/UI, typed
    aggregates, release-owner human semantics, operation-specific writes,
    ingress header stripping, and multi-instance acceptance remain gated.
- Public example gate:
  - `docs/review-context/public-examples/m3-public-example-gate.json`
  - Protected RR4 reference for one example-specific public artifact and copy
    scope.
- Website/PPT copy gate:
  - `docs/review-context/copy-gates/website-ppt-copy-gate.json`
  - Protected RR5 reference for website, README, PPT, and translation
    claim-level alignment.
- M5 closeout:
  - `docs/review-context/release-readiness/m5-closeout-summary.json`
  - Current release-readiness index and product-level release boundary.
- Workspace production persistence spec:
  - `docs/review-context/15-workspace-production-persistence-spec.md`
  - Product design for database-backed persistence, authorization, revision
    conflicts, audit history, and multi-instance behavior.

## Workspace Product

Workspace product code lives in the separate `vulca-platform` repository.

- Branch: `master` in
  `/Users/yhryzy/.config/superpowers/worktrees/vulca-platform/workspace-interactive-demo`
- Context baseline: `6efef07 fix: align workspace context review controls`
- Latest merged platform master:
  `dff2331f95161ec909a07b76ef7e94ae7def3cfe` from PR #39,
  `feat: add workspace review memberships`.
- Important files:
  - `wenxin-moyun/src/content/workspaceDemo.ts`
  - `wenxin-moyun/src/components/workspace/`
  - `wenxin-moyun/src/pages/WorkspacePage.tsx`
  - `wenxin-moyun/src/pages/WorkspaceManualPage.tsx`
  - `wenxin-backend/app/api/v1/workspace_review_state.py`
  - `wenxin-moyun/src/services/workspaceDurableReviewStore.ts`
  - `docs/superpowers/specs/2026-06-14-vulca-three-layer-review-workspace-design.md`
  - `docs/superpowers/specs/2026-06-15-vulca-creative-pr-typed-review-modes-design.md`
- Verified in prior session:
  - `npm test -- src/__tests__/content/workspaceDemo.test.ts src/__tests__/pages/WorkspacePage.test.tsx src/__tests__/config/seo.test.ts`
  - Result: 29 passed.
  - `npm run type-check`
  - Result: passed.
- Mainline audit:
  - `origin/master:docs/product/workspace-current-state-audit.md`
  - Merge commit: `cb6d52fe docs: surface VULCA Workspace product direction`
- Shared review-state merge:
  - `yha9806/vulca-platform` PR #34.
  - Merge commit: `d06a713bf490ad870fe9273f933c310e2955b4e9`.
  - Boundary: in-process shared backend state only; not production
    database-backed, authorized, conflict-safe, or multi-instance persistence.
- DB-backed review-state compatibility merge:
  - `yha9806/vulca-platform` PR #35.
  - Merge commit: `24efaab5101494cfa7777aa3ded6d8c27e923870`.
  - Evidence: SQLAlchemy `WorkspaceReviewState` model, existing
    `/api/v1/workspace/review-state/{repo_id}` API backed by DB persistence,
    backend-side `public_ready=false` normalization retained, and tests for
    cross-client load, process-local reset survival, table registration, clear,
    OpenAPI contract, and DB dependency fallback.
  - Boundary: compatibility snapshot persistence only; not full typed
    CreativeRepo/ReviewItem/EvidencePack/ReleaseGate persistence, not
    authorization, not stale-write conflict handling, not append-only audit
    events, and not multi-instance acceptance evidence.
- Revision conflict and audit compatibility merge:
  - `yha9806/vulca-platform` PR #36.
  - Merge commit: `3310093131132268ec9658736d3bd172ecccbe58`.
  - Evidence: `revision` returned by the existing review-state API,
    optional wrapped payloads with `baseRevision`, stale-write 409 responses,
    stale-after-clear 409 responses, row locking on write/delete paths,
    append-only `workspace_review_audit_events` save/clear records, and an
    Alembic migration for the audit table.
  - Boundary: compatibility snapshot conflict/audit only; not authorization,
    not typed CreativeRepo/ReviewItem/EvidencePack/ReleaseGate aggregates, not
    operation-specific frontend writes, not release-owner audit semantics, and
    not multi-instance acceptance evidence.
- Trusted actor gate compatibility merge:
  - `yha9806/vulca-platform` PR #37.
  - Merge commit: `0faf8748181c4d65f83b22b9a0b6ecfb10409b14`.
  - Evidence: `WorkspaceReviewActor` header dependency, stable 403 permission
    responses, development/test `preview` compatibility, production save/clear
    fail-closed unless trusted upstream actor headers carry a 32+ character
    `WORKSPACE_REVIEW_ACTOR_HEADER_SECRET`, clear restricted to
    `release_owner`, `repo_owner`, or `system`, save/clear audit metadata with
    `actor_id` and `actor_role`, README/env deployment notes, and Workspace
    E2E reset isolation updated to use a release-owner actor.
  - Boundary: compatibility route trusted-header gate only; not full
    user/JWT authentication, not repo membership authorization, not typed
    CreativeRepo/ReviewItem/EvidencePack/ReleaseGate aggregates, not
    operation-specific frontend writes, not release-owner human audit
    semantics, and not ingress/gateway header-stripping proof.
- Workspace membership gate compatibility merge:
  - `yha9806/vulca-platform` PR #39.
  - Merge commit: `dff2331f95161ec909a07b76ef7e94ae7def3cfe`.
  - Evidence: SQLAlchemy `WorkspaceReviewMembership` model, Alembic migration
    for `workspace_review_memberships`, active membership lookup by repo and
    trusted actor id, role-mismatch 403 responses, production save/clear
    membership enforcement, README deployment notes, and tests for non-member,
    inactive member, role mismatch, OpenAPI contract, and DB dependency
    fallback.
  - Boundary: compatibility-route save/clear membership gate only; not full
    user/JWT authentication, not read authorization, not membership management
    APIs/UI, not typed CreativeRepo/ReviewItem/EvidencePack/ReleaseGate
    aggregates, not operation-specific frontend writes, not release-owner human
    audit semantics, not ingress/gateway header-stripping proof, and not
    multi-instance acceptance evidence.
- Production persistence design:
  - `docs/review-context/15-workspace-production-persistence-spec.md`.
  - This is the next product-layer design reference before changing the
    platform database, permissions, conflict, or audit model.

## Website

Website code lives in the separate `vulca-platform` repository.

- Claim spine:
  - `docs/review-context/13-website-ppt-claim-spine.md`
  - Shared public-story standard for website, README-facing copy, PPT, and
    internal proof-lab summaries.
- Branch: `codex/vulcaart-film-led-homepage`
- Commit: `5dc32cd docs: plan flora-method homepage redesign`
- Important files:
  - `wenxin-moyun/src/content/homeCommercial.ts`
  - `wenxin-moyun/src/components/home/HeroDemoStage.tsx`
  - `wenxin-moyun/src/components/home/HomeHero.tsx`
  - `docs/superpowers/plans/2026-06-13-vulcaart-film-led-homepage.md`
  - `docs/superpowers/plans/2026-06-14-vulcaart-flora-method-homepage-redesign.md`
- Verified in prior session:
  - homepage unit tests: 10 passed.
  - type-check: passed.

## PPT Proof Lab

- Claim spine:
  - `docs/review-context/13-website-ppt-claim-spine.md`
  - Defines how PPT proof-lab material can support public story only when
    labeled internal, preview-gated, or public blocked as appropriate.
- Branch: `codex/vulca-ppt-case-pack`
- Important files:
  - `docs/product/ppt-case-pack-v1/`
  - `docs/product/ppt-run1-ai-presentation-launch/`
  - `docs/product/ppt-run1-5-product-lab/`
  - `docs/product/ppt-run2-data-skill-quality/`
  - `docs/product/ppt-parallel-usecase-pilots/`
- Latest important gate:
  - `docs/product/ppt-run2-data-skill-quality/results/run2_93_visual_quality_evaluation.md`
  - Status: `run2_93_visual_quality_evaluation_public_blocked`.
