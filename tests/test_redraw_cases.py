import json

import pytest

from vulca.layers.types import LayerInfo


def test_build_redraw_case_minimal_schema(tmp_path):
    from vulca.layers.redraw_cases import build_redraw_case

    layer = LayerInfo(
        id="layer_fg_001",
        name="fg",
        description="foreground object",
        z_index=1,
        content_type="subject",
        semantic_path="subject.object",
        quality_status="detected",
        area_pct=1.25,
    )
    record = build_redraw_case(
        artwork_dir=str(tmp_path),
        source_image="source.png",
        layer_info=layer,
        instruction="make it cleaner",
        provider="openai",
        model="gpt-image-2",
        route_requested="auto",
        source_layer_path=str(tmp_path / "fg.png"),
        redrawn_layer_path=str(tmp_path / "fg_redrawn.png"),
        source_pasteback_path=str(tmp_path / "fg_redrawn_on_source.png"),
        redraw_advisory={
            "route_chosen": "inpaint",
            "redraw_route": "sparse_bbox_crop",
            "geometry_redraw_route": "sparse_bbox_crop",
            "area_pct": 0.64,
            "bbox_fill": 1.0,
            "component_count": 1,
            "sparse_detected": True,
            "quality_gate_passed": True,
            "quality_failures": [],
            "refinement_applied": False,
            "refinement_reason": "no_target_profile",
            "refinement_strategy": "none",
            "refined_child_count": 0,
            "mask_granularity_score": 0.0,
        },
        created_at="2026-05-05T12:00:00Z",
    )

    assert record["schema_version"] == 1
    assert record["case_type"] == "redraw_case"
    assert record["case_id"].startswith("redraw_20260505T120000Z_")
    assert record["artwork_dir"] == str(tmp_path)
    assert record["source_image"] == "source.png"
    assert record["layer"] == {
        "id": "layer_fg_001",
        "name": "fg",
        "description": "foreground object",
        "semantic_path": "subject.object",
        "quality_status": "detected",
        "area_pct_manifest": 1.25,
    }
    assert record["route"]["requested"] == "auto"
    assert record["route"]["chosen"] == "inpaint"
    assert record["geometry"]["component_count"] == 1
    assert record["quality"]["gate_passed"] is True
    assert record["review"] == {
        "human_accept": None,
        "failure_type": "",
        "preferred_action": "",
        "reviewer": "",
        "reviewed_at": "",
    }


def test_append_redraw_case_writes_one_json_line(tmp_path):
    from vulca.layers.redraw_cases import append_redraw_case

    path = tmp_path / "cases" / "redraw_cases.jsonl"
    record = {
        "schema_version": 1,
        "case_type": "redraw_case",
        "case_id": "redraw_example",
    }

    written = append_redraw_case(str(path), record)

    assert written == str(path)
    lines = path.read_text().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == record


def test_validate_failure_type_rejects_unknown_label():
    from vulca.layers.redraw_cases import validate_failure_type

    assert validate_failure_type("") == ""
    assert validate_failure_type("mask_too_broad") == "mask_too_broad"
    with pytest.raises(ValueError, match="unsupported redraw failure_type"):
        validate_failure_type("bad_label")


def test_resolve_case_log_path_supports_env_default(tmp_path, monkeypatch):
    from vulca.layers.redraw_cases import resolve_case_log_path

    assert resolve_case_log_path("", str(tmp_path)) == ""

    monkeypatch.setenv("VULCA_REDRAW_CASE_LOG", "1")
    assert resolve_case_log_path("", str(tmp_path)) == str(tmp_path / "redraw_cases.jsonl")

    explicit = tmp_path / "custom.jsonl"
    assert resolve_case_log_path(str(explicit), str(tmp_path)) == str(explicit)

    monkeypatch.setenv("VULCA_REDRAW_CASE_LOG", str(tmp_path / "env.jsonl"))
    assert resolve_case_log_path("", str(tmp_path)) == str(tmp_path / "env.jsonl")
