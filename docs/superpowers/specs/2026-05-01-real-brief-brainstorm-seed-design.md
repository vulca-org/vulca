# Real Brief Brainstorm Seed Design

## Goal

Convert a Phase 2 real-brief workflow seed into a draft `/visual-brainstorm` proposal so real commercial briefs can enter the existing `proposal.md -> design.md -> plan.md -> evaluate` chain without bypassing the human gate.

## Scope

This phase adds an offline proposal seeding step for supported static visual domains. It reads `docs/visual-specs/<slug>/workflow_seed.md`, `real_brief/structured_brief.json`, and `real_brief/workflow_handoff.json`, then writes `docs/visual-specs/<slug>/proposal.md` with `status: draft`.

It does not finalize the proposal, invoke image providers, run `/visual-spec`, or judge image quality.

## Approach

Add a focused Python module under `vulca.real_brief` that owns the mapping from real brief fields to the existing `/visual-brainstorm` proposal schema. Add a small CLI wrapper for repeatable local use and tests. Update the skill text so an agent running `/visual-brainstorm <slug>` checks for a real-brief seed and uses the seeded proposal as the first draft instead of starting from an empty question loop.

## Behavior

- Supported domains remain the same as the Phase 2 adapter: `poster`, `packaging`, `brand_visual`, `illustration`, `editorial_cover`, `photography_brief`, and `hero_visual_for_ui`.
- Unsupported workflow seeds are refused with a clear error.
- Existing `proposal.md` with `status: ready` is never overwritten.
- Existing draft proposal requires an explicit `force=True` or CLI `--force`.
- The generated proposal keeps exactly the eight frontmatter fields required by `/visual-brainstorm`.
- `style_treatment` defaults to `unified` unless the real brief handoff later supplies a stricter value.
- `tradition` is YAML `null`; this keeps the cultural rubric honest until a human declares a tradition.
- The proposal includes the copied real brief source, deliverables, constraints, risks, and open questions so the user can review it inline before approving.

## Testing

Tests cover supported proposal generation, overwrite gates, unsupported seed refusal, CLI dry-run/write behavior, and secret leakage checks. Existing Phase 2 adapter and visual discovery tests must continue passing.
