# Vulca PPT Run 1.5 Product Lab Design

**Status:** draft for user review
**Date:** 2026-05-31
**Branch:** `codex/vulca-ppt-case-pack`
**Related PR:** https://github.com/vulca-org/vulca/pull/128

## Decision

Run 1.5 keeps the original PPT wedge plan, but changes the proof shape from an explanatory launch deck into a product experiment artifact. It is a thin slice, not a full new product surface.

Run 1 proved that a case-pack-driven, code-generated PPT can beat a prompt-only baseline on a documented rubric. Run 1.5 should prove something stricter:

```text
real commercial brief
-> tutorial / case evidence
-> design memory
-> skill workflow
-> code-generated PPT
-> controlled comparison
-> QA / publish gate
```

The important shift is not cosmetic. The deck should make the workflow feel like a real product system that ran, learned from structured inputs, produced an editable artifact, and exposed the evidence needed to decide whether it can be published.

Run 1.5 prioritizes one hard proof:

```text
design evidence -> design memory rules -> code generation choices -> visible output difference
```

The broader skill workflow surface and five-arm ablation matrix remain documented, but they must not crowd the main deck or block the first implementation pass.

## Why Run 1 Still Feels Too Prompt-Generated

The current Run 1 Vulca deck is better than the baseline, but it is still mostly an explanation of the system. It has visible proof objects, but many of them are abstract tables and flowcharts.

Observed gaps:

- **Content specificity:** The commercial brief is present in files, but the deck does not yet feel like a real customer or product launch brief being processed.
- **Layout rhythm:** The deck alternates cards, tables, and workflow diagrams, but most slides still read as generated explanation pages.
- **Functional product surface:** Viewers can understand the system, but they do not yet see enough input panels, transformation states, repair queues, gates, and outputs to believe the product is operating.
- **Learning evidence:** The case pack and design memory exist, but the visual story does not yet prove what changed because of the tutorial or case data.
- **Publishing confidence:** Structural QA exists, but native render and public-publish gates remain explicitly blocked.

## Product Hypothesis

If Vulca can convert tutorial and commercial case evidence into explicit rules, primitives, and QA gates, then the final PPT should improve for reasons that are visible and testable, not just because the prompt was longer.

Run 1.5 should make three claims:

1. **Product claim:** Vulca is a structured deck-generation workflow, not a one-shot slide generator.
2. **Learning claim:** Case and tutorial data affect the output through inspectable design memory and skill rules.
3. **Delivery claim:** Generated PPTX artifacts need renderer and publish gates before public claims.

## Target Output

Create a new Run 1.5 demo package under:

```text
docs/product/ppt-run1-5-product-lab/
```

The package should include design inputs, experiment protocol, generation briefs, QA reports, comparison tables, Gemini reviews, and final result notes.

Generated PPTX files, contact sheets, previews, and layout JSON should stay local under `outputs/$THREAD_ID/presentations/` unless the user explicitly approves committing release artifacts.

## Deck Shape

The Run 1.5 deck should remain a 10-slide deck, but its visual grammar should move from "explaining Vulca" to "showing a product lab run."

### Slide 01: Experiment Cover

Job: State the product experiment, not a generic launch claim.

Proof object: A compact run header with brief id, source count, rule count, baseline count, QA status, and publish status.

### Slide 02: Real Brief Cockpit

Job: Show a commercial brief being processed.

Proof object: A product-style input surface with audience, business goal, must-win decision, constraints, source boundary, and do-not-copy rules.

### Slide 03: Source And Tutorial Intake

Job: Show what the system learned from public references and tutorial notes.

Proof object: Source registry plus tutorial evidence slots, each mapped to allowed use and prohibited copying.

### Slide 04: Design Memory Compiler

Job: Show raw observations becoming reusable design rules.

Proof object: A transformation map from source insight to principle, code-generation rule, slide primitive, and QA check.

### Slide 05: Skill Workflow Surface

Job: Make the workflow feel operational.

Proof object: A compact state strip: ingest, normalize, generate, review, repair, validate, publish-block.

Scope control: This slide should not attempt to become a full UI mock. It should only prove state ownership and gate transitions.

### Slide 06: Code Generation Anatomy

Job: Prove that the output is code-first PPT generation.

Proof object: Native editable slide module map, artifact-tool export chain, layout JSON, provenance manifest, and PPTX package checks.

### Slide 07: Baseline Versus Vulca

Job: Show the central comparison without burying it in a dense table.

Proof object: Side-by-side score deltas and representative failure types: generic story, weak hierarchy, brittle editability, missing review path.

### Slide 08: Ablation Proof

Job: Test whether data actually matters.

Proof object: Three-arm main experiment:

- `prompt-only`: no case-pack rules.
- `full Vulca`: complete case pack plus workflow.
- `bad data / corrupted rules`: intentionally wrong or mismatched rules.

The detailed five-arm matrix can live in the report or appendix, not the main visual flow.

### Slide 09: QA And Publish Gate

Job: Make delivery risk visible.

Proof object: Structural QA, Gemini review, layout QA, PPTX integrity, renderer availability, native render status, human approval, public publish status.

### Slide 10: Product Decision

Job: End with the product primitive selected by evidence.

Proof object: Decision table showing whether the next primitive is renderer QA, layout primitives, data ingestion, review repair, or asset handling.

## Experiment Protocol

Run 1.5 should not only compare baseline and Vulca. It should add a small negative control.

Main experiment arms:

| Arm | Input | Expected Signal |
| --- | --- | --- |
| Prompt-only | ordinary brief prompt | generic but coherent deck |
| Full Vulca | brief, source registry, tutorial notes, design memory, workflow rules | stronger specificity, hierarchy, provenance, and QA evidence |
| Bad data / corrupted rules | mismatched or intentionally weak design rules | visible degradation or review flags |

Optional detailed arms for report only:

- source-only, without tutorial rules;
- tutorial-only, without commercial case context.

The main deck should show three arms to avoid cognitive overload. The five-arm matrix is deferred unless the first three-arm experiment is stable and the user explicitly asks to expand the study.

Run 1.5 does not need to generate all optional arms before the first demo pass. The blocking implementation set is:

- prompt-only deck;
- full Vulca deck;
- bad-data or corrupted-rules deck;
- one comparison report that records whether the bad-data arm degraded output or triggered review warnings.

Source-only and tutorial-only arms are deferred unless the first three-arm experiment is already stable.

## Visual Direction

The design should avoid generic SaaS launch-deck rhythm.

Use three recurring product surfaces:

- **Brief Cockpit:** dense but legible input and constraint panels.
- **Learning Map:** source insight to rule to primitive to QA mapping.
- **Experiment Lab:** comparison, ablation, repair queue, and gate evidence.

Rules:

- Keep essential text, labels, numbers, flow states, and comparison data editable.
- Use native PowerPoint shapes and text as the primary medium.
- Use SVG only for simple system marks, structural diagrams, or background scaffolds that remain inspectable.
- Use generated bitmap images only as auxiliary visual texture, never as a flattened information surface.
- Avoid copied screenshots, copied layouts, logos, brand marks, template files, and long copied prose from references.
- Prefer fewer, stronger proof objects over many small explanation cards.

### Layout Controls

Run 1.5 should use a stricter grid than Run 1:

- one dominant proof object per slide;
- no more than three secondary panels per slide;
- no dense four-column matrix in the main deck unless it is the central proof object;
- use large comparison deltas instead of full rubric tables where possible;
- reserve table density for the result report, not the hero slides;
- keep each slide's main claim understandable from the contact sheet.

These controls matter because a design memory compiler alone will not remove the generic generated-deck feel. The slide modules must encode stronger layout constraints.

## Data Flow

Run 1.5 should make the data-to-generation chain explicit:

```text
commercial_brief.md
sources.json
source_summaries.md
tutorial_notes.md
design_memory.json
slide_patterns.json
style_tokens.json
vulca_ppt_skill.md
-> generation brief
-> slide modules
-> PPTX / previews / layout JSON
-> Gemini review
-> repair queue
-> delivery QA
-> comparison report
```

The deck should distinguish between:

- **stored evidence:** source registry, summaries, tutorial notes;
- **learned rules:** design memory, slide primitives, style tokens, narrative rules;
- **executed workflow:** generated slide modules, preview, QA, repair;
- **delivery status:** structural pass, renderer gap, human approval, public publish block.

## Data Contract

The implementation should introduce or document a strict Run 1.5 design-memory shape before generating slides. The minimum contract is:

```json
{
  "evidence_id": "string",
  "source_role": "brief | source | tutorial | review",
  "observation": "short original note",
  "design_rule": "actionable generation rule",
  "slide_primitive": "cockpit | learning_map | comparison_delta | qa_gate | decision_table",
  "layout_constraint": "specific spacing, hierarchy, density, or editability rule",
  "qa_signal": "how the rule is checked or reviewed"
}
```

The deck should show examples of this contract, not a vague "memory" claim.

## Gemini-Agent Role

Gemini-agent should be used for critique, not ownership.

Use Gemini for:

- spec critique before implementation planning;
- contact-sheet review after generation;
- comparison sanity check;
- "does this still look like a generic GPT deck?" critique;
- focused repair suggestions.

Do not treat Gemini as final human approval, factual authority, copyright clearance, or the only aesthetic judge.

## QA Gates

Run 1.5 is internally successful only if:

- Run 1.5 case-pack files validate.
- All generated decks have editable native text and shapes for essential content.
- Layout QA passes with zero hard errors.
- PPTX integrity passes.
- Media entries are either zero or documented with provenance.
- Gemini reviews the contact sheet and explicitly comments on product-surface feel versus generic generated deck feel.
- The comparison report shows whether full Vulca beats prompt-only and whether bad data degrades or triggers warnings.
- Delivery QA records native renderer status instead of hiding it.
- Public publishing remains blocked until human review and at least one native render or manual inspection path passes.

Native render pass/fail should be explicit when implemented:

- pass: deck opens or renders with no blank slides, severe clipping, missing major text, or unusable layout breakage;
- caution: minor spacing or typography differences that do not block internal demo use;
- fail: blank slides, missing essential content, unreadable text, broken diagrams, or file-open errors.

## Implementation Boundaries

Run 1.5 may reuse Run 1 assets and structure, but should be a separate product package. Do not overwrite the Run 1 result report or generated workspaces.

Allowed implementation changes after this spec is approved:

- add Run 1.5 case-pack files;
- add or extend validators for Run 1.5 experiment protocol;
- generate new baseline / full Vulca / bad-data decks under `outputs/`;
- add result reports and Gemini review artifacts;
- extend delivery QA only if needed to represent the new experiment status.

Not allowed in Run 1.5:

- broad post-training;
- broad scraping pipeline;
- committing generated PPTX or preview binaries without explicit approval;
- claiming public demo readiness before native render and human review;
- changing unrelated Vulca visual workflows.

Deferred to Run 2 or later:

- full five-arm ablation generation as a required gate;
- production-grade design memory compiler UI;
- visual regression against fixed gold templates;
- broad malformed-intake stress testing;
- latency or performance benchmarking for an end-user product path.

## Success Criteria

Run 1.5 succeeds if a reviewer can understand these points from the deck and reports:

- what real commercial brief was processed;
- what tutorial or case evidence entered the system;
- how that evidence became design memory or skill rules;
- how code generation used those rules;
- how full Vulca differs from prompt-only;
- whether bad data degrades output or triggers review gates;
- what QA checks passed;
- what remains blocked before public publishing;
- what product primitive should be built next.

## Non-Goals

- Do not make a generic prettier version of Run 1.
- Do not use image generation as the primary PPT engine.
- Do not make the deck depend on copied reference visuals.
- Do not hide renderer risk.
- Do not overfit to Gemini's taste.
- Do not claim that the model was post-trained.

## Approval Gate

After this spec is reviewed, the next step is a Run 1.5 implementation plan using the Superpowers writing-plans workflow.

The first implementation task should create the Run 1.5 package and validator tests before generating any new deck artifacts.
