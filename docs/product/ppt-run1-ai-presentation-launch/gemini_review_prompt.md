# Gemini Review Prompt

Review the baseline deck and the Vulca case-pack deck from contact sheets, layout JSON summaries, and artifact notes. Do not generate slide code, rewrite the deck, or invent factual claims.

Return:

- Numeric zero-through-five scores for each rubric dimension for both decks.
- One evidence sentence for each score.
- Design issues ordered by severity.
- Slide-specific fixes for the Vulca deck.
- Editability risks, including rasterized text, non-editable diagrams, grouped objects that block editing, or hidden source-copy risk.
- Accessibility risks, including contrast, type size, density, reading order, color dependence, and label clarity.
- Cross-platform risks for PowerPoint, Keynote, Google Slides, and artifact-tool previews.
- A short judgment on whether the Vulca deck is stronger than the prompt-only baseline on narrative specificity and design coherence.

Rubric dimensions: commercial clarity, narrative flow, technical understandability, visual hierarchy, brand coherence, cultural/design intent, slide-to-slide consistency, editability, accessibility, and cross-platform rendering risk.

Gemini review is qualitative evidence only. Human review is required before any public-facing claim.
