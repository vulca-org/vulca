from __future__ import annotations

import json
from pathlib import Path

from scripts.experiments.vulca_jepa_guard import build_guard_result, sample_family, write_guard


def _write_json(path: Path, data: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False))
    return path


def _fixture_files(tmp_path: Path) -> dict[str, Path]:
    inventory = {
        "samples_total": 4,
        "audit_sets": {"core": 4},
        "samples": [
            {
                "sample_id": "gongbi_baseline_failed_subject",
                "group": "gallery_promptfix",
                "path": "gallery/chinese_gongbi.png",
                "audit_set": "core",
                "usable_for_embedding": True,
            },
            {
                "sample_id": "gongbi_promptfix_seed1",
                "group": "gallery_promptfix",
                "path": "gallery-promptfix/chinese_gongbi_seed1.png",
                "audit_set": "core",
                "usable_for_embedding": True,
            },
            {
                "sample_id": "gongbi_promptfix_seed2",
                "group": "gallery_promptfix",
                "path": "gallery-promptfix/chinese_gongbi_seed2.png",
                "audit_set": "core",
                "usable_for_embedding": True,
            },
            {
                "sample_id": "brand_design",
                "group": "gallery_breadth",
                "path": "gallery/brand_design.png",
                "audit_set": "core",
                "usable_for_embedding": True,
            },
        ],
    }
    dinov2 = {
        "backend": "dinov2",
        "status": "ok",
        "anomaly_ranking": [
            {
                "sample_id": "gongbi_baseline_failed_subject",
                "nearest_sample_id": "xieyi_promptfix",
                "nearest_distance": 0.62,
            },
            {
                "sample_id": "gongbi_promptfix_seed1",
                "nearest_sample_id": "gongbi_promptfix_seed2",
                "nearest_distance": 0.53,
            },
            {
                "sample_id": "gongbi_promptfix_seed2",
                "nearest_sample_id": "gongbi_promptfix_seed1",
                "nearest_distance": 0.53,
            },
        ],
    }
    siglip = {
        "backend": "siglip",
        "status": "ok",
        "samples": [
            {
                "sample_id": "gongbi_baseline_failed_subject",
                "probability": 0.00008,
                "logit": -9,
                "text_source": "prompt",
            },
            {
                "sample_id": "gongbi_promptfix_seed1",
                "probability": 0.007,
                "logit": -4.9,
                "text_source": "prompt",
            },
            {
                "sample_id": "gongbi_promptfix_seed2",
                "probability": 0.00009,
                "logit": -9.1,
                "text_source": "prompt",
            },
        ],
    }
    return {
        "inventory": _write_json(tmp_path / "inventory.json", inventory),
        "dinov2": _write_json(tmp_path / "dinov2.json", dinov2),
        "siglip": _write_json(tmp_path / "siglip.json", siglip),
    }


def test_sample_family_groups_promptfix_variants() -> None:
    assert sample_family("gongbi_baseline_failed_subject") == "gongbi"
    assert sample_family("gongbi_promptfix_seed1") == "gongbi"
    assert sample_family("xieyi_promptfix") == "xieyi"
    assert sample_family("japanese_baseline_failed_style") == "japanese"


def test_build_guard_result_warns_only_on_low_siglip_and_family_mismatch(tmp_path: Path) -> None:
    files = _fixture_files(tmp_path)

    result = build_guard_result(
        inventory_path=files["inventory"],
        dinov2_audit_path=files["dinov2"],
        siglip_audit_path=files["siglip"],
    )

    assert result["status"] == "ok"
    assert result["non_blocking"] is True
    assert result["samples_evaluated"] == 3
    assert result["warnings_total"] == 1
    warning = result["warnings"][0]
    assert warning["sample_id"] == "gongbi_baseline_failed_subject"
    assert warning["warning_type"] == "subject_drift_warning"
    assert warning["action"] == "warn_only"
    assert warning["signals"]["nearest_sample_id"] == "xieyi_promptfix"


def test_write_guard_outputs_json(tmp_path: Path) -> None:
    files = _fixture_files(tmp_path)
    out = tmp_path / "guard.json"

    result = write_guard(
        inventory_path=files["inventory"],
        dinov2_audit_path=files["dinov2"],
        siglip_audit_path=files["siglip"],
        out=out,
    )

    assert json.loads(out.read_text()) == result
    assert result["warnings_total"] == 1
