#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"
RESULT_JSON = PACK / "results" / "run2_83_workflow_taxonomy_bias_audit.json"
RESULT_MD = PACK / "results" / "run2_83_workflow_taxonomy_bias_audit.md"

CONSUMED_SOURCES = [
    "docs/product/ppt-run2-data-skill-quality/skill_workflow.json",
    "docs/product/ppt-run2-data-skill-quality/run2_8_workflow_gate_matrix.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_42_content_visual_asset_quality_audit.json",
    "docs/product/ppt-run2-data-skill-quality/run2_43_editorial_composition_typography_memory.json",
    "docs/product/ppt-run2-data-skill-quality/run2_49_readability_memory.json",
    "docs/product/ppt-run2-data-skill-quality/run2_51_shape_text_socket_memory.json",
    "docs/product/ppt-run2-data-skill-quality/run2_61_text_socket_fusion_contracts.json",
    "docs/product/ppt-run2-data-skill-quality/run2_64_text_fit_renderer_gates.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_source_quality_audit.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_tutorial_to_design_moves.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_visual_grammar_modules.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_renderer_adapter_contracts.json",
    "docs/product/ppt-run2-data-skill-quality/run2_73_text_binding_strategy.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_74_visual_quality_evaluation.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_76_visual_quality_evaluation.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_78_visual_quality_evaluation.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_80_visual_quality_evaluation.json",
    "docs/product/ppt-run2-data-skill-quality/run2_81_text_composition_typography_plan.json",
    "docs/product/ppt-run2-data-skill-quality/results/run2_82_renderer_product_surface_text_composition_rerun_result.json",
]

ENGINEERING_TERMS = [
    "adapter",
    "binding",
    "check",
    "contract",
    "gate",
    "metadata",
    "policy",
    "public",
    "release",
    "required",
    "rerun",
    "schema",
    "source",
    "status",
    "trace",
    "validator",
]

DESIGN_TERMS = [
    "aesthetic",
    "composition",
    "density",
    "hierarchy",
    "layout",
    "mockup",
    "motif",
    "rhythm",
    "spacing",
    "style",
    "surface",
    "theater",
    "typography",
    "visual",
]

PRESERVED_GATES = [
    "traceability",
    "source_availability",
    "validator_required_files",
    "public_release_block",
    "negative_controls",
    "viewer_metadata_routes",
    "reproducible_scripts",
]

MISSING_DESIGN_TAXONOMY = [
    (
        "motif_id",
        "Names the concrete design move extracted from a tutorial or case instead of only naming a gate.",
        "Renderer must preserve the named motif across layout, text, and object drawing.",
    ),
    (
        "motif_family",
        "Groups related tutorial moves such as matrix, product theater, editorial spread, overlay, or sticker stack.",
        "Style router can select compatible modules by family instead of generic rectangles.",
    ),
    (
        "layout_recipe",
        "Captures spatial composition as a recipe, not a vague module name.",
        "Renderer receives explicit zones, focal object scale, overlaps, and reading path.",
    ),
    (
        "spatial_relation",
        "Describes how text, object, evidence, and background relate on the canvas.",
        "Text cannot float because it must attach to an object, edge, rail, field, or panel relation.",
    ),
    (
        "typography_treatment",
        "Preserves the tutorial's headline, paragraph, caption, and label behavior.",
        "Renderer applies type hierarchy as visual composition rather than only max_words.",
    ),
    (
        "visual_density",
        "Separates sparse premium pages, heavy editorial pages, and modular proof pages.",
        "Renderer chooses density per scenario instead of flattening every slide to the same block system.",
    ),
    (
        "style_family",
        "Keeps commercial style direction distinct from engineering status labels.",
        "Color, depth, shape language, and asset treatment are routed by style family.",
    ),
    (
        "scenario_fit",
        "Matches usecase needs such as product pitch, teaching, finance, or technical proof.",
        "Motifs can be constrained by scenario so decorative moves do not override business clarity.",
    ),
    (
        "renderer_recipe",
        "Turns design motif into executable native-PPT drawing instructions.",
        "Renderer can reproduce tutorial-derived visual effects without copying source assets.",
    ),
    (
        "motif_fidelity_checks",
        "Checks whether the rendered slide still looks like the intended motif.",
        "Evaluation can reject rectangle-only or wireframe outputs even if traceability passes.",
    ),
]


def read_text(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def count_terms(text: str, terms: list[str]) -> int:
    total = 0
    lower = text.lower()
    for term in terms:
        total += len(re.findall(rf"\b{re.escape(term.lower())}\b", lower))
    return total


def source_input_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for source in CONSUMED_SOURCES:
        path = ROOT / source
        text = read_text(source)
        engineering_count = count_terms(text, ENGINEERING_TERMS)
        design_count = count_terms(text, DESIGN_TERMS)
        records.append(
            {
                "path": source,
                "available": path.exists(),
                "usage": "workflow_taxonomy_bias_source",
                "engineering_term_count": engineering_count,
                "design_term_count": design_count,
                "engineering_to_design_ratio": round(engineering_count / max(design_count, 1), 2),
            }
        )
    return records


def layer_bias_records() -> list[dict[str, Any]]:
    return [
        {
            "layer_id": "source_quality_inventory",
            "layer_name": "Source quality inventory",
            "engineering_strength": "Tracks source availability, source type, and decomposition gaps explicitly.",
            "design_signal_loss": "Inventory fields prove coverage but do not yet encode motif, spatial recipe, or style family.",
            "bias_direction": "engineering_gate_dominant",
            "evidence": [
                "run2_73_source_quality_audit records source coverage and decomposition status.",
                "Several records remain source inventory until shot/layout-level signals are decomposed.",
            ],
            "impact_on_ppt": "Renderer can cite sources but cannot reproduce the visual method behind those sources.",
            "must_preserve": "Keep source availability, anti-copy boundaries, and decomposition gap labels.",
            "needs_new_design_layer": True,
        },
        {
            "layer_id": "workflow_gate_matrix",
            "layer_name": "Workflow gate matrix",
            "engineering_strength": "Forces reproducible stage boundaries, negative controls, public blocking, and trace gates.",
            "design_signal_loss": "Gate names describe whether a step is allowed, not what aesthetic move must survive the step.",
            "bias_direction": "engineering_gate_dominant",
            "evidence": [
                "skill_workflow.json and run2_8_workflow_gate_matrix.json protect execution order.",
                "The same gate vocabulary can dominate prompt and renderer instructions.",
            ],
            "impact_on_ppt": "Slides inherit status/gate language and can read as process documentation.",
            "must_preserve": "Keep the stage gates because they make the product reproducible and auditable.",
            "needs_new_design_layer": True,
        },
        {
            "layer_id": "tutorial_design_moves",
            "layer_name": "Tutorial design moves",
            "engineering_strength": "Maps tutorial rules to structured renderer actions with traceability.",
            "design_signal_loss": "Rules are action-safe but not always motif-specific enough to recreate a tutorial look.",
            "bias_direction": "design_signal_collapsed",
            "evidence": [
                "run2_73_tutorial_to_design_moves maps hierarchy, whitespace, rhythm, and motion rules.",
                "Renderer actions emphasize target selectors and fallbacks more than visual motif fidelity.",
            ],
            "impact_on_ppt": "The system applies rules like fewer labels, but the page may still look generic.",
            "must_preserve": "Keep traceable action mapping from tutorial rule to renderer action.",
            "needs_new_design_layer": True,
        },
        {
            "layer_id": "visual_grammar_modules",
            "layer_name": "Visual grammar modules",
            "engineering_strength": "Defines reusable page modules such as hero_field, before_after_theater, and product_reveal.",
            "design_signal_loss": "Module IDs are stronger than rectangles, but they still need motif recipes and style parameters.",
            "bias_direction": "design_signal_collapsed",
            "evidence": [
                "run2_73_visual_grammar_modules contains public-facing module choices.",
                "Later reruns still collapse many modules into similar fields and panels.",
            ],
            "impact_on_ppt": "Pages differ in intent but remain visually similar because motif execution is under-specified.",
            "must_preserve": "Keep role-to-module mapping and page differentiation constraints.",
            "needs_new_design_layer": True,
        },
        {
            "layer_id": "renderer_adapter_contracts",
            "layer_name": "Renderer adapter contracts",
            "engineering_strength": "Converts scene plans into renderer-safe containers, bindings, and execution guards.",
            "design_signal_loss": "Adapter terms can flatten design intent into proof_panel, hero_object, and status-safe primitives.",
            "bias_direction": "renderer_execution_dominant",
            "evidence": [
                "run2_73_renderer_adapter_contracts prevents renderer/public release leakage.",
                "It does not guarantee that visual motifs survive translation into native shapes.",
            ],
            "impact_on_ppt": "Outputs become valid native-PPT structures but can read as wireframe diagrams.",
            "must_preserve": "Keep execution guards and native editable output constraints.",
            "needs_new_design_layer": True,
        },
        {
            "layer_id": "text_binding_strategy",
            "layer_name": "Text binding strategy",
            "engineering_strength": "Binds headline, proof, supporting copy, and notes to source IDs and visual objects.",
            "design_signal_loss": "Socket binding controls where text is allowed, but not enough about editorial typography treatment.",
            "bias_direction": "engineering_gate_dominant",
            "evidence": [
                "run2_73_text_binding_strategy routes traceability off canvas.",
                "The stronger O1 text plan still needs a motif-level typography treatment to avoid dead layouts.",
            ],
            "impact_on_ppt": "Text is safer and denser, but blocks can feel stiff and disconnected from composition.",
            "must_preserve": "Keep canvas/note routing and source-bound copy units.",
            "needs_new_design_layer": True,
        },
        {
            "layer_id": "text_composition_plan",
            "layer_name": "Text composition plan",
            "engineering_strength": "Introduces headline, subhead, proof sentence, caption, capacity, and label bans.",
            "design_signal_loss": "The plan improves readability but still does not select style-specific text treatments.",
            "bias_direction": "design_signal_collapsed",
            "evidence": [
                "run2_81_text_composition_typography_plan bans floating labels and traceability on canvas.",
                "Run 2.82 can still feel text-heavy without richer motif/style routing.",
            ],
            "impact_on_ppt": "Pages gain text hierarchy but may lose the earlier modular, matrix, and overlay visual energy.",
            "must_preserve": "Keep readable hierarchy, object anchors, and note routes.",
            "needs_new_design_layer": True,
        },
        {
            "layer_id": "renderer_rerun_results",
            "layer_name": "Renderer rerun results",
            "engineering_strength": "Produces four arms and records consumed sources, outputs, viewer updates, and checks.",
            "design_signal_loss": "Rerun success proves generation and viewer availability, not public-grade aesthetic fidelity.",
            "bias_direction": "renderer_execution_dominant",
            "evidence": [
                "run2_82_renderer_product_surface_text_composition_rerun_result records generated arms.",
                "Quality verdict is explicitly deferred and public_ready remains false.",
            ],
            "impact_on_ppt": "The system may improve content and structure while still missing the desired presentation feel.",
            "must_preserve": "Keep four-arm comparisons and bad-control arms.",
            "needs_new_design_layer": True,
        },
        {
            "layer_id": "visual_quality_evaluation_loop",
            "layer_name": "Visual quality evaluation loop",
            "engineering_strength": "Repeated evaluations correctly block public release when wireframe or label issues remain.",
            "design_signal_loss": "Evaluation detects failures after the fact but does not itself teach renderer motif recipes.",
            "bias_direction": "evaluation_detects_but_does_not_teach_motif",
            "evidence": [
                "run2_74, run2_76, run2_78, and run2_80 evaluations keep public_ready false.",
                "Repeated blockers include wireframe, sparse text, labels, and absent product surface.",
            ],
            "impact_on_ppt": "The loop prevents false release, but can produce repeated repair cycles with diminishing visual gains.",
            "must_preserve": "Keep independent visual evaluation and public blocking.",
            "needs_new_design_layer": True,
        },
        {
            "layer_id": "validator_and_tests",
            "layer_name": "Validator and tests",
            "engineering_strength": "Make every data, workflow, renderer, and release boundary reproducible in CI-like checks.",
            "design_signal_loss": "Tests currently validate fields and gates more readily than motif fidelity and style fit.",
            "bias_direction": "engineering_gate_dominant",
            "evidence": [
                "validate_ppt_case_pack.py requires each run2 artifact and rejects public release leakage.",
                "Motif fidelity checks are not yet first-class required fields.",
            ],
            "impact_on_ppt": "The project gets safer but can optimize toward passing schemas instead of design quality.",
            "must_preserve": "Keep validators and add design motif checks beside them.",
            "needs_new_design_layer": True,
        },
    ]


def build_audit() -> dict[str, Any]:
    return {
        "artifact_id": "run2_83_workflow_taxonomy_bias_audit",
        "part": "Part P0",
        "schema_version": "ppt_run2_83_workflow_taxonomy_bias_audit.v1",
        "run_id": "2.83",
        "status": "run2_83_workflow_taxonomy_bias_audit_ready_public_blocked",
        "stage_policy": "part_p0_audit_only_no_renderer_rerun_no_viewer_update_no_public_release",
        "creates_new_ppt_deck": False,
        "starts_renderer_rerun": False,
        "updates_html_viewer": False,
        "public_release_started": False,
        "public_ready": False,
        "quality_claim_boundary": "workflow_taxonomy_bias_audit_only_no_visual_quality_pass_no_public_release",
        "consumed_sources": CONSUMED_SOURCES,
        "source_inputs": source_input_records(),
        "engineering_rigor_preservation": {
            "preserve_existing_gates": PRESERVED_GATES,
            "do_not_weaken_traceability": True,
            "public_release_gate_remains_blocked": True,
            "design_layer_adds_to_engineering_layer": True,
            "rationale": (
                "The current engineering constraints make the system reproducible; the fix is to add "
                "design/aesthetic taxonomy above them, not to weaken traceability or release gates."
            ),
        },
        "taxonomy_bias_summary": {
            "primary_bias": "engineering_constraint_labels_over_design_motif_labels",
            "root_cause": "design_motif_taxonomy_missing_between_tutorial_memory_and_renderer_adapter",
            "required_correction": (
                "Add a design_motif_layer that carries motif_id, motif_family, layout_recipe, "
                "typography_treatment, style_family, and motif_fidelity_checks while preserving engineering gates."
            ),
        },
        "layer_bias_records": layer_bias_records(),
        "run2_series_pattern": [
            {
                "stage_range": "2.7-2.18",
                "dominant_work": "Evidence, workflow, and traceability thickening.",
                "effect_on_ppt": "The deck became more reproducible, but visual decomposition was still shallow.",
            },
            {
                "stage_range": "2.24-2.42",
                "dominant_work": "Content and visual asset enrichment.",
                "effect_on_ppt": "More information entered the system, but product surfaces stayed schematic.",
            },
            {
                "stage_range": "2.43-2.64",
                "dominant_work": "Typography, readability, socket, and renderer fit gates.",
                "effect_on_ppt": "Text became safer, but design moves were often reduced to capacity and placement rules.",
            },
            {
                "stage_range": "2.73-2.82",
                "dominant_work": "Validated A-F contracts, renderer repairs, O1 text composition, and O2 rerun.",
                "effect_on_ppt": "Engineering confidence improved while motif fidelity and scenario style remain under-modeled.",
            },
        ],
        "missing_design_taxonomy": [
            {
                "field": field,
                "why_needed": why_needed,
                "renderer_contract_implication": renderer_contract_implication,
            }
            for field, why_needed, renderer_contract_implication in MISSING_DESIGN_TAXONOMY
        ],
        "required_next_layer": {
            "layer_id": "design_motif_layer",
            "must_add_fields": [field for field, _, _ in MISSING_DESIGN_TAXONOMY],
            "must_preserve_engineering_gates": True,
            "must_not_replace_validator": True,
            "goal": (
                "Recover tutorial-derived modular, matrix, overlay, sticker-stack, product-theater, "
                "and editorial text motifs while keeping source trace and public-release gates."
            ),
        },
        "no_new_renderer_proof": {
            "new_ppt_created": False,
            "new_html_created": False,
            "viewer_updated": False,
        },
        "next_required_action": "part_p1_design_motif_taxonomy_and_style_router_plan",
    }


def write_markdown(audit: dict[str, Any]) -> None:
    rows = [
        "# Run 2.83 Workflow Taxonomy Bias Audit",
        "",
        "Status: public blocked, not a renderer rerun.",
        "",
        "Conclusion: the dominant issue is engineering constraint labels over design motif labels. "
        "The existing rigor is useful and should stay, but the system needs a design motif layer "
        "between tutorial memory and renderer adapter.",
        "",
        "## Preserve",
    ]
    for gate in audit["engineering_rigor_preservation"]["preserve_existing_gates"]:
        rows.append(f"- {gate}")
    rows.extend(["", "## Bias By Layer"])
    for layer in audit["layer_bias_records"]:
        rows.append(
            f"- {layer['layer_id']}: {layer['design_signal_loss']} Impact: {layer['impact_on_ppt']}"
        )
    rows.extend(["", "## Missing Design Taxonomy"])
    for item in audit["missing_design_taxonomy"]:
        rows.append(f"- {item['field']}: {item['why_needed']}")
    rows.extend(
        [
            "",
            "## Next",
            "",
            "Build the design_motif_layer / style router. Keep validator gates, traceability, negative controls, "
            "and public blocked release policy intact.",
        ]
    )
    RESULT_MD.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> None:
    RESULT_JSON.parent.mkdir(parents=True, exist_ok=True)
    audit = build_audit()
    RESULT_JSON.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    write_markdown(audit)
    print(f"wrote {RESULT_JSON.relative_to(ROOT)}")
    print(f"wrote {RESULT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
