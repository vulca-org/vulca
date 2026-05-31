# Comparison Report

Status: baseline generated; Vulca case-pack deck not generated yet.

## Baseline Artifacts

- Prompt: `docs/product/ppt-run1-ai-presentation-launch/baseline_prompt.md`
- Workspace: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f5a-f178-7ad2-a29c-44053c67cc0d/presentations/ppt-run1-baseline`
- Slide modules: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f5a-f178-7ad2-a29c-44053c67cc0d/presentations/ppt-run1-baseline/slides`
- PPTX: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f5a-f178-7ad2-a29c-44053c67cc0d/presentations/ppt-run1-baseline/output/ppt-run1-baseline.pptx`
- Contact sheet: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f5a-f178-7ad2-a29c-44053c67cc0d/presentations/ppt-run1-baseline/preview/contact-sheet.png`
- Layout JSON: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f5a-f178-7ad2-a29c-44053c67cc0d/presentations/ppt-run1-baseline/layout/final`

## Baseline Generation Notes

The baseline deck was generated from `baseline_prompt.md` only. It does not use the Vulca case-pack rules, source registry, design memory, slide patterns, style tokens, generation brief, Gemini, image generation, or external/generated image assets.

The deck contains exactly 10 editable artifact-tool slide modules using native text and shapes. Artifact-tool export produced the PPTX, per-slide previews, contact sheet, build manifest, and layout JSON.

## Initial Assessment

The prompt-only baseline is a usable comparison target: it communicates the high-level Vulca launch story, explains why ordinary prompt-generated slides are insufficient, and covers the requested ten-slide outline. Its visual system is intentionally generic product-launch styling, with simple cards, process blocks, and comparison panels rather than source-grounded design decisions.

Expected comparison limitations:

- Commercial clarity: adequate for a first-pass product launch narrative, but not yet scored against the Run 1 rubric.
- Narrative flow: follows the requested outline from problem to closing; finer story evidence is pending the Vulca case-pack deck.
- Technical understandability: explains design memory, code generation, and review loop at a high level without deeper architecture proof.
- Visual hierarchy: automated layout QA passed with 0 errors and 0 warnings after repair.
- Editability: generated with native text and shapes; no raster slide images or external assets were used.
- Reviewability: artifact-tool previews and layout JSON exist; Gemini review and final comparative scoring are pending later tasks.

## Comparison Status

The Vulca case-pack deck, Gemini review, rubric scores, product decision, and demo readiness decision are not available yet. This report should be extended after the case-pack deck and review artifacts are generated.
