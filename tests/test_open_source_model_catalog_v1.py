import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "docs/benchmarks/learning/open_source_model_catalog_v1.json"

REQUIRED_MODEL_FIELDS = {
    "id",
    "name",
    "source_url",
    "license",
    "license_risk",
    "model_role",
    "target_case_types",
    "target_workflows",
    "recommended_use",
    "intake_status",
    "default_runtime_enabled",
    "output_training_policy",
    "requires_manual_review_for_training_labels",
    "risks",
}

ALLOWED_CASE_TYPES = {"redraw_case", "decompose_case", "layer_generate_case"}
ALLOWED_LICENSE_RISKS = {
    "permissive",
    "non_commercial",
    "commercial_license_required",
    "license_review_required",
}
ALLOWED_OUTPUT_POLICIES = {
    "candidate_cases_only",
    "quality_signals_only",
    "benchmark_reference_only",
    "blocked_for_training",
}


def _load_catalog() -> dict:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def test_open_source_model_catalog_v1_schema_and_safety_defaults():
    catalog = _load_catalog()

    assert catalog["schema_version"] == 1
    assert catalog["case_type"] == "learning_open_source_model_catalog"
    assert catalog["default_runtime_enabled"] is False
    assert catalog["default_training_input"] is False
    assert catalog["requires_explicit_enablement"] is True
    assert catalog["requires_reviewed_case_conversion"] is True
    assert catalog["pilot_policy"] == {
        "requires_license_review_before_download": True,
        "requires_model_card_review_before_runtime": True,
        "requires_manual_review_before_training": True,
        "allow_weight_download_by_default": False,
        "output_kind": "open_model_candidate_signals",
    }

    models = catalog["models"]
    assert len(models) >= 6
    assert len({item["id"] for item in models}) == len(models)

    serialized = CATALOG.read_text(encoding="utf-8")
    assert "/Users/" not in serialized
    assert "private://local_path/" not in serialized

    for item in models:
        assert REQUIRED_MODEL_FIELDS.issubset(item)
        assert item["source_url"].startswith("https://")
        assert item["license"]
        assert item["license_risk"] in ALLOWED_LICENSE_RISKS
        assert item["intake_status"] in {
            "recommended_pilot",
            "catalog_only",
            "blocked_pending_license_review",
            "blocked_non_commercial",
        }
        assert item["default_runtime_enabled"] is False
        assert item["output_training_policy"] in ALLOWED_OUTPUT_POLICIES
        assert item["requires_manual_review_for_training_labels"] is True
        assert item["target_case_types"]
        assert set(item["target_case_types"]).issubset(ALLOWED_CASE_TYPES)
        assert item["risks"]


def test_open_source_model_catalog_prioritizes_current_vulca_roles():
    models = {item["id"]: item for item in _load_catalog()["models"]}

    assert models["qwen_image_edit"]["intake_status"] == "recommended_pilot"
    assert models["qwen_image_edit"]["license"] == "apache-2.0"
    assert models["qwen_image_edit"]["model_role"] == "open_image_edit_provider"
    assert set(models["qwen_image_edit"]["target_case_types"]) == {
        "redraw_case",
        "layer_generate_case",
    }
    assert models["qwen_image_edit"]["output_training_policy"] == "candidate_cases_only"

    assert models["segment_anything_sam_vit"]["intake_status"] == "recommended_pilot"
    assert models["segment_anything_sam_vit"]["model_role"] == "mask_proposal"
    assert "decompose_case" in models["segment_anything_sam_vit"]["target_case_types"]

    assert models["grounding_dino"]["intake_status"] == "recommended_pilot"
    assert models["grounding_dino"]["model_role"] == "text_grounded_detection"
    assert "layer_generate_case" in models["grounding_dino"]["target_case_types"]

    assert models["florence_2"]["license"] == "mit"
    assert models["florence_2"]["model_role"] == "vision_caption_grounding_ocr"


def test_open_source_model_catalog_blocks_noncommercial_or_unclear_models():
    models = {item["id"]: item for item in _load_catalog()["models"]}

    assert models["flux_kontext_dev"]["license_risk"] == "non_commercial"
    assert models["flux_kontext_dev"]["intake_status"] == "blocked_non_commercial"
    assert models["flux_kontext_dev"]["output_training_policy"] == "blocked_for_training"

    assert models["stable_diffusion_3_5_large"]["license_risk"] == (
        "commercial_license_required"
    )
    assert models["stable_diffusion_3_5_large"]["intake_status"] == (
        "blocked_pending_license_review"
    )
    assert models["stable_diffusion_3_5_large"]["default_runtime_enabled"] is False


def test_open_source_model_catalog_keeps_models_out_of_training_by_default():
    catalog = _load_catalog()

    for item in catalog["models"]:
        assert item["default_training_input"] is False
        assert item["recommended_use"] != "default_training"
        assert "human_reviewed" not in item["output_training_policy"]

    recommended = {
        item["id"] for item in catalog["models"] if item["intake_status"] == "recommended_pilot"
    }
    assert {
        "qwen_image_edit",
        "segment_anything_sam_vit",
        "grounding_dino",
        "florence_2",
    }.issubset(recommended)
