# Vulca PPT Run 1 Design

**Status:** Draft for user review
**Date:** 2026-05-31
**Branch:** `codex/vulca-ppt-case-pack`
**Related PR:** https://github.com/vulca-org/vulca/pull/128

## Decision

Start a formal **Run 1**, but treat it as a product-quality trial run, not a public launch.

Run 1 should prove whether Vulca can turn real commercial presentation references into an editable, code-generated deck that scores higher than a prompt-only baseline on a defined rubric. The target is a publishable demo package: case pack, baseline deck, Vulca deck, Gemini review, score table, iteration log, and a short video script.

## Selected Commercial Case

**Case theme:** AI presentation product launch deck.

**Commercial need:** A technical AI product must explain why ordinary prompt-generated slides are not enough, then show a more controlled workflow: reference research, structured design memory, code-generated editable PPT, visual QA, and iteration.

**Audience:** founders, product/design leads, and AI tool evaluators who care about presentation quality, editability, and credible commercial storytelling.

**Why this case:** It is close enough to Vulca's product wedge to be useful, but concrete enough to avoid generic "make a better PPT" work. It also gives a fair comparison target: prompt-only deck versus case-pack-driven deck.

## Reference Set

Use public references for analysis only. Do not copy proprietary visuals, screenshots, layouts, brand marks, full prose, or template files.

Primary references:

- GEO / Figma Slides case study: https://geo-nyc.com/projects/figma-slides/
- Figma Slides product announcement / Config 2024 context: https://www.figma.com/blog/inside-config-2024/
- Figma Config 2025 visual identity process: https://www.figma.com/blog/how-we-shaped-the-visual-identity-for-config-2025/
- MUSE Creatives / Supervity AI keynote presentation case: https://musecreatives.org/case-studies/visual-presentation-for-ai-thought-leadership/

Reference roles:

- Figma Slides / GEO: how a presentation product creates a recognizable launch look, templates, and product-facing creative system.
- Figma Config identity: how a flexible design system, glyph language, and event/product identity can become reusable deck vocabulary.
- Supervity AI keynote: how to make dense AI content commercially understandable through narrative flow, data visualization, and keynote-level polish.

## Product Hypothesis

If Vulca has a structured case pack and Gemini-assisted visual review, then a code-generated PPT can outperform prompt-only generation on:

- commercial clarity;
- narrative specificity;
- design coherence;
- editability;
- reviewability;
- artifact provenance.

The next primitive should be decided from evidence, not taste. The expected next primitive remains **case-pack schema plus Gemini-assisted review loop** unless Run 1 shows that slide layout primitives are the real bottleneck.

## Evaluation Protocol

Use the existing rubric from `docs/product/ppt-case-pack-v1/evaluation_rubric.md` and score the same ten comparison dimensions already used in `docs/product/ppt-case-pack-v1/results/comparison_report.md`:

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

Each dimension receives an integer 0-5 score for the baseline deck and the Vulca deck, plus one evidence sentence. Evidence must reference at least one of: source notes, generated artifact manifest, contact sheet review, layout JSON, PPTX integrity result, or Gemini critique.

Gemini review is qualitative evidence, not the sole scoring authority. If Gemini's qualitative judgment conflicts with layout QA or artifact evidence, the result is marked as a review conflict and requires human adjudication before any public-facing claim.

## Run 1 Data Shape

Do not start with post-training.

Use a small, inspectable multimodal case-pack dataset:

- `sources.json`: source registry, access dates, allowed use, copyright notes.
- `source_summaries.md`: original summaries of each source and why it matters.
- `tutorial_notes.md`: extracted design teaching points from videos/articles/tutorials, written as original notes.
- `commercial_brief.md`: target audience, buyer problem, demo promise, constraints.
- `design_memory.json`: reusable design observations, not copied layouts.
- `narrative_rules.json`: slide-story rules.
- `slide_patterns.json`: reusable slide roles and layout constraints.
- `style_tokens.json`: color, type, spacing, shape, and motion vocabulary for code generation.
- `asset_rules.json`: when to use native PPT shapes, editable SVG, generated bitmap images, or no image.
- `deck_outline.json`: exact Run 1 deck sequence.
- `baseline_prompt.md`: prompt-only baseline input.
- `vulca_generation_brief.md`: case-pack-driven generation input.
- `gemini_review_prompt.md`: visual review contract.
- `results/`: generated artifact manifest, Gemini review notes, score table, and iteration log.

This is a database in the product sense: structured, reusable, auditable design memory. It is not a vector database or model-training corpus yet.

## Generation Boundary

The main output must be code-generated PPT.

Primary target format: Office Open XML `.pptx`, intended first for Microsoft PowerPoint 365. Artifact-tool previews and layout JSON are the automated review surface for Run 1. Cross-platform inspection in Keynote and Google Slides is not required to pass Run 1, but it remains required before public publishing.

Allowed:

- native editable PPT text and shapes;
- editable SVG diagrams or marks generated from code;
- generated bitmap backgrounds or illustrations only when they support a specific slide and have provenance recorded;
- contact sheets and layout JSON for review.

Not allowed:

- copying reference visuals;
- flattened screenshot decks as the primary output;
- using image generation as the main deck engine;
- claiming video readiness before a human checks the deck.

## Gemini Role

Gemini is the aesthetic reviewer and critic, not the owner of the generation pipeline.

Use Gemini for:

- plan critique before building;
- contact-sheet visual review;
- score table sanity check;
- slide-specific visual repair suggestions;
- final "is this demo credible?" review.

Do not use Gemini as the source of truth for factual claims, copyright clearance, or final human approval.

## Run 1 Pipeline

1. Build Run 1 case-pack directory from the selected references.
2. Validate the case pack with the existing validator or a narrow extension.
3. Generate a prompt-only baseline deck.
4. Generate a Vulca case-pack deck using the bundled Presentations artifact-tool runtime.
5. Run layout QA and PPTX integrity checks.
6. If a headless office renderer is available, export a PDF or image render and record clipping/overflow observations. If unavailable, record the renderer gap instead of silently skipping it.
7. Ask Gemini to review both contact sheets with the committed Run 1 review prompt.
8. Apply one focused repair pass to the Vulca deck.
9. Score baseline versus Vulca across the evaluation protocol above.
10. Decide the next product primitive.
11. Produce a demo video outline only if the case-pack deck clears the quality gates.

## Quality Gates

Run 1 is successful only if:

- case pack validation passes;
- both baseline and Vulca decks generate as PPTX;
- Vulca deck has no hard layout QA errors;
- PPTX zip integrity checks pass;
- renderer availability is checked and recorded;
- all externally inspired material is marked reference-analysis-only;
- Vulca deck beats baseline by at least one average point across the rubric;
- Gemini identifies the Vulca deck as stronger on narrative specificity and design coherence, without being treated as final approval;
- at least one human review remains explicitly required before public publishing.

## Deliverables

Expected implementation deliverables:

- `docs/product/ppt-run1-ai-presentation-launch/`
- Run 1 validator tests or extensions if the current validator is too narrow.
- generated local evidence under `outputs/$THREAD_ID/presentations/`.
- committed result report, score table, and product decision.
- optional demo-video script if quality gates pass.

Generated binary PPTX/contact-sheet/layout outputs stay local unless explicitly approved for commit or release packaging.

## Non-Goals

- No post-training.
- No broad scraping pipeline.
- No general PPT layout engine yet.
- No public launch claim.
- No claim that Codex has good aesthetic taste by itself.
- No copying Figma, GEO, Supervity, or agency visuals.

## Open Risks

- Reference pages may not provide enough slide-level detail, requiring more public tutorial sources.
- Generated deck may still look competent but not launch-grade.
- Layout QA can catch overlap but not taste; Gemini can critique taste but is nondeterministic.
- Cross-platform editability remains unproven until manual PowerPoint, Keynote, or Google Slides checks.

## Approval Gate

After this spec is approved, write an implementation plan for Run 1. The first implementation task should create the Run 1 case-pack skeleton and validator coverage before generating any deck artifacts.
