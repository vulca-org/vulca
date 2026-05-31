# Commercial Brief

## Audience

Primary audience: founders, product leads, design leads, AI tool evaluators, and growth teams that need investor, customer, or launch decks with credible design quality.

Secondary audience: technical teams evaluating whether AI-assisted deck generation can produce editable, reviewable PowerPoint artifacts rather than attractive screenshots.

## Buyer Problem

Prompt-only slide tools can create fast first drafts, but the output often hides the design logic, weakens product-specific story, and leaves teams with brittle assets that are hard to edit in PowerPoint. For high-stakes product launches, the buyer needs clear narrative structure, reusable design decisions, native editability, and evidence that the deck was reviewed against commercial criteria.

## Promise

Vulca turns source-grounded design memory into a code-generated PPT. The deck remains editable, traceable, and reviewable: slide roles come from a case pack, visuals come from native shapes and editable diagrams, and the comparison against a prompt-only baseline records what improved and what still needs repair.

## Constraints

- Main output must be a code-generated editable PPT.
- Essential text, labels, diagrams, and proof objects must use native shapes, editable text, or editable SVG.
- Image generation is auxiliary and cannot be the deck engine.
- Public references may guide original analysis only.
- No copied screenshots, brand marks, proprietary layouts, templates, glyphs, or long source prose.
- Generated artifacts must remain local under `outputs/$THREAD_ID/presentations/` unless approved.

## Proof Standard

The deck must prove value with inspectable evidence: case-pack validation, PPTX generation, layout JSON, contact sheets, PPTX integrity checks, Gemini critique, one focused repair pass, and a ten-dimension score comparison against the prompt-only baseline. A public claim requires later human review.
