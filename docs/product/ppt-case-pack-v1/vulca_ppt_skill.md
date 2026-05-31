# Vulca PPT Skill v1

Use this skill when generating a commercial product-launch deck from the Vulca PPT case pack.

## Input Files

- `commercial_brief.md`
- `design_notes.md`
- `narrative_rules.json`
- `slide_patterns.json`
- `style_tokens.json`
- `asset_rules.json`
- `deck_outline.json`

## Rules

1. Generate editable slide code, not screenshots.
2. Keep title, body copy, diagrams, labels, and key shapes editable.
3. Use generated bitmap images only as supporting atmosphere or illustration.
4. Use SVG or native shapes for workflows, diagrams, matrices, system marks, and product metaphors.
5. Do not copy reference visuals, brand marks, page layouts, proprietary slide images, or source prose.
6. Each slide needs one claim and one proof object.
7. Map every slide to a `slide_patterns.json` pattern.
8. Run Gemini review on rendered screenshots before finalizing the deck.
9. Run layout and editability checks before claiming the deck is ready.

## Outputs

- Baseline prompt record.
- Vulca generation brief.
- PPTX or HTML slide artifact.
- Rendered screenshots or PDF.
- Gemini review notes.
- Comparison report.
