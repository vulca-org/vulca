# PPT Run 2.61 Narrative Proof Dataset Design

Status: draft-for-user-review.

## Context

Run 2.60 proves that Run 2.59 composition contracts can be consumed before native PPT drawing, but the visible result still misses the target. It is cleaner than earlier engineering-report outputs, yet it feels underpowered: public-slide information is thin, proof objects are abstract, and the visual system is weaker than the older visual-first Run 2.56.

The main failure is not color, shape vocabulary, or a missing styling pass. The failure is that the final generator consumes a compressed contract layer from Run 2.59, while earlier thick records are not directly represented in the slide surface:

- tutorial and multimodal source decompositions from Run 2.8, Run 2.12, and Run 2.18;
- visual module memory from Run 2.15;
- editorial copy and shape text sockets from Run 2.51;
- product capability and slide message contracts from Run 2.57;
- public/trace separation and capacity gates from Run 2.59.

The pipeline has evidence that these layers exist, but Run 2.60 mostly renders `public_claim`, `evidence_chips`, `primary_proof_object`, and trace placeholders. That produces a truthful but thin deck: it proves workflow existence without letting the viewer feel a strong business story or see enough product proof.

## External Reference Lessons

The next repair should follow source-safe patterns from public product and presentation references:

- Apple Events: product launches stage one memorable product moment at a time, with the object or demo moment carrying most of the visual attention.
- Figma Config 2025: product announcements are framed as a lifecycle story from idea to production, not as isolated feature cards.
- Stripe Sessions 2026: a very broad product launch is organized into product families, business outcomes, and specific capabilities rather than one undifferentiated grid.
- Canva design guidance: visual hierarchy, focal point, flow, grid, and typography must organize content before decoration is considered.

These references are inputs for abstraction only. The implementation must not copy brand visuals, source layouts, screenshots, video frames, event graphics, or source copy.

Reference URLs:

- `https://www.apple.com/apple-events/`
- `https://www.figma.com/blog/config-2025-press-release/`
- `https://stripe.com/blog/everything-we-announced-at-sessions-2026`
- `https://www.canva.com/learn/visual-hierarchy/`
- `https://www.canva.com/learn/flow-and-rhythm/`
- `https://www.canva.com/learn/presentation-design/2/`

## Goal

Run 2.61 creates a data/workflow-only narrative proof dataset that sits between the thick source memories and the next generated deck.

The goal is to make the next rerun consume a richer intermediate object than Run 2.59. Each slide should compile:

`reader question -> required answer -> proof payload -> copy units -> visual carrier -> text sockets -> density budget -> source trace -> bad-control probe`

Run 2.61 should make it impossible for the next generator to satisfy the workflow by drawing generic diagrams with thin text. It should require every public slide to have one business action, one dominant visual carrier, and enough concrete proof to answer the slide's reader question.

## Non-Goals

- Do not generate a new PPT deck in Run 2.61.
- Do not advance to Run 3.0.
- Do not claim public release readiness.
- Do not scrape or store copyrighted slide/video frames as reusable assets.
- Do not copy Apple, Figma, Stripe, Canva, or other source-brand visual systems.
- Do not solve the problem by increasing visible word count alone.
- Do not remove trace/viewer separation; improve the public proof layer while keeping raw internals inspectable elsewhere.

## Problem Diagnosis

Run 2.60 has four product-quality failures:

1. **Compression loss**
   - Earlier data layers are summarized too aggressively before rendering.
   - The renderer sees compact claims and chips, not a thick proof payload.

2. **Carrier mismatch**
   - Layout selection chooses a module, but not a slide-specific product action.
   - Shapes become diagrams explaining the system, not objects that demonstrate the system.

3. **Text is not socketed enough**
   - Run 2.51 defines shape text sockets, but Run 2.60 does not directly consume those sockets.
   - Public text becomes floating labels and status boxes instead of integrated editorial copy.

4. **Trace split overcorrects**
   - Moving raw detail to the viewer is correct, but Run 2.60 often replaces detail with a generic placeholder.
   - Public slides need anonymized, synthetic, or summarized proof objects that still feel specific.

## Options Considered

### Option A: Restyle Run 2.60 Directly

This would edit the 2.60 generator to make the slides look more like Run 2.56.

Trade-off: it may improve the screenshot quickly, but it would not prove that the dataset and workflow improved. It risks another manual styling pass.

### Option B: Add More Tutorial And Video Sources First

This would expand the source database before changing the compiler.

Trade-off: useful later, but not sufficient now. The current problem is not only source volume. The current problem is that source detail is not reaching the renderer in a useful form.

### Option C: Build Run 2.61 Narrative Proof Dataset First

This creates a richer intermediate dataset before another generated rerun. It fuses text, evidence, visual carrier selection, socket obligations, source references, and bad-control probes into one per-slide contract.

This is the chosen path because it repairs the pipeline at the point where visual and text data currently separate.

## Chosen Design

Run 2.61 adds a narrative proof dataset and selector layer. It remains a data/workflow repair pass with no new PPT deck.

It should add these artifacts:

- `docs/product/ppt-run2-data-skill-quality/run2_61_narrative_proof_dataset.json`
- `docs/product/ppt-run2-data-skill-quality/run2_61_story_to_visual_carrier_selector.json`
- `docs/product/ppt-run2-data-skill-quality/run2_61_text_socket_fusion_contracts.json`
- `docs/product/ppt-run2-data-skill-quality/run2_61_source_to_public_proof_policy.json`
- `docs/product/ppt-run2-data-skill-quality/run2_61_narrative_workflow_gates.json`

It should add result documentation:

- `docs/product/ppt-run2-data-skill-quality/results/run2_61_narrative_proof_dataset_result.json`
- `docs/product/ppt-run2-data-skill-quality/results/run2_61_narrative_proof_dataset_result.md`

It should update the HTML viewer data/workflow audit section so reviewers can inspect:

- source layers consumed;
- per-slide reader question and required answer;
- proof payload density;
- selected visual carrier;
- selected text sockets;
- public proof replacement for trace-only detail;
- bad-control failure mode;
- next Run 2.62 consumer contract.

## Artifact 1: Narrative Proof Dataset

`run2_61_narrative_proof_dataset.json` defines one record per slide role.

Each record must include:

- `narrative_proof_id`
- `role`
- `selected_usecase_id`
- `source_run_ids`
- `reader_question`
- `required_answer`
- `business_action`
- `public_takeaway`
- `proof_payload`
- `copy_units`
- `source_refs`
- `trace_only_payload`
- `public_proof_replacement`
- `density_budget`
- `forbidden_surface_terms`
- `bad_control_probe`
- `next_rerun_obligation`

`proof_payload` must be specific enough to draw from. It should include at least:

- `primary_evidence_object`
- `secondary_evidence_objects`
- `product_mechanism`
- `business_consequence`
- `before_state`
- `after_state`
- `what_the_viewer_should_notice`

`copy_units` must separate:

- `headline`
- `subhead`
- `proof_badges`
- `annotations`
- `state_labels`
- `speaker_note`

`density_budget` must include:

- maximum public visible words;
- minimum public proof objects;
- maximum trace placeholders;
- minimum visual carrier area;
- maximum free-floating labels;
- minimum socket-bound copy units.

## Artifact 2: Story To Visual Carrier Selector

`run2_61_story_to_visual_carrier_selector.json` maps each narrative proof record to a visual carrier.

The selector must choose the carrier from existing memory where possible:

- Run 2.15 layout modules;
- Run 2.51 shape text socket archetypes;
- Run 2.56 visual-first role renderer strengths;
- Run 2.59 capacity and trace separation rules.

Each selector record must include:

- `selector_id`
- `role`
- `source_narrative_proof_id`
- `selected_layout_module_id`
- `selected_socket_memory_id`
- `visual_carrier_type`
- `carrier_reason`
- `visual_weight_requirement`
- `text_socket_requirement`
- `fallback_if_over_capacity`
- `bad_control_probe`

Allowed `visual_carrier_type` values:

- `product_surface`
- `operating_loop`
- `before_after_delta`
- `workspace_inspection`
- `climax_result_object`
- `release_handoff`

The selector must reject a carrier when the slide cannot show a business action. A generic workflow diagram is not enough.

## Artifact 3: Text Socket Fusion Contracts

`run2_61_text_socket_fusion_contracts.json` binds copy units to actual text sockets.

Each contract must include:

- `fusion_contract_id`
- `role`
- `source_socket_memory_id`
- `source_copy_units`
- `socket_bindings`
- `fit_rules`
- `overflow_behavior`
- `surface_terms_policy`
- `trace_fields_for_next_rerun`

Each `socket_bindings` item must include:

- `copy_unit_key`
- `socket_id`
- `owning_shape_role`
- `character_budget`
- `max_lines`
- `minimum_font_size`
- `placement_rule`
- `failure_status`

The next generator must fail if it places a required public copy unit without a Run 2.61 socket binding.

## Artifact 4: Source To Public Proof Policy

`run2_61_source_to_public_proof_policy.json` defines how rich source detail reaches a public slide without leaking raw internals or copying source materials.

The policy must define:

- allowed source abstraction types;
- forbidden source copying behaviors;
- anonymized proof object rules;
- synthetic proof object rules;
- trace-only retention rules;
- public replacement rules;
- source URL and local artifact attribution fields.

Public proof replacement examples:

- Replace raw source inventory with a compact "source pack" object.
- Replace full workflow gate list with one pass/fail inspection board.
- Replace raw competitor prose with one before/after route break.
- Replace a real screenshot with a native editable proxy object that shows the same product action.

## Artifact 5: Narrative Workflow Gates

`run2_61_narrative_workflow_gates.json` defines gates that must pass before Run 2.62 native drawing.

Required gates:

- every slide role has a narrative proof record;
- every narrative proof record answers its reader question;
- every proof payload has a business action and a product mechanism;
- every record has at least two source references;
- every role has a selected visual carrier;
- every required copy unit has a socket binding;
- public proof replacement exists for trace-only detail;
- bad control is defined per role;
- next-rerun trace fields are explicit.

## Data Flow

Run 2.61 should compile from existing records:

1. Select one commercial usecase from `commercial_usecase_bank.json`.
2. Pull relevant tutorial and multimodal concepts from Run 2.8, Run 2.12, and Run 2.18.
3. Pull layout modules from Run 2.15.
4. Pull copy and socket obligations from Run 2.51.
5. Pull product message contracts from Run 2.57.
6. Pull public/trace split and capacity rules from Run 2.59.
7. Emit Run 2.61 narrative proof records, carrier selector records, socket fusion contracts, source policy, and workflow gates.
8. Expose the layer in the viewer.
9. Require Run 2.62 to consume Run 2.61 before drawing native PPT.

## Viewer Design

The existing `ppt-run-viewer.html` should show Run 2.61 as a data/workflow layer, not a generated deck.

Add a section to Data / Skill and Data/Workflow Audit:

- "Run 2.61 narrative proof dataset"
- "Why 2.60 felt thin"
- "Source layers consumed"
- "Per-slide narrative proof table"
- "Visual carrier selector"
- "Text socket fusion"
- "Public proof replacement"
- "Next Run 2.62 consumer contract"

The viewer latest generated run remains 2.60 until Run 2.62 creates a deck.

## Acceptance Criteria

- Tests prove all Run 2.61 artifacts exist.
- Tests prove all six slide roles have narrative proof records.
- Tests prove each record has `reader_question`, `required_answer`, `business_action`, `proof_payload`, `copy_units`, `density_budget`, and `source_refs`.
- Tests prove every role maps to an existing Run 2.15 layout module and an existing Run 2.51 socket memory record.
- Tests prove every required copy unit has a socket binding.
- Tests prove source references include at least two prior run ids or external reference ids per role.
- Tests prove trace-only detail has a public proof replacement.
- Tests prove a bad-control probe exists per role.
- Tests prove the HTML viewer exposes Run 2.61 while keeping latest generated run at 2.60.
- Tests prove Run 2.61 creates no PPT deck.

## Risks

- If Run 2.61 becomes another summary layer, Run 2.62 will repeat the 2.60 failure.
- If proof payloads are too dense, the next deck may return to report-like clutter.
- If public proof replacements are too abstract, the deck will still feel empty.
- If socket bindings are only documented but not enforced, text will drift back into floating labels.
- If visual carriers are selected by role only, not by business action, slides will continue to look similar.

## Next Step

After this spec is reviewed, write an implementation plan for Run 2.61. Implementation should be TDD-first and should create the data artifacts, result docs, viewer exposure, and tests before any Run 2.62 PPT generation.
