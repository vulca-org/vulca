# Comparison Report

**Status:** baseline-and-case-pack-generated

## Baseline

- Status: generated
- Source: `docs/product/ppt-case-pack-v1/baseline_prompt.md`
- PPTX path: `outputs/019e7ed2-6e44-7140-8ed1-d2ad117e97da/presentations/vulca-ppt-baseline/output/vulca-prompt-baseline.pptx`
- Contact sheet path: `outputs/019e7ed2-6e44-7140-8ed1-d2ad117e97da/presentations/vulca-ppt-baseline/preview/contact-sheet.png`
- Layout JSON path: `outputs/019e7ed2-6e44-7140-8ed1-d2ad117e97da/presentations/vulca-ppt-baseline/layout/final/`
- Initial assessment: baseline exists for comparison only. It is not the product-quality target.

## Vulca Case-Pack Deck

- Status: generated
- Sources:
  - `docs/product/ppt-case-pack-v1/commercial_brief.md`
  - `docs/product/ppt-case-pack-v1/design_notes.md`
  - `docs/product/ppt-case-pack-v1/narrative_rules.json`
  - `docs/product/ppt-case-pack-v1/slide_patterns.json`
  - `docs/product/ppt-case-pack-v1/style_tokens.json`
  - `docs/product/ppt-case-pack-v1/asset_rules.json`
  - `docs/product/ppt-case-pack-v1/deck_outline.json`
  - `docs/product/ppt-case-pack-v1/vulca_generation_brief.md`
  - `docs/product/ppt-case-pack-v1/evaluation_rubric.md`
- PPTX path: `outputs/019e7ee0-8340-7713-8017-5a0227447ae4/presentations/vulca-ppt-case-pack/output/vulca-case-pack-launch.pptx`
- Contact sheet path: `outputs/019e7ee0-8340-7713-8017-5a0227447ae4/presentations/vulca-ppt-case-pack/preview/contact-sheet.png`
- Layout JSON path: `outputs/019e7ee0-8340-7713-8017-5a0227447ae4/presentations/vulca-ppt-case-pack/layout/final/`
- Initial assessment: generated from the structured case pack with editable text and native shape proof objects. No copied reference visuals or external image assets were used.

## Evaluation

Both decks now have exported screenshots and editable presentation files. Formal scoring and external model review remain separate review work.

## Gemini Review

- **Baseline commercial clarity:** The baseline clearly frames Vulca's thesis, but it stays broad by discussing generic deck-generation limits more than concrete buyer-facing workflow outcomes.
- **Baseline visual hierarchy:** The baseline uses a readable slide-by-slide structure, though the contact sheet suggests several slides lean on familiar prompt-deck patterns and fine-print text is difficult to inspect.
- **Baseline template-like risks:** Gemini flagged that prompt-only generation can drift toward generic slide structures, so the baseline risks feeling interchangeable where it should prove Vulca's specific method.
- **Baseline most important fix:** The baseline's most important fix is to make the Gemini review loop and reference-to-recipe translation explicit, visually traceable steps.
- **Vulca commercial clarity:** The case-pack deck more directly sells Vulca as a case-pack-to-editable-code workflow with clear failure modes, control layers, artifacts, and outputs.
- **Vulca visual hierarchy:** The case-pack deck presents a stronger claim/proof rhythm through named failure modes, workflow stages, product pillars, and code-first output evidence.
- **Vulca reference-case alignment:** Gemini found the case-pack deck better aligned to the supplied design memory because design decisions are tied to structured artifacts instead of inferred from a single prompt.
- **Vulca most important fix:** The case-pack deck's most important fix is to define the `slide_patterns` schema, provenance gate, and overlap-resolution behavior with implementation-level specificity.
- **Decision:** Gemini's contact-sheet aesthetic/design review indicates the case-pack deck is stronger than the baseline on narrative specificity, design coherence, and editability, but this is not final human approval, video readiness, or a full cross-platform PPT editability test.

## Score Table

| Dimension | Baseline | Vulca case-pack | Evidence |
| --- | ---: | ---: | --- |
| Commercial clarity | 3 | 5 | Gemini found the baseline thesis clear but broad, while the case-pack deck more directly sells a case-pack-to-editable-code workflow with failure modes, control layers, artifacts, and outputs. |
| Narrative flow | 3 | 4 | Gemini described the baseline as readable slide-by-slide, while the case-pack deck has a stronger claim/proof rhythm through named failure modes, workflow stages, product pillars, and code-first output evidence. |
| Technical understandability | 2 | 4 | Gemini's most important baseline fix was to make the review loop and reference-to-recipe translation explicit, while the case-pack deck already exposes structured artifacts but still needs implementation-level specificity for `slide_patterns`, provenance, and overlap resolution. |
| Visual hierarchy | 3 | 4 | Gemini found the baseline readable but noted fine-print inspection issues in the contact sheet, while the case-pack deck presents clearer hierarchy through workflow stages, pillars, and proof evidence. |
| Brand coherence | 2 | 4 | Gemini flagged prompt-only generation as prone to generic slide structures, while the case-pack deck better matches the supplied design memory by tying design decisions to structured artifacts. |
| Cultural/design intent | 2 | 4 | The baseline depends on intent inferred from one prompt, while the case-pack deck grounds design choices in the case-pack sources and Gemini review, though it is not final human approval. |
| Slide-to-slide consistency | 3 | 4 | The baseline contact sheet suggests familiar prompt-deck patterns, while Gemini found the case-pack deck's repeated failure-mode, workflow, pillar, and output-evidence structure more coherent across slides. |
| Editability | 3 | 5 | The artifact manifest records editable PPTX outputs for both decks, and the case-pack deck additionally uses editable text and native shape proof objects with no copied reference visuals or external image assets. |
| Accessibility | 2 | 3 | Gemini noted baseline fine print is difficult to inspect and credited the case-pack deck with stronger hierarchy, but neither deck has a formal accessibility audit recorded. |
| Cross-platform rendering risk | 3 | 4 | Both decks have PPTX and layout JSON exports, and the case-pack deck reduces asset risk by using native shapes, but no manual PowerPoint, Keynote, or Google Slides inspection has been completed. |

## Product Primitive Decision

- Recommended next primitive: case-pack schema plus Gemini-assisted deck review loop.
- Reason: structured design knowledge and aesthetic review improved narrative specificity/design coherence before investing in a larger layout engine.
- Next product question: which slide patterns are reliable enough to become reusable generation primitives.
