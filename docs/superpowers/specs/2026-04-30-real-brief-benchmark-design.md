# Real Brief Benchmark Harness Design

**Date:** 2026-04-30
**Status:** Approved design for implementation planning
**Branch:** `codex/real-brief-benchmark-design`
**Scope:** Phase 1 benchmark harness, with artifacts designed for Phase 2 workflow integration and Phase 3 review surface.

## Decision

Build Phase 1 as a **script-based real-brief benchmark harness**, but design its artifacts as long-lived product contracts.

The implementation should not only compare generated images. It should test whether Vulca can turn realistic creative work into a decision-ready and production-ready package:

```text
real brief
-> structured brief
-> decision package
-> production package
-> A/B/C/D workflow comparison
-> review schema + optional preview surface
-> summary
```

Phase 1 is not the final workflow. It creates evidence and stable artifacts that Phase 2 can route into `/visual-discovery -> /visual-brainstorm -> /visual-spec -> /visual-plan -> /evaluate`, and that Phase 3 can render in a stronger Review/Studio surface.

## Why This Replaces The Old Prompt Test

The cultural-term benchmark used broad prompts such as "premium tea packaging with xieyi restraint." Strong image models can make those prompts look good even when the workflow adds little value. That makes evaluation ambiguous.

The new benchmark must use real constraints from public creative briefs and RFPs:

- concrete client/context;
- target audience;
- budget and timeline;
- required deliverables;
- format and production constraints;
- legal/IP/AI usage constraints;
- review criteria;
- risks and avoid lists.

Vulca should win on decision usefulness, constraint handling, structural control, and production readiness. It does not need to win on raw image beauty.

## Phase Order

### Phase 1: Benchmark-First Harness

Implement now.

The harness reads curated real-brief fixtures and writes dry-run artifacts by default. It may later support explicit real-provider opt-in, but no live provider call should happen unless the user passes a cost-bearing flag and local credentials.

Phase 1 outputs:

- `structured_brief.json`
- `decision_package.md`
- `production_package.md`
- A/B/C/D condition packages
- `workflow_handoff.json`
- `review_schema.json`
- `human_review.html`
- `summary.md`

### Phase 2: Workflow-First Adapter

Design now, implement later.

Phase 2 consumes `workflow_handoff.json` and turns a real brief into official Vulca workflow artifacts:

```text
structured_brief.json
-> discovery seed
-> proposal.md
-> design.md
-> plan.md
-> evaluation.md/evaluation.json
```

This adapter should preserve the existing human gates in `/visual-brainstorm`, `/visual-spec`, and `/visual-plan`. It should not silently auto-finalize proposal/design/plan artifacts.

### Phase 3: Review Surface / Studio

Design now, implement after artifact stability.

The review surface consumes the Phase 1/2 artifacts and displays:

- source brief;
- structured brief;
- decision package;
- production package;
- A/B/C/D conditions;
- prompts and images;
- evaluations;
- human scores;
- final recommendation and next action.

The first version may be local HTML, but the data contract must not be HTML-specific.

## Real Brief Fixtures

Phase 1 should ship five fixtures first:

1. `gsm-community-market-campaign`
   - Source: Rogers Park Business Alliance / Glenwood Sunday Market marketing and creative services RFP.
   - Tests campaign systems, Canva-editable templates, social channels, banners, stickers, tote concepts, real photography, and brand consistency.

2. `seattle-polish-film-festival-poster`
   - Source: Seattle Polish Film Festival poster submission brief.
   - Tests poster layout compliance, required text, logo band, margins, print-readiness, and cultural specificity.

3. `model-young-package-unpacking-taboo`
   - Source: Model Young Package 2026 "Unpacking Taboo."
   - Tests packaging concept, paper/cardboard structure, unboxing flow, functionality, manufacturability, sustainability, and responsible tone.

4. `erie-botanical-gardens-public-art`
   - Source: Erie County / Buffalo and Erie County Botanical Gardens public art call.
   - Tests artist proposal structure, site response, materials, durability, installation, maintenance, budget assumptions, and public meaning.

5. `music-video-treatment-low-budget`
   - Source: Creative Commission music-video brief.
   - Tests director treatment, low-budget execution, mood frames, scene beats, production constraints, and AI-use disclosure.

The fixture set intentionally spans brand/campaign, poster/layout, packaging/product, artist proposal, and director treatment workflows.

## Source Hygiene

The source list was checked on 2026-04-30. Several opportunities have deadlines before or near that date, so fixtures must be treated as historical/internal benchmark material unless a source is revalidated at run time.

Implementation requirements:

- store `source.retrieved_on` and `source.url` with every fixture;
- store `source.deadline` when the source publishes one;
- store `source.usage_note` as `Internal benchmark only` by default;
- mark expired opportunities as `simulation_only: true`;
- mark AI-prohibited sources as `ai_policy: prohibited_for_submission` and keep generated outputs out of any submission-ready claim;
- prefer primary source pages/PDFs over aggregator summaries; use aggregators only as backup notes.

## Fixture Schema

Each fixture should be structured data, not only markdown prose.

Required fields:

```json
{
  "schema_version": "0.1",
  "slug": "seattle-polish-film-festival-poster",
  "title": "Seattle Polish Film Festival 2026 Poster",
  "source": {
    "url": "https://www.polishfilms.org/submit-a-poster",
    "retrieved_on": "2026-04-30",
    "usage_note": "Internal benchmark only"
  },
  "client": "Seattle Polish Film Festival",
  "context": "Poster concept for the 34th festival edition.",
  "audience": ["festival attendees", "Polish and American cinema communities"],
  "deliverables": [
    {
      "name": "poster concept",
      "format": "11 x 17 in vertical",
      "channel": "print/digital",
      "required": true
    }
  ],
  "constraints": ["required text must be present", "bottom sponsor band reserved"],
  "budget": "not specified by source",
  "timeline": "source-specific contest deadline",
  "required_outputs": ["decision_package", "production_package"],
  "ai_policy": "allowed | prohibited_for_submission | unspecified",
  "risks": ["broken text rendering", "unsafe margins", "generic national symbols"],
  "avoid": ["illegible typography", "missing sponsor area"],
  "evaluation_dimensions": ["brief_compliance", "constraint_handling"]
}
```

For sources that prohibit AI submissions, the fixture must mark the run as simulation-only. The harness must not imply that outputs are submission-ready.

## Output Artifact Tree

Default output root:

```text
docs/product/experiments/real-brief-results/<date>-<slug>/
  source_brief.md
  structured_brief.json
  decision_package.md
  production_package.md
  workflow_handoff.json
  review_schema.json
  conditions/
    A-one-shot.md
    B-structured-brief.md
    C-vulca-planning.md
    D-vulca-preview-iterate.md
  prompts/
    A.txt
    B.txt
    C.txt
    D.txt
  images/
    README.md
  evaluations/
    README.md
  human_review.html
  summary.md
  manifest.json
```

Dry-run outputs must be complete enough to inspect without images. `images/README.md` and `evaluations/README.md` explain that no image quality conclusion is available until real-provider generation and evaluation run.

## Condition Design

The old cultural-term A/B/C/D conditions should be replaced.

### A. One-Shot Model Baseline

Raw real brief condensed into a single ask. This represents what a user might paste into a strong model directly.

Purpose: measure what one-click or chat-first generation can already do.

### B. Structured Brief Baseline

Same brief normalized into:

- client;
- context;
- audience;
- deliverables;
- constraints;
- success criteria;
- avoid list.

Purpose: measure the value of structure alone.

### C. Vulca Planning Workflow

Adds Vulca-style planning artifacts:

- ambiguity detection;
- missing questions;
- cultural/taste/intent analysis;
- 2-3 creative directions;
- direction card;
- visual operations;
- evaluation rubric.

Purpose: measure whether Vulca makes the user's intent clearer before generation.

### D. Vulca Preview-And-Iterate Workflow

Adds preview-oriented planning:

- rough thumbnail prompts;
- per-direction preview plan;
- critique pass against the real brief;
- refined direction;
- final comp prompt;
- editability/redraw notes.

Purpose: measure the higher-value loop: chat while demonstrating, then deepen the chosen direction.

## Decision Package Contract

`decision_package.md` is for the client, artist, director, or designer to choose a direction.

Required sections:

- brief digest;
- assumptions;
- missing questions;
- 2-3 creative directions;
- direction rationale;
- risks and rejected approaches;
- recommended direction;
- decision checklist.

This package should be readable without knowing Vulca internals.

## Production Package Contract

`production_package.md` is for downstream execution.

Required sections:

- selected direction;
- prompt packet;
- visual operations;
- layout/structure constraints;
- channel/deliverable constraints;
- preview or thumbnail plan;
- evaluation checklist;
- editability/reusability notes;
- redraw/layer notes for future v0.22+ integration;
- next iteration plan.

This package may reference existing Vulca capabilities but must not require the redraw branch to be merged.

## Workflow Handoff Contract

`workflow_handoff.json` is the Phase 2 bridge.

Required top-level shape:

```json
{
  "schema_version": "0.1",
  "slug": "seattle-polish-film-festival-poster",
  "structured_brief_path": "structured_brief.json",
  "visual_discovery_seed": {},
  "visual_brainstorm_seed": {},
  "visual_spec_seed": {},
  "visual_plan_seed": {},
  "evaluate_seed": {},
  "human_gate_required": true
}
```

Phase 1 only writes the seed data. Phase 2 will teach the official `/visual-*` workflows to consume or import this handoff.

Important invariant: `human_gate_required` remains true. Benchmark automation must not bypass approval gates that current skills require.

## Review Schema Contract

`review_schema.json` is the Phase 3 bridge.

Default dimensions use a 0/1/2 scale:

1. `brief_compliance`
2. `audience_fit`
3. `deliverable_fit`
4. `constraint_handling`
5. `cultural_taste_specificity`
6. `structural_control`
7. `editability_reusability`
8. `production_realism`
9. `risk_avoidance`
10. `decision_usefulness`

Winning condition:

- A/B may win visual attractiveness.
- C/D should win decision usefulness, constraint handling, next-step clarity, and production realism.
- If C/D do not win those, Vulca's product claim is weak for that brief type.

## Human Review Surface

Phase 1 should generate a lightweight `human_review.html` from `review_schema.json` and manifest data.

Requirements:

- group by brief and condition;
- show condition descriptions;
- show decision and production package links;
- expose 0/1/2 scoring controls;
- persist local browser notes;
- export JSON;
- avoid embedding provider keys or live endpoint information.

This HTML is a prototype of Phase 3, not the final product.

## Internal Vulca Tool Usage

Phase 1 should reuse existing internals where possible:

- `vulca.discovery.profile.infer_taste_profile` for early taste/domain signals;
- `vulca.discovery.cards.generate_direction_cards` for Vulca-style direction candidates;
- `vulca.discovery.prompting.compose_prompt_from_direction_card` for prompt assembly;
- `vulca.studio.Brief` as a compatibility bridge to existing Studio concepts;
- `vulca.studio.eval_criteria` for L1-L5 criteria generation or fallback;
- provider interfaces only behind explicit real-provider opt-in;
- `/evaluate` concepts for future image scoring after images exist.

Phase 1 must not:

- change redraw internals;
- depend on v0.22 mask refinement;
- bypass `/visual-*` human gates;
- require network calls during tests;
- write secrets to artifacts.

## CLI Design

Add a new script rather than overloading the cultural-term harness:

```bash
PYTHONPATH=src python3 scripts/real_brief_benchmark.py \
  --date 2026-04-30 \
  --slug all \
  --output-root docs/product/experiments/real-brief-results
```

Flags:

- `--slug <slug|all>`
- `--date YYYY-MM-DD`
- `--output-root <path>`
- `--real-provider`
- `--provider openai|gemini|comfyui`
- `--max-images <n>`
- `--write-html-review`

Default mode is dry-run. Real-provider mode must fail closed without credentials and must not serialize credentials.

## Error Handling

- Unknown slug: fail with known slug list.
- Missing fixture field: fail with field name and fixture path.
- Unsafe slug: reject path traversal, absolute paths, `..`, and shell-like names.
- Real-provider requested without credentials: fail before writing partial image artifacts.
- AI-prohibited source: allow simulation artifacts, but mark `ai_policy` and `summary.md` clearly.
- HTML export failure: still write core markdown/json artifacts and mark review surface as unavailable.
- Evaluation absent: write `evaluations/README.md` and keep `summary.md` honest.

## Testing Plan

Unit tests:

- fixture schema validation;
- slug safety;
- A/B/C/D condition generation;
- artifact tree creation;
- `workflow_handoff.json` schema;
- `review_schema.json` schema;
- dry-run no-provider behavior;
- real-provider fail-closed behavior without credentials;
- secret scanning for generated artifacts.

Golden tests:

- one fixture dry-run produces stable key files;
- `summary.md` contains no quality conclusion in dry-run;
- HTML review includes all condition ids and rubric dimensions.

Existing regression tests to keep green:

- visual discovery benchmark tests;
- visual discovery artifact tests;
- visual discovery cards/types tests.

## Implementation Boundaries

Keep Phase 1 implementation tightly scoped:

- add real-brief fixture data;
- add harness code;
- add artifact writers;
- add tests;
- add docs update pointing to the benchmark.

Do not implement Phase 2 workflow import or Phase 3 Studio in the first implementation PR. Only design the artifacts so those phases can consume them without reshaping the output tree.

## Open Questions

- Whether real brief fixtures should live under `docs/product/experiments/real-brief-fixtures/` or `src/vulca/real_brief/fixtures/`.
- Whether Phase 1 should generate `proposal_seed.md` files for easier `/visual-brainstorm` import in Phase 2.
- Whether music-video treatment should remain in the same fixture set even though current `/visual-brainstorm` explicitly excludes video; for Phase 1 benchmark it is valuable, but Phase 2 needs a video-specific adapter or a scoped redirect.

## Sources

- Glenwood Sunday Market marketing/creative services RFP: `https://rpba.org/wp-content/uploads/2026/02/Marketing-Creative-Services-for-GSM-RFP-2026.pdf`
- ImageOut 2026 Theme Contest: `https://imageout.org/contest/`
- Seattle Polish Film Festival poster brief: `https://www.polishfilms.org/submit-a-poster`
- Model Young Package 2026: `https://www.modelgroup.com/language-masters/en/model-young-package.html`
- Erie County Botanical Gardens public art call: `https://www4.erie.gov/publicart/2026-call-artists-buffalo-and-erie-county-botanical-gardens`
- Los Angeles County Sanitation Districts graphic design RFP: `https://www.lacsd.org/Home/Components/RFP/RFP/853/488`
- Charlotte-Mecklenburg Storm Water Services summary: `https://govtribe.com/opportunity/state-local-contract-opportunity/creative-services-for-storm-water-services-fy27rfp02`
- Creative Commission music-video brief: `https://creative-commission.com/briefs/brief-10642`
