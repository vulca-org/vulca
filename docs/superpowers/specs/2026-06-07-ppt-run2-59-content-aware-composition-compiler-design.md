# PPT Run 2.59 Content-Aware Composition Compiler Design

## Status
approved-for-implementation

## Context
Run 2.58 proved that Run 2.57 product capability content can reach native PPT generation, but the visual result still reads like an engineering report. The root problem is not missing content or missing layout modules. The root problem is that the generator does not compile content burden into a layout capacity decision before drawing.

Run 2.15 already defines useful layout module memory: editorial cover field, product theater stage, before/after route, metric reveal stage, quiet release handoff, and dense evidence compression. Run 2.57 adds product capability content, slide message contracts, and content workflow gates. Run 2.58 connects the content layer to PPT code but hard-codes per-role renderers and lets visible text, QA proof, trace proof, and product explanation compete on the same slide surface.

## Goal
Run 2.59 creates a data/workflow-only content-aware composition compiler. It decides what belongs on the public slide, what belongs in trace/viewer, which layout module can carry the content, and when content must be compressed or split before any Run 2.60 PPT rerun.

## Non-Goals
- Do not generate a new PPT deck in Run 2.59.
- Do not advance to Run 3.0.
- Do not add more visual style variants without content capacity rules.
- Do not copy source layouts, demo decks, video frames, screenshots, or brand assets.

## Design
Run 2.59 adds five artifacts to the existing case pack:

1. `run2_59_content_composition_contracts.json`
   - One record per slide role.
   - Splits content into `public_claim`, `primary_proof_object`, `evidence_chips`, `trace_only_details`, and `speaker_note`.
   - Forces slide-visible content to stay below role-specific capacity.

2. `run2_59_layout_capacity_model.json`
   - One capacity record per layout module.
   - Defines max title lines, max visible words, max evidence chips, primary object area, spacing rule, and forbidden patterns.
   - Reuses Run 2.15 module ids instead of inventing a new visual taxonomy.

3. `run2_59_content_to_layout_selector.json`
   - Maps each slide role to a selected layout module.
   - Records selection reason, content burden, fallback route, and required trace fields for Run 2.60.
   - Prevents `role -> renderer` from being the only decision path.

4. `run2_59_public_surface_trace_policy.json`
   - Separates public slide surface from QA/viewer surface.
   - Public slide must be readable and persuasive.
   - HTML viewer / trace manifest carries inspection details, gates, and internal proof.

5. `run2_59_composition_workflow_gates.json`
   - Defines pass/fail gates for content capacity, module selection, trace separation, and layout collision prevention.
   - Defines the Run 2.60 consumer contract.

The result file `results/run2_59_content_aware_composition_compiler_result.json` records this as a data/workflow-only repair layer. The markdown companion summarizes why 2.59 exists and why 2.60 must consume it before native drawing.

## Viewer Design
The existing `ppt-run-viewer.html` Data / Skill page will show a new Run 2.59 section above Run 2.57:

- "Next data/workflow repair: Run 2.59 content-aware composition compiler"
- output artifact paths
- selected layout modules by role
- public-vs-trace separation policy
- capacity gates and next Run 2.60 consumer contract

The viewer latest generated run remains 2.58 because 2.59 creates no PPT deck.

## Acceptance Criteria
- Tests prove all five Run 2.59 JSON artifacts exist and are internally consistent.
- Tests prove every slide role has a content contract and selected layout module.
- Tests prove selected modules reference Run 2.15 module ids.
- Tests prove public slide content has lower visible word budgets than trace/viewer details.
- Tests prove Run 2.59 creates no PPT deck and requires Run 2.60 to consume the new fields.
- Tests prove the HTML viewer surfaces Run 2.59 without changing latest generated run from 2.58.

## Risks
- If Run 2.59 only documents rules but Run 2.60 does not trace them, the same hard-coded renderer failure will return.
- If visible-word budgets are too low, the deck may look good but feel empty.
- If trace/viewer separation is too aggressive, the public deck may hide necessary product proof.

## Next Step
Implement the data/workflow layer and viewer exposure with TDD. Do not generate Run 2.60 until Run 2.59 is tested and visible in the viewer.
