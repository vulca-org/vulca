# Vulca Generation Brief

Generate the Vulca Product Launch Deck using the full case pack.

## Required Inputs

- `commercial_brief.md`
- `design_notes.md`
- `narrative_rules.json`
- `slide_patterns.json`
- `style_tokens.json`
- `asset_rules.json`
- `deck_outline.json`
- `evaluation_rubric.md`

## Design Constraints

- Use artifact-tool presentation JSX for editable PPTX generation.
- Use one slide module per slide.
- Keep all titles, body copy, labels, and diagram text editable.
- Use native shapes or editable SVG for diagrams.
- Do not use bitmap images for text.
- Do not copy reference-case visuals.
- Use a restrained warm-neutral base with signal accents from `style_tokens.json`.
- Avoid a generic dark-blue AI SaaS palette.
- Each slide must include one claim and one proof object.
- Generate rendered previews, layout JSON, and a contact sheet before review.

## Source Boundary

Respect the source boundary: use the references only for original analysis. Do not copy proprietary visuals, source layouts, article text, screenshots, event graphics, or client materials.

## Expected Output

- editable PPTX;
- rendered slide PNGs;
- contact sheet;
- layout JSON;
- Gemini review notes;
- comparison report against the baseline deck.
