---
slug: 2026-04-28-ipad-cartoon-roadside-direct-showcase
status: ready
domain: brand_visual
tradition: null
style_treatment: unified
generated_by: visual-brainstorm@0.1.0
created: 2026-04-28
updated: 2026-04-28
---

# IMG_6847 Direct iPad-Cartoon Showcase

> Direct-showcase branch created after v0.20.1 layered redraw produced poor visuals. This branch intentionally follows the Scottish showcase pattern: lock intent and prompt first, then run one direct image edit/generation path.

## Intent

Create a clean showcase image from `source/IMG_6847.jpg` using Vulca's front-loaded planning value: constrain the subject, style, preserved anchors, and failure modes before pixel generation. This is not a decompose-plus-redraw proof. It is a marketing-quality direct visual meant to test whether prompt planning alone produces a stronger hero image than the v0.20.1 sparse-layer redraw path.

## Audience

Design-curious creators, AI image workflow builders, and Vulca evaluators comparing "structured prompt planning" against naive image prompting and against fragile layer redraw.

## Physical Form

Single 4:3 hero image plus audit trail:
- source copy: `source/IMG_6847.jpg`
- generated image: `iters/1/`
- execution log: `execution_log.md`
- proposal/design/plan markdown records

## Market

Bilingual-ready social/demo material. No on-image explanatory text required.

## Budget And Deadline

One primary OpenAI image call, with one fallback call allowed only if the first call fails due model contract. Keep total under two real image calls.

## Color Constraints

iPad Procreate-style vivid pastel palette, soft rounded outlines, clean flat shading, sunny roadside color mood. Avoid pale white block fill, cream masks, large flat blank areas, photorealistic texture, muddy green/brown drift, and global low-contrast wash.

## References

- `source/IMG_6847.jpg` copied byte-for-byte from the prior iPad roadside slug.
- Prior failure evidence: `2026-04-27-ipad-cartoon-roadside` v0.20.1 layered redraw artifacts.
- Positive prior pattern: Scottish showcase prompt-planning path.

## Series Plan

none

## Acceptance Rubric

none

## Questions Resolved

- Q: Should this use decompose plus redraw?
  A: No. This branch is a direct-showcase run, explicitly modeled on the Scottish showcase path.
- Q: What is the product claim?
  A: Vulca improves model controllability by structured intent/prompt planning before generation.
- Q: What should the image look like?
  A: A coherent iPad/Procreate cartoon illustration of the same roadside scene, not pasted sparse-layer artifacts.
- Q: What is the failure threshold?
  A: Reject if it shows large white blocks, obvious mask seams, muddy layer drift, or loses the roadside composition.

## Open Questions

none

## Notes

Superpowers execution note: user explicitly requested a run with results recorded. This artifact is the reviewable brief for that run. Verification-before-completion applies before claiming the result exists or is usable.
