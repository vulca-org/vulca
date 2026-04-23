---
name: visual-plan
description: "Turn a resolved design.md (from /visual-spec) into reviewable plan.md + run generate+evaluate loop → status {completed, partial, aborted}. Triggers: /visual-plan, '视觉 plan', '设计 execute'. Requires design.md status: resolved + Vulca checkout."
---

You are running `/visual-plan` — the third meta-skill in the `brainstorm → spec → plan → execute` pipeline. Your job: read a `design.md` at `docs/visual-specs/<slug>/` (produced by `/visual-spec` with `status: resolved`), derive a reviewable `plan.md` draft, walk the user through plan review, execute the generate+evaluate loop against the provider specified by `design.A.provider`, and finalize with terminal status + handoff string.

**In scope:** any `design.md` with `status: resolved` and `tradition` in the registry (or literal `null`), inside a Vulca checkout (`src/vulca/` present at cwd).
**Out of scope:** producing pixels outside Phase 3 (Err #8); multi-slug batch runs; modifying `design.md` (`/visual-plan` NEVER writes to `design.md` — S4 invariant).

**Tone:** decisive plan derivation + collaborative review gate + disciplined execution with per-iter audit.

## Phase 1 — Precondition gate + derivation + plan.md draft write

(filled in Task 6)

## Phase 2 — Plan-review loop

(filled in Task 6)

## Phase 3 — Execution loop

(filled in Task 6)

## Phase 4 — Finalize + optional hygiene

(filled in Task 6)

## References

- Design spec: `docs/superpowers/specs/2026-04-23-visual-plan-skill-design.md`
- Sibling skills: `.claude/skills/visual-brainstorm/SKILL.md` (v0.17.4), `.claude/skills/visual-spec/SKILL.md` (v0.17.5)
