import json

import pytest

from vulca.layers.types import LayerInfo


def test_build_decompose_case_minimal_schema(tmp_path):
    from vulca.layers.decompose_cases import build_decompose_case

    manifest_path = tmp_path / "manifest.json"
    manifest_data = {
        "version": 5,
        "split_mode": "claude_orchestrated",
        "status": "partial",
        "layers": [
            {
                "id": "layer_sky",
                "name": "sky",
                "semantic_path": "background.sky",
                "file": "sky.png",
                "z_index": 10,
                "quality_status": "detected",
                "area_pct": 70.0,
                "bbox": [0, 0, 100, 70],
                "parent_layer_id": None,
            },
            {
                "id": "layer_residual",
                "name": "residual",
                "semantic_path": "residual",
                "file": "residual.png",
                "z_index": 1,
                "quality_status": "residual",
                "area_pct": 30.0,
                "bbox": [0, 0, 100, 100],
                "parent_layer_id": None,
            },
        ],
        "detection_report": {
            "requested": 2,
            "detected": 1,
            "suspect": 0,
            "missed": 1,
            "success_rate": 0.5,
        },
    }
    manifest_path.write_text(json.dumps(manifest_data))

    record = build_decompose_case(
        source_image="source.jpg",
        mode="orchestrated",
        provider="",
        model="",
        tradition="post_impressionist_painting",
        output_dir=str(tmp_path),
        manifest_path=str(manifest_path),
        target_layer_hints=[
            {
                "name": "sky",
                "label": "swirling sky",
                "semantic_path": "background.sky",
                "detector": "sam_bbox",
                "bbox_hint_pct": [0.0, 0.0, 1.0, 0.7],
                "multi_instance": False,
                "threshold": None,
                "order": None,
            }
        ],
        debug_artifacts={"qa_contact_sheet_path": str(tmp_path / "qa.jpg")},
        created_at="2026-05-05T12:00:00Z",
    )

    assert record["schema_version"] == 1
    assert record["case_type"] == "decompose_case"
    assert record["case_id"].startswith("decompose_20260505T120000Z_")
    assert record["input"]["source_image"] == "source.jpg"
    assert record["input"]["requested"] == {
        "mode": "orchestrated",
        "provider": "",
        "model": "",
        "tradition": "post_impressionist_painting",
    }
    assert record["input"]["target_layer_hints"][0]["semantic_path"] == "background.sky"
    assert record["output"]["manifest_path"] == str(manifest_path)
    assert record["output"]["output_dir"] == str(tmp_path)
    assert record["output"]["manifest_version"] == 5
    assert record["output"]["split_mode"] == "claude_orchestrated"
    assert record["output"]["status"] == "partial"
    assert record["output"]["layers"][0] == {
        "id": "layer_sky",
        "name": "sky",
        "semantic_path": "background.sky",
        "file": str(tmp_path / "sky.png"),
        "z_index": 10,
        "quality_status": "detected",
        "area_pct": 70.0,
        "bbox": [0, 0, 100, 70],
        "parent_layer_id": None,
    }
    assert record["output"]["residual_path"] == str(tmp_path / "residual.png")
    assert record["output"]["composite_path"] == ""
    assert record["output"]["detection_report"]["missed"] == 1
    assert record["output"]["debug_artifacts"]["qa_contact_sheet_path"] == str(tmp_path / "qa.jpg")
    assert record["quality"]["quality_score"] is None
    assert record["quality"]["layer_coverage"] == {
        "claimed_pct": 70.0,
        "residual_pct": 30.0,
        "missed_hint_count": 1,
        "suspect_hint_count": 0,
    }
    assert record["quality"]["alpha_quality"]["empty_layer_count"] == 0
    assert record["quality"]["residual_leakage"]["residual_pct"] == 30.0
    assert record["review"] == {
        "human_accept": None,
        "failure_type": "",
        "preferred_action": "",
        "reviewer": "",
        "reviewed_at": "",
        "notes": "",
    }


def test_append_decompose_case_writes_one_json_line(tmp_path):
    from vulca.layers.decompose_cases import append_decompose_case

    path = tmp_path / "cases" / "decompose_cases.jsonl"
    record = {
        "schema_version": 1,
        "case_type": "decompose_case",
        "case_id": "decompose_example",
    }

    written = append_decompose_case(str(path), record)

    assert written == str(path)
    lines = path.read_text().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == record


def test_validate_decompose_labels_reject_unknown_values():
    from vulca.layers.decompose_cases import (
        validate_failure_type,
        validate_preferred_action,
    )

    assert validate_failure_type("") == ""
    assert validate_failure_type("under_split") == "under_split"
    assert validate_preferred_action("") == ""
    assert validate_preferred_action("adjust_hints") == "adjust_hints"

    with pytest.raises(ValueError, match="unsupported decompose failure_type"):
        validate_failure_type("color_drift")
    with pytest.raises(ValueError, match="unsupported decompose preferred_action"):
        validate_preferred_action("adjust_mask")


def test_resolve_case_log_path_supports_env_default(tmp_path, monkeypatch):
    from vulca.layers.decompose_cases import resolve_case_log_path

    assert resolve_case_log_path("", str(tmp_path)) == ""

    monkeypatch.setenv("VULCA_DECOMPOSE_CASE_LOG", "1")
    assert resolve_case_log_path("", str(tmp_path)) == str(tmp_path / "decompose_cases.jsonl")

    explicit = tmp_path / "custom.jsonl"
    assert resolve_case_log_path(str(explicit), str(tmp_path)) == str(explicit)

    monkeypatch.setenv("VULCA_DECOMPOSE_CASE_LOG", str(tmp_path / "env.jsonl"))
    assert resolve_case_log_path("", str(tmp_path)) == str(tmp_path / "env.jsonl")


def test_target_hints_from_plan_and_layer_infos():
    from vulca.layers.decompose_cases import (
        target_hints_from_layer_infos,
        target_hints_from_plan,
    )

    plan = {
        "entities": [
            {
                "name": "person",
                "label": "main person",
                "semantic_path": "subject.person[0]",
                "detector": "yolo",
                "bbox_hint_pct": None,
                "multi_instance": True,
                "threshold": 0.25,
                "order": 1,
            }
        ]
    }
    assert target_hints_from_plan(plan) == [
        {
            "name": "person",
            "label": "main person",
            "semantic_path": "subject.person[0]",
            "detector": "yolo",
            "bbox_hint_pct": None,
            "multi_instance": True,
            "threshold": 0.25,
            "order": 1,
        }
    ]

    infos = [
        LayerInfo(
            name="sky",
            description="blue sky",
            z_index=0,
            content_type="background",
            semantic_path="background.sky",
        )
    ]
    assert target_hints_from_layer_infos(infos) == [
        {
            "name": "sky",
            "label": "blue sky",
            "semantic_path": "background.sky",
            "detector": "",
            "bbox_hint_pct": None,
            "multi_instance": False,
            "threshold": None,
            "order": None,
        }
    ]
