# Vulca PPT Run 2.0 Data And Skill Quality Design

**Status:** draft for user review
**Date:** 2026-06-01
**Branch:** `codex/vulca-ppt-case-pack`
**Related PR:** https://github.com/vulca-org/vulca/pull/128

## Decision

Run 2.0 restarts the PPT wedge from the data and skill layer. Run 1.5 proved that the workflow can run end to end, but it did not prove public-demo-level taste. The next pass should not patch the generated deck directly. It should thicken the fixed product pipeline:

```text
real commercial case
-> tutorial / video / case data
-> evidence memory + aesthetic memory + asset memory
-> PPT skill workflow
-> code-generated deck
-> baseline / ablation / aesthetic QA
```

These five layers are permanent product layers, not one-time milestones. Run 2.0 makes each layer serious enough to produce a credible public demo. Run 3.0 should deepen the same five layers rather than adding a sixth stage.

"Restart" means restarting the quality standard, not discarding working infrastructure. Run 2.0 should preserve useful Run 1.5 validators, generation scripts, artifact layout conventions, comparison reports, and publish gates unless a concrete quality issue requires changing them.

## Why Run 1.5 Was Not Enough

Run 1.5 used data, but it used it mainly as proof infrastructure. The design memory records evidence boundaries, product-lab primitives, comparison arms, and QA gates. That makes the artifact more trustworthy, but it pushes the visual language toward dashboards, tables, status strips, and engineering reports.

Observed gaps:

- **Data depth:** The tutorial and case notes are thin summaries, not a reusable design corpus.
- **Aesthetic extraction:** The system records what the deck should prove, but not enough about how high-end presentation design creates rhythm, scale, contrast, and visual tension.
- **Skill behavior:** The skill can generate an inspectable PPT, but it does not act like an art director. It lacks hard choices about density, pacing, hero slides, visual climax, and what to remove.
- **Asset strategy:** Generated images, SVGs, and video-derived references are not yet organized as a governed asset memory.
- **Evaluation:** Structural QA and Gemini review exist, but the main gate still rewards traceability more than public-facing visual quality.

## Product Principle

Run 2.0 must separate two kinds of quality:

| Quality Type | What It Proves | Failure Mode If Missing |
| --- | --- | --- |
| Evidence quality | The deck came from real inputs and can be audited. | Pretty but untrustworthy deck. |
| Aesthetic quality | The deck feels like a high-end public presentation. | Correct but boring engineering report. |

The deck generator needs both. Evidence memory should protect truth and provenance. Aesthetic memory should control taste, rhythm, composition, and restraint.

## Stage Contracts

Each fixed layer needs an explicit contract so Run 3.0 can deepen the same layers without changing the product architecture.

| Layer | Input | Output | Contract Check |
| --- | --- | --- | --- |
| Real commercial case | One selected business scenario and target audience | `commercial_case.md` with decision, audience, stakes, constraints, failure definition | Required fields present; case is concrete enough to generate a deck without invention. |
| Tutorial, video, and case data | Public references, tutorials, video links, local-only review notes | `source_cards/` and `video_cards/` with allowed use, observed move, translation, and risk | Every card has source id, allowed use, do-not-copy boundary, observed move, PPT translation, and quality risk. |
| Memory layer | Source cards and video cards | `evidence_memory.json`, `aesthetic_memory.json`, `asset_memory.json` | JSON schemas validate; every aesthetic move traces to at least one card; every asset has provenance state. |
| Skill workflow | Commercial case plus memory files | `vulca_ppt_skill.md`, generation briefs, generated slide modules | Skill stages run in order; selected slide archetypes cite memory ids; deletion/appendix routing is available. |
| Rerun and evaluation | Generated arms and local artifacts | comparison reports, aesthetic review, render gate, release decision | Baseline, Run 1.5, Run 2.0, and bad-aesthetic arms are comparable on the same rubric. |

These contracts matter more than file names. File names can evolve; the five layer boundaries should not.

## The Five Fixed Layers

### 1. Real Commercial Case

Run 2.0 should select one concrete commercial presentation need, not a generic "make a beautiful PPT" prompt.

The case must define:

- audience and decision context;
- business objective;
- product or idea being sold;
- expected deck length;
- must-win emotional impression;
- public-demo constraints;
- what would count as a failed deck.

The first Run 2.0 case should stay close to the current wedge: a high-end AI product or design-system presentation where technical credibility and design polish both matter.

### 2. Tutorial, Video, And Case Data

Run 2.0 data should be structured as analysis cards, not loose notes.

Each source should produce one or more cards with:

- `source_id`;
- `source_type`: `commercial_case`, `tutorial`, `video`, `design_article`, or `reference_deck`;
- `allowed_use`: short analysis, derived rules, visual inspiration, or local-only review;
- `do_not_copy`: screenshots, logos, proprietary layouts, full transcripts, or long prose;
- `observed_move`: the design move seen in the source;
- `why_it_works`: the business or perceptual reason;
- `ppt_translation`: how the move becomes an editable PPT primitive;
- `quality_risk`: how this could become generic, overdesigned, or misleading.

Video sources need a separate extraction pass:

```text
video URL or local path
-> chapter / timestamp map
-> representative keyframe descriptions
-> presenter pacing notes
-> slide transition observations
-> derived aesthetic cards
```

The repository should store derived observations and references. It should not store full copyrighted video, full transcripts, copied slide screenshots, or proprietary visual assets unless a later license review explicitly allows it.

### 3. Memory Layer

Run 2.0 should split memory into three files.

#### `evidence_memory.json`

Purpose: prove claims and preserve source boundaries.

It should store:

- source ids;
- observations;
- allowed use;
- prohibited copying;
- business relevance;
- claims supported by each observation;
- QA checks required before public use.

#### `aesthetic_memory.json`

Purpose: control presentation taste.

It should store:

- `aesthetic_move`: named design move, such as `cinematic_cover`, `low_density_claim`, `big_object_layout`, `editorial_comparison`, `visual_climax`, or `premium_closing`;
- `trigger`: when this move should be used;
- `composition_rule`: scale, placement, whitespace, contrast, and hierarchy requirements;
- `typography_rule`: title/body ratio, line length, label behavior, and emphasis;
- `density_budget`: maximum claims, panels, and words;
- `rhythm_role`: cover, setup, contrast, proof, climax, relief, or close;
- `ppt_primitive`: native shapes, editable text, SVG, generated background, chart, or diagram;
- `negative_rules`: dashboard smells, table overuse, small-label overload, weak focal point, or template-like symmetry;
- `qa_signal`: what a reviewer or programmatic gate should inspect.

#### `asset_memory.json`

Purpose: govern image, SVG, and video-derived support assets.

It should store:

- generated image prompts and provenance;
- SVG roles and editability boundaries;
- local-only reference notes;
- asset license state;
- which slides can use atmosphere versus evidence;
- which text must remain editable;
- render and accessibility risks.

### 4. Skill Workflow

The Run 2.0 skill should be rewritten as a staged deck director, not a longer prompt.

Required stages:

1. Read commercial case and select the narrative spine.
2. Compile evidence memory into claims and guardrails.
3. Compile aesthetic memory into slide archetypes and rhythm.
4. Select assets only after the slide role is known.
5. Generate code-first PPT modules.
6. Run structural QA.
7. Run aesthetic QA.
8. Repair the deck with explicit reasons.
9. Emit a release decision: internal only, demo candidate, or public blocked.

The skill must make deletion possible. If a slide has too many proof objects, the correct action is often to move detail to appendix or speaker notes, not compress the same content into smaller text.

### 5. Rerun And Evaluation

Run 2.0 should rerun the same core comparison structure, but with a better quality target.

Required arms:

| Arm | Input | Purpose |
| --- | --- | --- |
| Prompt-only | commercial brief only | Measures generic model baseline. |
| Run 1.5 skill | previous evidence-heavy workflow | Measures current product-lab baseline. |
| Run 2.0 skill | thick data + aesthetic memory + asset memory | Tests whether data and skill improvements raise public-demo quality. |
| Bad aesthetic memory | valid evidence but weak or wrong aesthetic rules | Tests whether the aesthetic layer actually matters. |

Required evaluation:

- contact-sheet review;
- per-slide density score;
- rhythm variance score;
- focal-object scale score;
- visual hierarchy score;
- evidence alignment check;
- asset provenance check;
- native or cross-platform render inspection;
- Gemini advisory review;
- human public-demo decision.

## Visual And Content Quality Checklist

Run 2.0 should evaluate public-demo quality with concrete checks, not only taste language.

Main-deck checks:

- each slide has one dominant claim;
- each slide has one dominant visual object or composition move;
- no main slide uses a dense table unless the table is the visual object;
- main title is readable from a contact sheet;
- secondary text does not compete with the focal object;
- slide rhythm includes setup, contrast, proof, and close rather than repeated dashboards;
- at least two slides use low-density high-impact composition;
- at least one slide creates a visual climax;
- appendix or notes absorb proof detail that weakens the main story;
- all core text remains editable.

Quality scoring should include:

- `commercial_specificity`;
- `evidence_alignment`;
- `aesthetic_memory_usage`;
- `visual_hierarchy`;
- `rhythm_variance`;
- `density_control`;
- `asset_discipline`;
- `editability`;
- `render_risk`.

Run 2.0 should beat Run 1.5 specifically on `aesthetic_memory_usage`, `rhythm_variance`, and `density_control`. If it only improves evidence alignment, the rerun has not solved the right problem.

## Non-Functional Constraints

Run 2.0 should stay narrow enough to finish.

- Start with one commercial case, not a broad benchmark suite.
- Start with a small curated source set before adding automated source ingestion.
- Prefer manual video-card extraction in the first pass unless a script clearly saves time.
- Reuse Run 1.5 validators and artifact conventions when they still apply.
- Keep generated main-deck length to five, six, or seven slides.
- Keep implementation testable with schema validators before running expensive generation.
- Treat Gemini and human review as quality gates, not as uncontrolled iteration loops.

## AWT Role

Academic Writing Toolkit should support source discipline, not visual scoring.

Use AWT for:

- reading-note templates for source analysis;
- citation consistency between source notes and analysis claims;
- paragraph-level logic review of design rationale documents;
- conservative spelling/style cleanup for public-facing written reports if needed.

Do not use AWT as a substitute for visual review. It should catch weak argumentation and source drift in the written knowledge base.

## Gemini-Agent Role

Gemini-agent should support visual and plan judgment.

Use Gemini for:

- plan critique before broad workflow changes;
- artifact review of contact sheets, screenshots, and generated decks;
- research briefs when current public presentation references are needed;
- independent review of whether the result feels premium, public-ready, and less like an engineering report.

Gemini feedback is advisory. Codex remains responsible for repository edits, validation, commits, and final claims.

## Superpowers Role

Use Superpowers to keep the work disciplined:

- brainstorming for design decisions;
- writing-plans before implementation;
- subagent-driven-development for independent tasks;
- receiving-code-review for reviewer findings;
- verification-before-completion before any completion claim.

The Run 2.0 implementation should use small commits for coherent verified changes.

## Target Package

Create a new package:

```text
docs/product/ppt-run2-data-skill-quality/
  README.md
  commercial_case.md
  sources.json
  source_cards/
  video_cards/
  evidence_memory.json
  aesthetic_memory.json
  asset_memory.json
  narrative_spine.json
  slide_archetypes.json
  aesthetic_rubric.md
  vulca_ppt_skill.md
  generation_briefs/
  results/
```

Generated decks, screenshots, contact sheets, and local render artifacts should remain under `outputs/` unless the user explicitly approves committing release artifacts.

## Quality Bar

Run 2.0 is successful only if:

- the data layer is inspectable and materially thicker than Run 1.5;
- aesthetic memory contains concrete composition, rhythm, typography, and density rules;
- the new skill uses those rules during generation instead of merely quoting them;
- Run 2.0 beats both prompt-only and Run 1.5 in aesthetic review;
- a bad-aesthetic-memory arm degrades visual quality without breaking structural output;
- the final deck can still be traced back to evidence memory;
- public release remains blocked unless human and native-render gates pass.

## Non-Goals

- Do not claim post-training, fine-tuning, or model learning unless such a training process is actually implemented.
- Do not copy commercial source visuals, screenshots, templates, logos, layouts, or long prose into the generated deck.
- Do not treat a beautiful generated background as the product. The main output remains editable, code-generated PPT.
- Do not expand to many cases before one high-quality case proves the pipeline.
- Do not skip the baseline, bad-memory arm, or publish gate.

## Open Decisions For Implementation Planning

The implementation plan should decide:

- whether Run 2.0 starts with one new source set or upgrades the existing Run 1.5 sources first;
- the minimum required number of source cards before generation is allowed;
- whether video cards are manually authored in v1 or produced by a script;
- the exact validator contract for `aesthetic_memory.json`;
- whether the first generated public-demo deck is five, six, or seven slides.
