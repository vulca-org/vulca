# Run 2.83 Workflow Taxonomy Bias Audit

Status: public blocked, not a renderer rerun.

Conclusion: the dominant issue is engineering constraint labels over design motif labels. The existing rigor is useful and should stay, but the system needs a design motif layer between tutorial memory and renderer adapter.

## Preserve
- traceability
- source_availability
- validator_required_files
- public_release_block
- negative_controls
- viewer_metadata_routes
- reproducible_scripts

## Bias By Layer
- source_quality_inventory: Inventory fields prove coverage but do not yet encode motif, spatial recipe, or style family. Impact: Renderer can cite sources but cannot reproduce the visual method behind those sources.
- workflow_gate_matrix: Gate names describe whether a step is allowed, not what aesthetic move must survive the step. Impact: Slides inherit status/gate language and can read as process documentation.
- tutorial_design_moves: Rules are action-safe but not always motif-specific enough to recreate a tutorial look. Impact: The system applies rules like fewer labels, but the page may still look generic.
- visual_grammar_modules: Module IDs are stronger than rectangles, but they still need motif recipes and style parameters. Impact: Pages differ in intent but remain visually similar because motif execution is under-specified.
- renderer_adapter_contracts: Adapter terms can flatten design intent into proof_panel, hero_object, and status-safe primitives. Impact: Outputs become valid native-PPT structures but can read as wireframe diagrams.
- text_binding_strategy: Socket binding controls where text is allowed, but not enough about editorial typography treatment. Impact: Text is safer and denser, but blocks can feel stiff and disconnected from composition.
- text_composition_plan: The plan improves readability but still does not select style-specific text treatments. Impact: Pages gain text hierarchy but may lose the earlier modular, matrix, and overlay visual energy.
- renderer_rerun_results: Rerun success proves generation and viewer availability, not public-grade aesthetic fidelity. Impact: The system may improve content and structure while still missing the desired presentation feel.
- visual_quality_evaluation_loop: Evaluation detects failures after the fact but does not itself teach renderer motif recipes. Impact: The loop prevents false release, but can produce repeated repair cycles with diminishing visual gains.
- validator_and_tests: Tests currently validate fields and gates more readily than motif fidelity and style fit. Impact: The project gets safer but can optimize toward passing schemas instead of design quality.

## Missing Design Taxonomy
- motif_id: Names the concrete design move extracted from a tutorial or case instead of only naming a gate.
- motif_family: Groups related tutorial moves such as matrix, product theater, editorial spread, overlay, or sticker stack.
- layout_recipe: Captures spatial composition as a recipe, not a vague module name.
- spatial_relation: Describes how text, object, evidence, and background relate on the canvas.
- typography_treatment: Preserves the tutorial's headline, paragraph, caption, and label behavior.
- visual_density: Separates sparse premium pages, heavy editorial pages, and modular proof pages.
- style_family: Keeps commercial style direction distinct from engineering status labels.
- scenario_fit: Matches usecase needs such as product pitch, teaching, finance, or technical proof.
- renderer_recipe: Turns design motif into executable native-PPT drawing instructions.
- motif_fidelity_checks: Checks whether the rendered slide still looks like the intended motif.

## Next

Build the design_motif_layer / style router. Keep validator gates, traceability, negative controls, and public blocked release policy intact.
