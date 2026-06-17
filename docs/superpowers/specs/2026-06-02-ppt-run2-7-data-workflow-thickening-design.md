# PPT Run 2.7 Data And Workflow Thickening Design

## Status

Proposed design. Run 2.7 is a same-loop thickening pass after Run 2.6R. It must not advance the project to Run 3.0.

## Decision Rule

Every next decision must improve at least one of these five layers, and preferably connect several of them:

1. More real commercial usecase
2. Higher-quality multimodal tutorial and case database
3. More specific design memory
4. Stricter skill workflow
5. More advanced code-generated native PPT

Changes that only rename runs, restyle colors, or add isolated visual polish without improving the data-to-workflow chain are out of scope.

## Goal

Run 2.7 should prove that the product can deepen the same pipeline that Run 2.6R made visible:

```text
real commercial brief
-> multimodal tutorial/case database
-> design memory
-> skill workflow
-> code-generated native PPT
-> QA, control arms, and review gates
```

Run 2.6R proved that a visual repair policy can visibly change the deck. Run 2.7 must prove that richer source data and stricter workflow produce a better, more attributable repair.

## Primary Usecase

The first Run 2.7 usecase should be:

```text
AI design-to-production platform launch deck
```

Audience:
- AI product builders
- design engineering leaders
- technical founders
- public-demo viewers who need to understand why Vulca is not a normal slide generator

Business job:
- show that Vulca can turn real design tutorials, case references, and design memory into editable presentation output
- prove product-system learning, not one-shot prompting
- create a publishable internal demo candidate while preserving public-blocked gates

Failure modes:
- looks like an engineering experiment report
- has data in trace but not in the picture
- copies source brand identity
- uses raster images as the main slide surface
- has no climax slide or payoff moment
- cannot explain why the output changed

## Layer 1: Real Usecase

Run 2.7 should replace generic PPT goals with a commercial brief that includes:

- current public-source references gathered during implementation
- audience and buying context
- business decision being influenced
- six-slide narrative arc
- must-show and must-not-show constraints
- public-demo risk
- measurable proof questions

The brief should force concrete presentation decisions:

- cover: what product category is being introduced
- setup: what workflow problem exists
- contrast: what changes when the product is used
- proof: what evidence route should be visible
- climax: what one large transformation object proves the point
- close: what release or handoff gate remains

## Layer 2: Multimodal Tutorial And Case Database

The database must stop being a loose collection of sources. Each source unit should become a design-learning record.

Required source types:

- video tutorial or talk segment
- transcript excerpt
- screenshot or frame reference
- visual case article
- public presentation or launch reference
- interaction or product-surface reference when applicable

Each record should include:

- source id
- source type
- allowed use
- timestamp or section anchor
- visual observation
- transcript or teaching claim
- extracted design rule
- slide role applicability
- native PPT implication
- anti-copy boundary
- QA probe

Example record shape:

```json
{
  "id": "mm_2_7_climax_single_object_tutorial",
  "source_type": "video",
  "allowed_use": "derived_rules_only",
  "anchor": "timestamp_or_section",
  "observation": "The presenter turns a complex workflow into one large transformation object.",
  "design_rule": "Climax slide should allocate the largest field to one native proof object.",
  "slide_roles": ["climax"],
  "native_ppt_implication": "Use editable grouped shapes, not a screenshot.",
  "anti_copy_boundary": "Do not copy the original brand, colors, UI, or exact composition.",
  "qa_probe": "Contact sheet should show a clear single-object climax."
}
```

## Layer 3: Design Memory

Run 2.7 design memory should be specific enough to drive generation choices.

Memory families:

- typography memory: title word count, scale ratios, caption size, line length, trace label hierarchy
- spacing memory: outer margins, gutters, focal/support/provenance zones, slide-role-specific density
- composition memory: cover field, before/after spread, route proof, climax object, close gate
- rhythm memory: six-slide pacing, where to compress, where to enlarge, where to pause
- anti-pattern memory: equal cards, report panels, dense captions, generic dashboards, dark-template reuse
- source-brand sanitization: learn structure without copying visible identity

The memory should produce concrete rules, not advice. For example:

```text
If slide_role = climax:
- headline has at most 9 words
- one native proof object occupies 40-55% of the canvas
- secondary proof detail goes to a side rail
- trace/provenance is below the main visual field
- no more than one accent color carries the transformation
```

Each memory artifact should be deterministic and serializable. A memory record should include:

- memory id
- source record ids
- applicable usecases
- applicable slide roles
- typography rules
- spacing rules
- composition rules
- rhythm rules
- native PPT generation requirements
- forbidden patterns
- QA probes
- release boundary

The generator should consume selected memory ids and write those ids into trace. It should not rely on free-form hidden taste notes that cannot be validated.

## Layer 4: Skill Workflow

The workflow should select memory before the generator draws slides.

Required workflow decisions:

- select commercial usecase
- select source/tutorial records
- select benchmark or reference family
- select typography memory
- select spacing memory
- select composition memory
- select climax strategy
- select visual repair policy
- generate native PPT code
- run layout, delivery, trace, source-brand, and public-blocked gates

Workflow transitions should be explicit and validated. A slide should not move from memory selection to generation unless required usecase, source records, design memory ids, and public-blocked gates are present.

Every generated slide trace should answer:

- which usecase drove the slide
- which source or tutorial records influenced it
- which memory rules were selected
- which workflow decision selected them
- what changed from Run 2.6R
- why control arms could not use the same repair

## Layer 5: Code-Generated Native PPT

Run 2.7 remains code-first. Image generation may support backgrounds or small illustrations, but the primary deck structure must be editable PPT primitives.

Allowed:

- native text boxes
- native shapes
- editable grouped proof objects
- SVG marks or diagrams when they stay editable or traceable
- generated images only as secondary backgrounds or illustrations

Blocked:

- full-slide raster images
- screenshots as the main proof object
- copied source deck visuals
- untraceable visual changes
- manual post-design that cannot be reproduced by the generator

Native checks must continue to verify:

- no full-slide rasterization
- no media fallback in the full arm unless explicitly allowed and traced
- valid PPTX package structure and required slide entries
- layout errors and warnings remain zero
- trace fields connect visual choices to data and workflow

## Experiment Design

Run 2.7 should keep the four-arm comparison:

- prompt-only control
- Run 1.5 baseline
- Run 2.7 full skill
- bad workflow memory

The negative control should be stricter than before. It should receive valid commercial/usecase context but be denied the high-quality design memory and workflow selection layer. This makes it easier to prove that the memory and workflow matter.

Required comparison images:

- Run 2.7 four-arm contact sheet
- full-skill horizontal progression including Run 2.6R and Run 2.7

## Success Criteria

Run 2.7 succeeds only if all are true:

- data quality improves with richer multimodal/tutorial/case records
- memory rules become more concrete than Run 2.6R policy text
- workflow trace shows memory selection before generation
- full arm is visually different from 2.6R for attributable reasons
- control arms cannot access the new design memory/workflow layer
- PPT remains native and code-generated
- layout and delivery QA pass
- result remains public blocked until native render and human review pass

## Non-Goals

- Do not start Run 3.0.
- Do not treat 2.7 as a final public release.
- Do not optimize only color palette or surface style.
- Do not replace PPT generation with image generation.
- Do not copy the identity of public reference brands.
- Do not commit generated `outputs/` artifacts.
- Do not introduce autonomous multi-agent design negotiation.
- Do not claim arbitrary multimodal extraction is fully accurate without source review.

## Expected Output

Run 2.7 should produce:

- a richer commercial usecase artifact
- a thicker multimodal database
- one or more new design memory artifacts
- a stricter workflow decision policy
- a new Run 2.7 four-arm generator
- four local output arms
- two mandatory comparison images
- QA reports
- public-blocked result JSON and Markdown

## Implementation Direction

Run 2.7 should deepen the entire pipeline, not only one slide. The climax slide remains the strongest visual proof target because it is where typography, spacing, composition, rhythm, and workflow attribution are easiest to judge in one image.

The implementation should therefore create whole-pipeline artifacts first, then use the climax slide as the primary quality gate.
