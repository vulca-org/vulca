# Vulca Generation Brief

Generate a code-generated PPT for Run 1 using this case pack. The output must be editable PowerPoint content built from native shapes, editable text, editable diagrams, and layout JSON. Image generation is auxiliary only and must not become the primary deck engine.

## Sources

- `geo_figma_slides`: https://geo-nyc.com/projects/figma-slides/
- `figma_config_2024`: https://www.figma.com/blog/config-2024-recap/
- `figma_config_2025_identity`: https://www.figma.com/blog/how-we-shaped-the-visual-identity-for-config-2025/
- `supervity_ai_keynote`: https://musecreatives.org/case-studies/visual-presentation-for-ai-thought-leadership/

Use these sources for original analysis only. Do not copy visuals, screenshots, layouts, brand marks, template files, glyphs, full prose, or long quotes.

## Required Inputs

- `commercial_brief.md`
- `design_notes.md`
- `tutorial_notes.md`
- `design_memory.json`
- `narrative_rules.json`
- `slide_patterns.json`
- `style_tokens.json`
- `asset_rules.json`
- `deck_outline.json`

## Required Outputs

- PPTX generated from code with one slide module per outline slide.
- Contact sheet for baseline and Vulca decks.
- Layout JSON for every slide.
- Asset provenance manifest for every generated, referenced, or embedded asset.
- PPTX integrity result.
- Renderer availability record, including the renderer used or the renderer gap if unavailable.
- Gemini review notes.
- Iteration log for the repair pass.
- Comparison report with numeric zero-through-five scores.

## Constraints

- Follow the exact 10-slide deck outline.
- Create one slide module per outline slide, using the slide `id`, `pattern_id`, `title`, `claim`, and `proof_object` from `deck_outline.json`.
- Keep all essential titles, claims, labels, diagrams, and comparison cells editable.
- Use editable text for every title, claim, label, score, and evidence sentence.
- Use native shapes for panels, proof objects, badges, connectors, diagrams, and matrices.
- Use editable SVG only for simple system marks or diagrams that remain inspectable.
- Do not rasterize text.
- Do not use copied reference visuals, screenshots, layouts, brand marks, template files, glyphs, or long prose from the sources.
- Store generated artifacts under `outputs/$THREAD_ID/presentations/`.
