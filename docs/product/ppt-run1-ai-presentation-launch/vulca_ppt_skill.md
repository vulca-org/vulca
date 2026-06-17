# Vulca PPT Skill

Use this skill draft for Run 1 deck generation after the case pack validates.

## Steps

1. Source analysis: read `sources.json` and `source_summaries.md`; extract only original principles, not visuals or source wording.
2. Design memory: load `design_memory.json` and translate each observation into editable layout behavior, diagram vocabulary, or review criteria.
3. Narrative assembly: use `narrative_rules.json`, `slide_patterns.json`, and `deck_outline.json` to create the exact ten-slide sequence.
4. Style application: use `style_tokens.json` for palette, type, spacing, corner radius, strokes, and status treatments.
5. Asset discipline: follow `asset_rules.json`; prefer native shapes and editable SVG; keep image generation auxiliary.
6. Code-generated deck: write deterministic presentation code that emits editable PPT content and layout JSON.
7. Artifact check: save generated PPTX, contact sheets, layout JSON, and temporary assets under `outputs/$THREAD_ID/presentations/`.
8. Gemini review: run the contact-sheet review with `gemini_review_prompt.md`; request numeric zero-through-five scores and slide-specific fixes.
9. Repair pass: apply one focused repair pass to the Vulca deck, record changes in `results/iteration_log.md`, and keep evidence traceable.
10. Comparison: update `results/comparison_report.md` only after baseline and Vulca decks exist and checks have run.
