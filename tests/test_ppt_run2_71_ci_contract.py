import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "product" / "ppt-run2-data-skill-quality"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_contains(text: str, terms: list[str]) -> None:
    missing = [term for term in terms if term not in text]
    assert not missing, f"missing terms: {missing}"


def test_run2_71_static_component_semantics_contract_is_ci_visible() -> None:
    generator = ROOT / "scripts" / "generate_ppt_run2_71_component_semantics_arms.mjs"
    assert generator.exists()
    script = generator.read_text(encoding="utf-8")

    result = load_json(PACK / "results" / "run2_71_component_semantics_rerun_result.json")
    assert result["run_id"] == "2.71"
    assert result["source_generated_run_id"] == "2.70"
    assert result["source_design_run_id"] == "2.66"
    assert result["component_semantics_scope"]["target_roles"] == ["contrast", "proof", "climax"]
    assert result["component_semantics_scope"]["required_component_archetypes"] == [
        "before_after_product_scene",
        "inspectable_evidence_workspace",
        "editable_presentation_surface",
    ]
    assert result["quality_delta"]["target_layer"] == "run2_70_component_semantics_content_binding"
    assert result["quality_delta"]["full_targeted_slides_with_component_manifests"] == 3
    assert result["quality_delta"]["full_targeted_slides_with_text_component_bindings"] == 3
    assert result["quality_delta"]["full_targeted_slides_with_non_rectangular_primitives"] == 3
    assert result["quality_delta"]["full_targeted_slides_with_distinct_component_archetypes"] == 3
    assert result["quality_delta"]["bad_control_targeted_slides_without_component_semantics"] == 3
    assert result["control_boundary"]["bad_run2_70_without_component_semantics"]

    assert_contains(
        script,
        [
            "run2_70_high_fidelity_mock_content_rerun_result.json",
            "drawRun271ComponentSemanticSurface",
            "drawRun271BeforeAfterProductScene",
            "fillRun271InspectableEvidenceWorkspace",
            "fillRun271EditablePresentationSurface",
            "registerRun271ComponentManifest",
            "registerRun271TextComponentBinding",
            "component_semantics_content_binding",
            "bad_run2_70_without_component_semantics",
        ],
    )

    viewer = (
        ROOT
        / "outputs"
        / "019e7d9c-532a-70b3-8892-fa3ae42baef2"
        / "presentations"
        / "ppt-run-viewer.html"
    ).read_text(encoding="utf-8")
    assert_contains(
        viewer,
        [
            "Run 2.71",
            "ppt-run2-71-full-vulca",
            "ppt-run2-71-bad-without-component-semantics",
            "run2-71-four-arm-contact-sheet.png",
            "run2_71_component_semantics_rerun_result.json",
            '"latestRunId": "2.71"',
        ],
    )
