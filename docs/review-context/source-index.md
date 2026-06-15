# Source Index

Vault status: source references.

This file anchors vault claims to concrete repository evidence. It is not an
exhaustive bibliography; it is the minimum evidence map a future session should
check before changing high-level VULCA claims.

## SDK / MCP Mainline

- `README.md`
  - Product thesis: fuzzy visual intent to controlled creative production.
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

## Workspace Product

Workspace product code lives in the separate `vulca-platform` repository.

- Branch: `master` in
  `/Users/yhryzy/.config/superpowers/worktrees/vulca-platform/workspace-interactive-demo`
- Commit: `6efef07 fix: align workspace context review controls`
- Important files:
  - `wenxin-moyun/src/content/workspaceDemo.ts`
  - `wenxin-moyun/src/components/workspace/`
  - `wenxin-moyun/src/pages/WorkspacePage.tsx`
  - `wenxin-moyun/src/pages/WorkspaceManualPage.tsx`
  - `docs/superpowers/specs/2026-06-14-vulca-three-layer-review-workspace-design.md`
  - `docs/superpowers/specs/2026-06-15-vulca-creative-pr-typed-review-modes-design.md`
- Verified in prior session:
  - `npm test -- src/__tests__/content/workspaceDemo.test.ts src/__tests__/pages/WorkspacePage.test.tsx src/__tests__/config/seo.test.ts`
  - Result: 29 passed.
  - `npm run type-check`
  - Result: passed.

## Website

Website code lives in the separate `vulca-platform` repository.

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
