import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "docs/benchmarks/learning/external_dataset_catalog_v1.json"

REQUIRED_DATASET_FIELDS = {
    "id",
    "name",
    "source_url",
    "license",
    "license_risk",
    "supervision_kind",
    "target_case_types",
    "candidate_mapping",
    "recommended_use",
    "intake_status",
    "default_training_input",
    "requires_manual_review",
}

ALLOWED_CASE_TYPES = {"redraw_case", "decompose_case", "layer_generate_case"}
ALLOWED_LICENSE_RISKS = {
    "permissive",
    "attribution_required",
    "research_only",
    "license_review_required",
}


def _load_catalog() -> dict:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def test_external_dataset_catalog_v1_schema_and_safety_defaults():
    catalog = _load_catalog()

    assert catalog["schema_version"] == 1
    assert catalog["case_type"] == "learning_external_dataset_catalog"
    assert catalog["default_training_input"] is False
    assert catalog["requires_reviewed_case_conversion"] is True
    assert catalog["pilot_policy"] == {
        "max_records_per_dataset": 300,
        "requires_license_review_before_download": True,
        "requires_manual_review_before_training": True,
        "output_kind": "external_candidate_cases",
    }

    datasets = catalog["datasets"]
    assert len(datasets) >= 8
    assert len({item["id"] for item in datasets}) == len(datasets)

    for item in datasets:
        assert REQUIRED_DATASET_FIELDS.issubset(item)
        assert item["source_url"].startswith("https://")
        assert item["license"]
        assert item["license_risk"] in ALLOWED_LICENSE_RISKS
        assert item["intake_status"] in {
            "recommended_pilot",
            "catalog_only",
            "benchmark_only",
            "blocked_pending_license_review",
        }
        assert item["default_training_input"] is False
        assert item["requires_manual_review"] is True
        assert set(item["target_case_types"]).issubset(ALLOWED_CASE_TYPES)
        assert item["target_case_types"]

    serialized = CATALOG.read_text(encoding="utf-8")
    assert "/Users/" not in serialized
    assert "private://local_path/" not in serialized


def test_external_dataset_catalog_prioritizes_sources_by_vulca_case_type():
    datasets = {item["id"]: item for item in _load_catalog()["datasets"]}

    assert datasets["magicbrush"]["intake_status"] == "recommended_pilot"
    assert datasets["magicbrush"]["target_case_types"] == ["redraw_case"]
    assert datasets["magicbrush"]["candidate_mapping"]["instruction"] == "instruction"

    assert datasets["ade20k"]["intake_status"] == "recommended_pilot"
    assert "decompose_case" in datasets["ade20k"]["target_case_types"]
    assert datasets["ade20k"]["candidate_mapping"]["layer_hints"] == "object_part_annotations"

    assert datasets["imagerewarddb"]["intake_status"] == "recommended_pilot"
    assert datasets["imagerewarddb"]["target_case_types"] == ["layer_generate_case"]
    assert datasets["imagerewarddb"]["candidate_mapping"]["review_label"] == "preferred_image"

    assert datasets["sa1b"]["license_risk"] == "research_only"
    assert datasets["sa1b"]["intake_status"] == "blocked_pending_license_review"


def test_external_dataset_catalog_separates_training_use_from_benchmark_use():
    datasets = {item["id"]: item for item in _load_catalog()["datasets"]}

    benchmark_only = {
        item["id"] for item in datasets.values() if item["intake_status"] == "benchmark_only"
    }
    assert {"pie_bench"}.issubset(benchmark_only)

    training_candidates = {
        item["id"] for item in datasets.values() if item["intake_status"] == "recommended_pilot"
    }
    assert {
        "magicbrush",
        "ade20k",
        "imagerewarddb",
    }.issubset(training_candidates)

    for item in datasets.values():
        assert "reviewed" not in item.get("output_kind", "")
        assert item["recommended_use"] != "default_training"
