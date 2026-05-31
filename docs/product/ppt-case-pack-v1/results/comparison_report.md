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
