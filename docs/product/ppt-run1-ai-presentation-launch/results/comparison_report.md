# Comparison Report

Status: baseline and Vulca case-pack decks generated; Gemini review, focused repair pass, scorecard, and product primitive decision completed. Human approval remains pending before public publishing.

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

## Score Table

| Dimension | Baseline | Vulca | Evidence |
| --- | ---: | ---: | --- |
| Commercial clarity | 3 | 4 | Baseline states the cleanup-backlog problem, while Vulca adds the buyer problem, case-pack proof, editable output promise, and Gemini-recognized sharper prompt-only critique. |
| Narrative flow | 3 | 4 | Both decks follow the ten-slide outline, but Vulca uses source boundaries, workflow, design memory, review, comparison, and decision proof surfaces from `deck_outline.json` and the case pack. |
| Technical understandability | 3 | 4 | Baseline explains the architecture at a high level; Vulca shows visible files, slide modules, artifact outputs, layout JSON, and QA gates. |
| Visual hierarchy | 3 | 4 | Both final layout QA runs passed with `0 error(s), 0 warning(s)`, and Gemini recognized the Vulca sequence as more evidence-visible across workflow, code stack, review, and decision slides. |
| Brand coherence | 2 | 4 | Baseline uses generic launch styling; Vulca uses consistent style tokens, native system marks, proof-object bands, and a more coherent case-pack visual grammar. |
| Cultural/design intent | 2 | 4 | Vulca turns public references into original source-grounded rules in `design_memory.json`, `source_summaries.md`, and `tutorial_notes.md` without copying visuals or layouts. |
| Slide-to-slide consistency | 3 | 4 | Both decks render ten slides, but Vulca uses one reusable case style, repeated proof-object treatment, footer metadata, and outline-linked slide IDs. |
| Editability | 4 | 4 | Both decks use native text and shapes; Vulca adds stronger manifests and provenance evidence, but no manual PowerPoint edit inspection has been completed. |
| Accessibility | 3 | 4 | Layout QA found no hard overlaps after repair, and the final contact sheet shows clear labels and hierarchy; manual accessibility review is still pending. |
| Cross-platform rendering risk | 2 | 3 | Both PPTX files passed `unzip -t`, and Vulca has no `ppt/media` entries; however LibreOffice was unavailable and Keynote/Google Slides were not checked. |

Average score: baseline `2.8`, Vulca `3.9`, delta `+1.1`.

## Quality Gate Decision

- **Case-pack validation:** passed with `python3 scripts/validate_ppt_case_pack.py --profile run1 docs/product/ppt-run1-ai-presentation-launch`.
- **Baseline PPTX generation:** passed; baseline PPTX, previews, contact sheet, and layout JSON exist under the baseline output workspace.
- **Vulca PPTX generation:** passed; Vulca PPTX, previews, contact sheet, layout JSON, and build manifest exist under the Vulca output workspace.
- **Vulca hard layout errors:** passed after repair with `Checked 10 layout file(s): 0 error(s), 0 warning(s).`
- **PPTX integrity:** passed for both generated decks via `unzip -t`; both reported no compressed-data errors.
- **Renderer availability:** recorded as unavailable; artifact-tool preview and layout JSON were used for automated review.
- **Reference-analysis-only provenance:** passed; `asset_provenance.json` records no external, generated, copied, or embedded media assets.
- **Average score delta:** passed for Run 1 with Vulca ahead by `+1.1`, exceeding the one-point target.
- **Gemini narrative/design judgment:** passed as qualitative evidence; Gemini read Vulca as the sharper case-pack argument with stronger visible workflow evidence, while still requiring human approval.
- **Public publishing status:** blocked until human review and at least one real Office/cross-platform render or manual inspection pass.

## Product Primitive Decision

Selected next primitive: **renderer/cross-platform QA**.

Reason: Run 1 shows that the case-pack plus Gemini repair loop can beat the prompt-only baseline, but the weakest score remains cross-platform rendering risk because LibreOffice was unavailable and PowerPoint, Keynote, and Google Slides behavior were not inspected. Public claims should not depend only on artifact-tool previews and zip integrity.

Next implementation question: what is the smallest reliable QA adapter that can render or inspect generated PPTX output across Microsoft PowerPoint 365 first, then Keynote or Google Slides, without making generated binary artifacts part of the committed case pack?

## Comparison Status

The Vulca case-pack deck is available after Gemini review, focused repair, and scoring. It is ready for an internal demo-video draft, but public publishing remains blocked until human approval and cross-platform inspection.
