# PPT Run 2.51 Editorial Copy And Shape Text Sockets Design

Status: draft-for-user-review.

## Context

Run 2.50 is the latest generated rerun in the PPT product experiment. It proves the suspected workflow bug is mostly fixed: the full arm consumes Run 2.49 readability memory, content evidence density memory, and editorial renderer gates before native PPT drawing.

The visible result is still not public-video-grade. The full arm is richer than the controls, but it still reads like an engineering experiment: text feels stiff, many shapes still behave like boxes, and proof objects are not yet composed as editorial surfaces.

Run 2.51 stays inside the same five-layer loop:

`real commercial usecase -> multimodal tutorial/case database -> design memory -> skill workflow -> code-generated native PPT -> baseline/ablation/evaluation`

It does not advance to Run 3.0. It does not claim public readiness. It thickens the next missing layer before another generator rerun.

## Goal

Run 2.51 should make the data-to-slide translation more editorial.

The target is not "add more shapes" or "change colors again." The target is to define two executable layers that the next full arm must consume:

1. an editorial copy compiler that converts raw evidence and workflow records into short public-facing display copy;
2. a shape text socket system that makes every major shape own a semantic text position, size budget, and fit rule.

The next rerun should then prove that these layers changed the visible surface and that the negative control without them remains stiff.

## Problem Diagnosis

Run 2.50 improved evidence density, but it still has four product-quality failures:

- Raw workflow language leaks into public-facing slide text.
- Text blocks are placed as labels around shapes instead of being integrated into a visual composition.
- Non-square surfaces exist, but too many still behave like bordered rectangles or equal cards.
- Word-count and proof-object counts are verified, but character-width fit, text hierarchy, and semantic placement are not verified.

That means the renderer can truthfully consume data and still produce awkward slides. Run 2.51 must repair the last translation layer between evidence and visual surface.

## Options Considered

### Option A: Directly Restyle The Run 2.50 Generator

This would edit the 2.50 drawing functions to make the deck prettier.

Trade-off: it might produce a better screenshot quickly, but it would not prove product learning. It risks another pass where the deck changes because of manual styling, not because the database and workflow became better.

### Option B: Add More Multimodal Tutorial Records First

This would continue expanding tutorial/video/case data before touching renderer rules.

Trade-off: useful later, but source volume is not the current bottleneck. The current bottleneck is that evidence does not become editorial copy and semantic shape placement.

### Option C: Build Run 2.51 Editorial Copy And Shape Socket Memories First

This adds a data/workflow layer before the next rerun. It defines copy roles, text fit budgets, visual archetypes, geometry constraints, and trace gates.

This is the recommended path because it converts "better taste" into a product mechanism that can be tested, ablated, and reused.

## Chosen Design

Run 2.51 is a same-stage data/workflow repair pass before a generated rerun.

This pass prepares the repair contract. It does not visually validate the repair by itself because it creates no new deck. Visual validation is deferred to the next generated rerun that consumes these artifacts.

It should add these core artifacts:

- `docs/product/ppt-run2-data-skill-quality/run2_51_editorial_copy_memory.json`
- `docs/product/ppt-run2-data-skill-quality/run2_51_shape_text_socket_memory.json`
- `docs/product/ppt-run2-data-skill-quality/run2_51_renderer_archetype_workflow_gates.json`

It should add result documentation:

- `docs/product/ppt-run2-data-skill-quality/results/run2_51_editorial_shape_text_repair_result.json`
- `docs/product/ppt-run2-data-skill-quality/results/run2_51_editorial_shape_text_repair_result.md`

It should update viewer/reporting so Run 2.51 appears as a data/workflow layer, not as a new PPT deck.

## Editorial Copy Memory

The editorial copy memory turns raw evidence into display copy bundles.

Each memory record should include:

- `copy_memory_id`
- `role`
- `selected_usecase_id`
- `source_run_ids`
- `raw_evidence_inputs`
- `public_surface_copy_bundle`
- `trace_only_copy_bundle`
- `copy_fit_budget`
- `forbidden_surface_terms`
- `business_claim_preservation_check`
- `bad_control_probe`
- `next_rerun_obligation`

The `public_surface_copy_bundle` must separate at least these roles:

- `headline`: maximum 7 words and maximum 48 visible characters.
- `subline`: maximum 18 words and maximum 120 visible characters.
- `proof_nuggets`: 2 to 4 items; each maximum 8 words and maximum 54 visible characters.
- `annotations`: 2 to 5 items; each maximum 6 words and maximum 42 visible characters.
- `state_labels`: 2 to 5 items; each maximum 4 words and maximum 28 visible characters.

The copy compiler must not simply truncate raw text. It must rewrite evidence into display language while preserving the business claim. Raw workflow names, run ids, memory ids, audit ids, and internal gate names belong in trace fields, not public slide text.

Forbidden public-surface terms include:

- `run2`
- `memory`
- `workflow gate`
- `trace`
- `audit`
- `negative control`
- `public blocked`
- file names and schema ids

These terms may remain in manifests, result docs, HTML viewer diagnostics, and trace panels.

## Shape Text Socket Memory

The shape text socket memory defines where text can live inside each semantic visual archetype.

Each memory record should include:

- `socket_memory_id`
- `role`
- `primary_archetype`
- `shape_primitives`
- `socket_contracts`
- `geometry_constraints`
- `copy_role_bindings`
- `fit_checks`
- `forbidden_layout_patterns`
- `bad_control_probe`
- `next_rerun_obligation`

Every socket contract should include:

- `socket_id`
- `copy_role`
- `owning_shape_id`
- `placement_rule`
- `max_lines`
- `font_size_range`
- `character_budget`
- `minimum_padding`
- `alignment`
- `overflow_policy`

Text should be inside, attached to, or optically locked to a semantic shape. It should not float as generic explanation beside a decorative block.

## Slide Archetypes And Sockets

Run 2.51 should define six role-specific archetypes.

| Role | Primary archetype | Required text sockets |
| --- | --- | --- |
| Cover | poster stage | headline plane, hero-object caption, proof badge, source-boundary whisper |
| Setup | route map | failure-path title, route node labels, break-risk marker, selected-route claim |
| Contrast | before-after lens | before caption, after claim, delta marker, implication line |
| Proof | workspace surface | workspace title, lane labels, proof nuggets, inspectable object captions |
| Climax | exploded hero object | result headline, exploded proof tags, release boundary tag, memory route label |
| Close | decision room | decision headline, gate labels, next-action strip, residual-blocker caption |

Each slide must expose one dominant archetype. It may use secondary accents, but it must not become a mixed dashboard of unrelated shapes.

## Semantic Shape Vocabulary

The vocabulary should use shape roles, not decorative names.

Required primitive families:

- `stage`: full-width or poster-scale field with a clear headline plane.
- `route_path`: connected path or stepped route with node sockets.
- `lens`: circular, oval, or cropped-window comparison surface.
- `exploded_layers`: separated stacked layers connected by callouts.
- `bracket_callout`: bracket, brace, or leader that anchors annotation text.
- `ribbon`: horizontal or diagonal strip for state or release labels.
- `stamp_badge`: compact proof marker or status marker.
- `spotlight`: clipped light field or contrast field that creates focus.
- `depth_stack`: offset layers with visible depth and non-equal scale.
- `decision_wall`: grouped handoff surface with gate/action sockets.

Each primitive must include explicit geometry constraints. Naming a primitive `lens` is not enough. For example:

- A `lens` must use an oval, circle, clipped window, or rounded mask-like surface, not a plain rectangle.
- A `route_path` must include connector geometry and at least three node sockets, not three equal cards.
- `exploded_layers` must include offset position, scale separation, and connector lines.
- A `ribbon` must be visibly narrower than the main surface and may be diagonal or edge-bound.
- A `depth_stack` must include at least three unequal layers with offset shadows or overlap.

## Geometry And Fit Gates

Run 2.51 must add stricter gates than Run 2.49.

Required per-slide checks:

- at least 3 non-card semantic primitives;
- no more than 1 equal-card cluster;
- primary surface is not a square block grid;
- at least 4 and no more than 7 socket-bound public text elements;
- no public text element exceeds its character budget;
- no public text element exceeds its max-line budget;
- every proof nugget is bound to a proof object, path node, badge, callout, or layer tag;
- headline and subline are not placed in the same visual weight as proof labels;
- trace-only terms do not appear on the public slide surface.

If the artifact tool cannot measure pixel width directly, the first implementation may use a conservative character-width proxy. The result must state this limitation and keep public release blocked.

## Workflow Contract

Run 2.51 should enforce this order:

1. Select slide role and selected commercial usecase.
2. Load Run 2.49 readability and density obligations.
3. Compile public display copy from raw evidence.
4. Select one slide archetype.
5. Select semantic shape primitives for that archetype.
6. Bind copy roles into shape text sockets.
7. Run geometry, text fit, and forbidden-term gates.
8. Record trace fields for the next generated rerun.

The generator must not draw public text until copy memory and socket memory have both passed.

## Trace Contract

The next full-arm rerun must record these fields for every slide:

- `run2_51_editorial_copy_memory_id`
- `run2_51_shape_text_socket_memory_id`
- `run2_51_renderer_archetype_gate_id`
- `run2_51_primary_archetype`
- `run2_51_public_surface_copy_status`
- `run2_51_text_socket_placement_status`
- `run2_51_shape_vocabulary_status`
- `run2_51_character_fit_status`
- `run2_51_forbidden_surface_terms_count`
- `run2_51_equal_card_cluster_count`
- `run2_51_semantic_primitive_count`

The negative control may reuse Run 2.49 or Run 2.50 context, but it must fail if it lacks Run 2.51 copy memory ids, socket memory ids, and archetype gate ids.

## Viewer And Reporting

The HTML viewer should show Run 2.51 as a data/workflow layer in the Data / Skill area.

The result report should make these boundaries explicit:

- Run 2.51 creates no new PPT deck.
- Run 2.51 is not a visual success claim by itself.
- The new contribution is the data-to-public-copy and shape-to-text-socket contract.
- The next generated rerun must prove actual consumption.
- Public release remains blocked.

The viewer should also list the six archetypes and a compact table of copy budgets so the user can inspect what the next rerun is supposed to obey.

## QA

Required checks for the data/workflow pass:

- Schema validation tests for all three Run 2.51 JSON artifacts.
- Tests that all three Run 2.51 artifacts exist and validate.
- Tests that every role has one editorial copy memory record.
- Tests that every role has one shape text socket memory record.
- Tests that every role maps to one primary archetype and at least four socket contracts.
- Tests that public copy bundles respect word and character budgets.
- Dry-run copy translation tests using Run 2.50 source data to confirm the copy compiler can compress raw evidence without dropping the slide's core business claim.
- Tests that forbidden public-surface terms are absent from public copy.
- Tests that semantic primitives include explicit geometry constraints.
- Tests that gate records require trace fields and bad-control probes.
- Tests that result docs and viewer references describe Run 2.51 as data/workflow-only.
- `git diff --check`.

Required checks for the later generated rerun:

- `node --check` for the new generator.
- Focused pytest coverage for trace fields, copy consumption, socket consumption, and bad-control failure.
- Four-arm contact sheet generation.
- Full-skill-series comparison image generation.
- Browser inspection of the HTML viewer.
- Gemini artifact review of the four-arm sheet.
- Gemini artifact review of the full-skill series.

## Non-Goals

- Do not advance to Run 3.0.
- Do not claim public readiness.
- Do not create a new PPT deck in the 2.51 data/workflow pass.
- Do not copy source screenshots, source layouts, logos, video frames, audio, full transcripts, or brand marks.
- Do not replace native editable PPT text and shapes with a full-slide raster image.
- Do not solve the issue by adding more boxes, more colors, larger text, or denser labels.
- Do not expose workflow proof as public slide copy.

## Risks And Mitigations

Risk: semantic shape names still render as rectangles.

Mitigation: every primitive must include geometry constraints and tests must reject primitive records without explicit non-box behavior.

Risk: word limits still allow awkward line breaks.

Mitigation: copy budgets must include both word count and character count. The generator must record line/fit status before claiming the slide passed.

Risk: too many primitive families create visual chaos.

Mitigation: each slide gets one primary archetype and 3 to 5 semantic primitives. Extra primitives are rejected unless they own a required text socket.

Risk: copy compression removes evidence.

Mitigation: raw evidence remains in trace-only fields, while public copy must preserve one business claim per slide and link back to source evidence ids.

## Success Criteria

Run 2.51 is successful if:

1. The copy memory, socket memory, and archetype gate artifacts exist and validate.
2. Every slide role has public copy budgets, socket contracts, and geometry constraints.
3. Forbidden workflow terms are routed out of public copy and into trace-only fields.
4. The next rerun has concrete fields to prove consumption and ablate against a bad control.
5. The spec and result docs state that visual repair is not validated until the later generated rerun consumes the 2.51 artifacts.
6. The project remains public blocked until the later generated deck passes visual review, render inspection, and human approval.
