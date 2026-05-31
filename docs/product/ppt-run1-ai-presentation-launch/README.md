# PPT Run 1: AI Presentation Launch

Status: baseline and Vulca case-pack decks generated. Gemini review, repair pass, final scoring, product decision, and demo readiness are pending.

This pack defines Run 1 for an AI presentation product launch deck. The generated decks argue that prompt-only slides are not enough for high-stakes product communication, then show a controlled workflow: public reference analysis, structured design memory, code-generated PPT, visual review, repair, and comparison against a baseline.

## Source Boundary

The public references in `sources.json` are reference analysis only. Use them to understand launch framing, product-event storytelling, identity-system thinking, AI keynote clarity, and modular presentation systems. Do not copy proprietary visuals, screenshots, layouts, brand marks, template files, glyphs, full prose, or long quotes.

## Expected Outputs

- Prompt-only baseline: a 10-slide AI presentation product launch deck generated from `baseline_prompt.md`.
- Vulca deck: a code-generated PPT built from `vulca_generation_brief.md`, `deck_outline.json`, `slide_patterns.json`, `style_tokens.json`, `design_memory.json`, and `asset_rules.json`.
- Review evidence: layout JSON, contact sheets, PPTX integrity notes, Gemini review notes, repair log, and score comparison.
- Decision evidence: a comparison report that decides the next product primitive from observed gaps, not preference.

## Local Artifact Rule

Generated PPTX files, contact sheets, layout JSON, preview renders, and temporary assets stay under `outputs/$THREAD_ID/presentations/` unless a human explicitly approves release packaging. This committed pack records source rules and result status only.
