"""Contract test: ValidationReport survives _report_to_dict -> JSON -> _report_from_dict."""
from __future__ import annotations

import json

from vulca.layers.layered_generate import _report_from_dict, _report_to_dict
from vulca.layers.validate import ValidationReport, ValidationWarning


def test_round_trip_preserves_all_fields():
    original = ValidationReport(
        ok=False,
        warnings=[
            ValidationWarning(kind="coverage", message="low",
                              detail={"actual": 0.12}),
            ValidationWarning(kind="position", message="off", detail={}),
        ],
        coverage_actual=0.12,
        position_iou=0.45,
    )
    as_dict = _report_to_dict(original)
    as_json = json.loads(json.dumps(as_dict))
    restored = _report_from_dict(as_json)

    assert restored is not None, "round-trip returned None (schema version mismatch?)"
    assert restored.ok == original.ok
    assert restored.coverage_actual == original.coverage_actual
    assert restored.position_iou == original.position_iou
    assert len(restored.warnings) == len(original.warnings)
    for r, o in zip(restored.warnings, original.warnings):
        assert isinstance(r, ValidationWarning)
        assert r.kind == o.kind
        assert r.message == o.message
        assert r.detail == o.detail


def test_round_trip_with_empty_warnings():
    original = ValidationReport(ok=True, warnings=[], coverage_actual=0.0, position_iou=0.0)
    restored = _report_from_dict(
        json.loads(json.dumps(_report_to_dict(original)))
    )
    assert restored is not None
    assert restored.ok is True
    assert restored.warnings == []


def test_unknown_fields_silently_dropped():
    """_report_from_dict uses explicit field extraction — unknown fields
    are ignored. This documents that behavior as intentional (forward
    compat with future schema additions)."""
    d = {
        "schema_version": 1,
        "ok": True,
        "warnings": [],
        "coverage_actual": 0.5,
        "position_iou": 0.3,
        "future_field": "should be ignored",
    }
    restored = _report_from_dict(d)
    assert restored is not None
    assert restored.ok is True
    assert not hasattr(restored, "future_field")


def test_stale_schema_version_returns_none():
    """Sidecar with wrong schema_version returns None — forces re-validation."""
    d = {
        "schema_version": 999,
        "ok": True,
        "warnings": [],
    }
    assert _report_from_dict(d) is None


def test_missing_schema_version_returns_none():
    """Legacy sidecar without schema_version returns None."""
    d = {"ok": True, "warnings": []}
    assert _report_from_dict(d) is None
