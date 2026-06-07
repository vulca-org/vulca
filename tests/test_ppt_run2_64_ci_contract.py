from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_contains(body: str, terms: list[str]) -> None:
    for term in terms:
        assert term in body, f"missing term: {term!r}"


def test_run2_64_static_contract_is_ci_visible() -> None:
    builder = (ROOT / "scripts" / "build_ppt_run2_64_renderer_composition_repair.py").read_text(
        encoding="utf-8"
    )
    viewer = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")
    result = load_json(PACK / "results" / "run2_64_renderer_composition_repair_result.json")
    dynamic_socket = load_json(PACK / "run2_64_dynamic_socket_renderer_memory.json")
    semantic_diagram = load_json(PACK / "run2_64_semantic_diagram_renderer_memory.json")
    text_fit = load_json(PACK / "run2_64_text_fit_renderer_gates.json")
    dry_run = load_json(PACK / "run2_64_renderer_dry_run_binding_matrix.json")
    result_md = (PACK / "results" / "run2_64_renderer_composition_repair_result.md").read_text(
        encoding="utf-8"
    )

    assert result["run_id"] == "2.64"
    assert result["source_audit_run"] == "2.63"
    assert result["source_generated_run"] == "2.62"
    assert result["creates_new_ppt_deck"] is False
    assert result["next_required_action"] == (
        "run2_65_generate_four_arm_ppt_consuming_run2_64_renderer_composition_repair"
    )
    assert len(dynamic_socket["dynamic_socket_renderer_records"]) == 6
    assert len(semantic_diagram["semantic_diagram_renderer_records"]) == 6
    assert len(text_fit["text_fit_renderer_gates"]) == 6
    assert len(dry_run["dry_run_binding_records"]) == 6
    assert all(record["orphan_socket_count"] == 0 for record in dry_run["dry_run_binding_records"])
    assert all(
        record["runtime_claim_boundary"] == "must_be_verified_by_run2_65_render_trace"
        for record in text_fit["text_fit_renderer_gates"]
    )

    assert_contains(
        builder,
        [
            "run2_63_narrative_proof_consumption_effectiveness_audit.json",
            "run2_61_text_socket_fusion_contracts.json",
            "run2_64_dynamic_socket_renderer_memory.json",
            "run2_64_semantic_diagram_renderer_memory.json",
            "run2_64_text_fit_renderer_gates.json",
            "run2_64_renderer_dry_run_binding_matrix.json",
            "must_be_verified_by_run2_65_render_trace",
            "run2_65_generate_four_arm_ppt_consuming_run2_64_renderer_composition_repair",
        ],
    )
    assert_contains(
        viewer,
        [
            "Run 2.64 renderer composition repair",
            "run2_64_dynamic_socket_renderer_memory.json",
            "run2_64_renderer_dry_run_binding_matrix.json",
            "run2_65_generate_four_arm_ppt_consuming_run2_64_renderer_composition_repair",
        ],
    )
    assert_contains(
        result_md,
        [
            "Run 2.64 Renderer Composition Repair",
            "dynamic socket",
            "semantic diagram",
            "text-fit",
            "dry-run binding matrix",
            "Run 2.65",
        ],
    )
