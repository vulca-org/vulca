# Comparison Report

Status: baseline and Vulca case-pack decks generated; Gemini review and focused repair pass completed. Final scorecard and human approval remain pending.

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

## Vulca Case-Pack Artifacts

- Case pack: `docs/product/ppt-run1-ai-presentation-launch`
- Workspace: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca`
- Profile plan: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca/profile-plan.txt`
- Slide modules: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca/slides`
- PPTX: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca/output/ppt-run1-vulca.pptx`
- Contact sheet: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca/preview/contact-sheet.png`
- Layout JSON: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca/layout/final`
- Build manifest: `/Users/yhryzy/.codex/worktrees/031a/vulca/outputs/019e7f6e-bd46-7990-95b1-8ea3dcc98bb4/presentations/ppt-run1-vulca/output/artifact-build-manifest.json`

## Vulca Generation Notes

The Vulca deck was generated with the Presentations artifact-tool workflow from the full Run 1 case pack. It follows the 10-slide `deck_outline.json` sequence and uses one editable slide module per outline slide. The deck surfaces case-pack artifacts, source-use boundaries, design memory, deterministic code generation, layout QA, review-loop evidence, and product-decision evidence.

No external images, generated bitmap images, screenshots, copied reference visuals, copied layouts, brand marks, template files, or rasterized text were used. Essential text, proof objects, diagrams, matrices, status labels, and connectors are native editable PowerPoint shapes/text generated from artifact-tool slide modules.

## Initial Assessment

The prompt-only baseline is a usable comparison target: it communicates the high-level Vulca launch story, explains why ordinary prompt-generated slides are insufficient, and covers the requested ten-slide outline. Its visual system is intentionally generic product-launch styling, with simple cards, process blocks, and comparison panels rather than source-grounded design decisions.

Baseline comparison limitations:

- Commercial clarity: adequate for a first-pass product launch narrative, but not yet scored against the Run 1 rubric.
- Narrative flow: follows the requested outline from problem to closing; finer story evidence is pending final comparative scoring.
- Technical understandability: explains design memory, code generation, and review loop at a high level without deeper architecture proof.
- Visual hierarchy: automated layout QA passed with 0 errors and 0 warnings.
- Editability: generated with native text and shapes; no raster slide images or external assets were used.
- Reviewability: artifact-tool previews and layout JSON exist; Gemini review is recorded below, with final comparative scoring still pending.

Initial Vulca case-pack assessment:

- Commercial clarity: stronger buyer-problem framing because the deck exposes the source boundary, case-pack proof, editable output promise, and review gate.
- Narrative flow: follows the required progression from promise to product decision, with distinct proof surfaces for reference shift, workflow, design memory, code generation, review, comparison, and next primitive.
- Technical understandability: makes the workflow inspectable through visible files, slide modules, artifact outputs, layout JSON, and integrity checks rather than vague AI claims.
- Visual hierarchy: automated layout QA passed with 0 errors and 0 warnings, and the contact sheet shows a more varied slide rhythm than the baseline.
- Editability: generated with native editable text and shapes; no media entries were found in the PPTX package.
- Reviewability: case-pack deck artifacts passed Gemini critique intake, focused repair, layout QA, PPTX integrity, and the later human approval gate remains open.

## Gemini Review

- **Baseline commercial clarity:** Gemini read the baseline as a clear structured-creation value proposition that addresses prompt-to-slide cleanup backlog, but it remains a high-level product story.
- **Baseline visual hierarchy:** Gemini identified a legible five-stage workflow, design-memory concept, code-generation claim, and review loop; the hierarchy is adequate but less evidence-dense than the case-pack deck.
- **Baseline most important fix:** Make the repair-loop mechanism and design-memory ingestion more explicit. The target generation boundary remains artifact-tool native PPT output, not `python-pptx`.
- **Vulca commercial clarity:** Gemini read the Vulca deck as a sharper argument against prompt-only decks, with the case pack, source boundaries, code-first workflow, and QA evidence visible.
- **Vulca visual hierarchy:** Gemini recognized the ten-slide sequence from prompt-only failure to source rules, workflow, file inventory, code stack, review loop, benchmark, and product decision.
- **Vulca most important fix:** Clarify how Gemini critique maps back to target slide modules, repair actions, QA evidence, and the next product primitive decision.
- **Review conflict:** No visual conflict. One Gemini implementation hint suggested `python-pptx`, which is rejected because the Presentations workflow requires artifact-tool editable PPT generation.
- **Decision caveat:** Gemini is qualitative evidence, not final human approval.

## Focused Repair Pass

The repair pass changed two local Vulca slide modules under the generated output workspace:

- `slide-07.mjs`: replaced generic review-loop wording with structured issue fields, target module mapping, repair action, QA evidence, and human caveat.
- `slide-09.mjs`: replaced broad product-decision wording with converging evidence gates across rubric delta, Gemini risk, QA evidence, and human gate.

No external images, generated bitmap images, screenshots, copied reference visuals, brand marks, or media assets were added.

The first two rebuild QA runs caught slide 07 proof-object overlap after the repair text changed. The final rebuild passed layout QA with `0 error(s), 0 warning(s)`, passed PPTX zip integrity, and still contains no `ppt/media` entries.

## Comparison Status

The Vulca case-pack deck is available after Gemini review and a focused repair pass. Final rubric scores, product decision, public demo readiness, and human approval remain pending later Run 1 tasks.
