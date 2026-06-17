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


def test_run2_63_static_contract_is_ci_visible() -> None:
    audit_script = (
        ROOT / "scripts" / "audit_ppt_run2_63_narrative_proof_consumption_effectiveness.py"
    ).read_text(encoding="utf-8")
    viewer = (ROOT / "scripts" / "build_ppt_run_html_viewer.py").read_text(encoding="utf-8")
    result = load_json(
        PACK / "results" / "run2_63_narrative_proof_consumption_effectiveness_audit.json"
    )
    result_md = (
        PACK / "results" / "run2_63_narrative_proof_consumption_effectiveness_audit.md"
    ).read_text(encoding="utf-8")

    assert result["run_id"] == "2.63"
    assert result["source_generated_run"] == "2.62"
    assert result["source_data_run"] == "2.61"
    assert result["creates_new_ppt_deck"] is False
    assert result["data_consumption_assessment"]["run2_61_data_consumed"] is True
    assert result["data_consumption_assessment"]["full_slides_with_run2_61_contracts"] == 6
    assert result["data_consumption_assessment"]["full_slides_with_socket_bindings"] == 6
    assert result["data_consumption_assessment"]["bad_control_without_run2_61_contracts"] == 6
    assert result["root_cause_assessment"]["primary_layer"] == "renderer_composition_grammar"
    assert result["gate_summary"]["renderer_effectiveness_gate"] == "blocked"
    assert result["next_required_action"] == (
        "build_run2_64_renderer_composition_repair_for_dynamic_sockets_and_semantic_diagrams_before_rerun"
    )

    assert_contains(
        audit_script,
        [
            "RUN262_FULL_STATUS",
            "RUN262_BAD_STATUS",
            "RENDERER_BLOCKERS",
            "static_socket_plan_repeated_on_every_slide",
            "text_fit_and_wrapping_not_trace_gated",
            "build_run2_64_renderer_composition_repair_for_dynamic_sockets_and_semantic_diagrams_before_rerun",
        ],
    )
    assert_contains(
        viewer,
        [
            "Run 2.63 narrative proof effectiveness audit",
            "run2_63_narrative_proof_consumption_effectiveness_audit.json",
            "renderer_composition_grammar",
            "static_socket_plan_repeated_on_every_slide",
            "run263RoleCards",
        ],
    )
    assert_contains(
        result_md,
        [
            "Run 2.63 Narrative Proof Consumption Effectiveness Audit",
            "2.62 consumes 2.61",
            "renderer/composition grammar",
            "static socket plan",
            "Run 2.64",
            "Do not advance to Run 3.0",
        ],
    )
