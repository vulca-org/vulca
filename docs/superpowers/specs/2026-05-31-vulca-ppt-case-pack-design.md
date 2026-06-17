# Vulca PPT Case Pack Design

**Date:** 2026-05-31
**Status:** draft for user review
**Scope:** Product wedge, case-pack structure, evaluation loop, and Gemini-assisted design QA

## Product Thesis

Vulca's PPT direction is not an image-generation product. It is a design-knowledge-driven presentation system:

```text
real commercial presentation cases
-> structured design knowledge
-> Vulca PPT skill
-> editable deck generated mostly by code
-> auxiliary SVG / image assets
-> visual and programmatic evaluation
```

The first proof should show that Vulca can turn real design references into a repeatable workflow for producing a commercial-quality product launch deck.

## First Use Case

The first deck should be a **Vulca Product Launch Deck**.

It should prove:

- Vulca can explain a complex AI-native visual workflow clearly.
- Vulca can generate editable slides through code, not screenshots.
- Vulca can encode design rules from real commercial references.
- Vulca can use generated images or SVGs as supporting assets without making image generation the product.
- Vulca can evaluate visual quality with Gemini while also checking layout and editability programmatically.

## Reference Cases

Use public references as design and commercial benchmarks. Do not copy proprietary slides, images, or layouts.

| Role | Source | Use |
|---|---|---|
| Main commercial reference | [Supervity AI presentation case](https://musecreatives.org/case-studies/visual-presentation-for-ai-thought-leadership/) | B2B AI keynote structure, technical complexity, premium visual tone |
| Visual system reference | [Figma Config 2025 identity](https://www.figma.com/blog/how-we-shaped-the-visual-identity-for-config-2025/) | Product-launch identity, typography, color systems, motion logic, design-system thinking |
| Product-slide reference | [Figma Slides case](https://geo-nyc.com/projects/figma-slides/) | Presentation-product launch language and user-confidence framing |
| Commercial deck reference | [Launch Labs sales deck case](https://www.whitepage.studio/portfolio/launch-lab) | Sales narrative, editable modular deck expectations, conversion-oriented clarity |
| High-end keynote reference | [Google Cloud Next keynote case](https://www.wearesparks.com/our-work/google-cloud-next/) | Multi-audience technical storytelling, cohesive visual grammar, large-scale launch polish |

## Case Pack v1

Create a repository-local case pack, not a training dataset:

```text
docs/product/ppt-case-pack-v1/
  sources.json
  source_summaries.md
  commercial_brief.md
  design_notes.md
  narrative_rules.json
  slide_patterns.json
  style_tokens.json
  asset_rules.json
  evaluation_rubric.md
  vulca_ppt_skill.md
```

### `sources.json`

Records source URL, title, role, access date, allowed use, and copyright notes.

Rules:

- Store links and short source summaries.
- Do not store full article text, full video transcripts, or proprietary slide assets.
- Screenshots may be used only as review references, not copied into generated decks.

### `commercial_brief.md`

Defines the real business need:

- audience;
- buying or adoption context;
- primary decision the deck must win;
- level of technical complexity;
- desired emotional tone;
- expected call to action.

For the first Vulca deck, the audience is builders, designers, and platform reviewers who need to understand why Vulca is different from one-click image or presentation generators.

### `design_notes.md`

Our own analysis of the references:

- narrative structure;
- information hierarchy;
- slide density;
- typography behavior;
- color usage;
- visual rhythm;
- icon, SVG, diagram, and image roles;
- what to avoid.

This file must be written as original analysis, not copied prose.

### `narrative_rules.json`

Encodes reusable story rules:

```json
{
  "opening": "Name the workflow problem before naming the feature.",
  "progression": ["pain", "market shift", "Vulca approach", "workflow", "proof", "call_to_action"],
  "technical_depth": "Expose technical control through diagrams, not long prose.",
  "closing": "End with a concrete next workflow, not a generic vision statement."
}
```

### `slide_patterns.json`

Defines slide roles and layout constraints:

- cover;
- problem;
- market shift;
- workflow diagram;
- product pillars;
- case-pack method;
- generated output proof;
- benchmark comparison;
- roadmap;
- closing.

Each pattern should include expected content density, layout shape, visual asset type, and editability requirements.

### `style_tokens.json`

Defines a strict, code-friendly design system:

- palette;
- font stack and fallbacks;
- spacing scale;
- corner radius;
- stroke widths;
- diagram styles;
- chart styles;
- light and dark usage rules.

Use system-safe font fallbacks first. Custom typography may be recommended, but the generated PPT must remain coherent if custom fonts are missing.

### `asset_rules.json`

Controls auxiliary visuals:

- prefer editable SVG for abstract systems, diagrams, arrows, nodes, and product metaphors;
- use generated bitmap images only for atmospheric or illustrative background moments;
- avoid using images as text containers;
- keep all text editable in the presentation file;
- record asset prompt, source, and license status.

### `evaluation_rubric.md`

Rates the deck across:

- commercial clarity;
- narrative flow;
- technical understandability;
- visual hierarchy;
- brand coherence;
- cultural/design intent;
- slide-to-slide consistency;
- editability;
- accessibility;
- cross-platform rendering risk.

## Generation Flow

```text
ordinary prompt
  -> baseline deck
  -> screenshots + editable-file check

case pack + Vulca PPT skill
  -> generated deck code
  -> PPTX / HTML slides
  -> screenshots
  -> Gemini aesthetic review
  -> programmatic layout checks
  -> revised deck
  -> comparison report
```

The initial implementation may generate PPTX, HTML slides, or both. PPTX proves business editability. HTML can provide stronger layout control and screenshot verification.

## Gemini-Agent Role

Codex owns:

- source collection;
- case-pack structure;
- code generation;
- layout logic;
- export scripts;
- programmatic checks;
- repository commits.

Gemini-agent owns review of:

- visual hierarchy;
- premium vs template-like feel;
- brand coherence;
- reference-case alignment;
- slide rhythm;
- whether the design looks commercially credible.

Gemini review is advisory. It does not replace deterministic checks.

## Required Checks

### Visual Review

Run Gemini artifact review on exported screenshots or PDF pages. The review should produce compact findings, not vague taste commentary.

### Layout Stress Test

The deck generator must test:

- titles 50% longer than the intended copy;
- empty optional fields;
- extra bullet counts;
- unusually long words;
- swapped auxiliary assets.

### Overlap And Bounds Check

Programmatically detect:

- text boxes outside slide bounds;
- element overlap beyond allowed intentional layering;
- clipped labels;
- unsafe margins;
- missing alt text or speaker notes where required.

### Editability Check

Verify that:

- text remains text, not rasterized into images;
- diagrams are composed of editable shapes or SVG assets;
- major sections can be edited without breaking the whole slide;
- a non-designer can change copy and replace an asset.

### Cross-Platform Check

At minimum, manually inspect output in one primary editor. Before public claims, inspect in:

- PowerPoint;
- Keynote or Google Slides;
- exported PDF.

## P1 Deliverable

P1 is complete when the repository contains:

- `ppt-case-pack-v1` with source notes, design rules, style tokens, slide patterns, and rubric;
- a baseline deck generated from an ordinary prompt;
- a Vulca-generated deck using the case pack;
- screenshots or PDF exports for both;
- Gemini review artifacts;
- a short comparison report;
- a video-ready narrative explaining why the Vulca version is better.

## P2 Evaluation

P2 answers whether the case-pack approach is worth productizing.

Compare:

```text
ordinary prompt deck
vs
case pack + Vulca PPT skill deck
```

Measure:

- does the generated deck satisfy a real commercial need;
- does it explain technical complexity more clearly;
- does it look less generic;
- does it stay editable;
- does it remain consistent across slides;
- does Gemini and human review agree that the case-pack version is stronger;
- which slide patterns are reliable enough to become product primitives.

## Non-Goals

- Do not build a generic presentation app.
- Do not train or fine-tune a model in v1.
- Do not download and store copyrighted videos, articles, or proprietary slide decks as training data.
- Do not copy reference-case visuals into the generated deck.
- Do not present generated background images as the core product.
- Do not claim keynote-scale quality until layout, typography, and editability are verified.

## Open Product Decision

After the first case-pack run, decide whether the next product primitive should be:

1. a PPT-specific Vulca skill;
2. a reusable case-pack schema;
3. a slide layout engine;
4. a Gemini-assisted deck review loop.

The decision should be based on P2 evidence, not taste alone.
