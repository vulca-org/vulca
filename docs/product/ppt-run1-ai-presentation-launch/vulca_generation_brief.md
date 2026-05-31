# Vulca Generation Brief

Generate a code-generated PPT for Run 1 using this case pack. The output must be editable PowerPoint content built from native shapes, editable text, editable diagrams, and layout JSON. Image generation is auxiliary only and must not become the primary deck engine.

## Sources

- `geo_figma_slides`: https://geo-nyc.com/projects/figma-slides/
- `figma_config_2024`: https://www.figma.com/blog/inside-config-2024/
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

- Editable `.pptx` generated from code.
- Contact sheet for baseline and Vulca decks.
- Layout JSON for every slide.
- Asset provenance manifest.
- PPTX integrity result.
- Gemini review notes.
- One repair-pass log.
- Comparison report with numeric zero-through-five scores.

## Constraints

- Follow the exact 10-slide deck outline.
- Keep all essential titles, claims, labels, diagrams, and comparison cells editable.
- Use native shapes for panels, proof objects, badges, connectors, and matrices.
- Use editable SVG only for simple system marks or diagrams that remain inspectable.
- Do not rasterize text.
- Do not use copied source visuals.
- Store generated artifacts under `outputs/$THREAD_ID/presentations/`.
