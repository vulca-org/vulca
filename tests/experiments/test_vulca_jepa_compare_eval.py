from __future__ import annotations

import json
from pathlib import Path

from scripts.experiments.vulca_jepa_compare_eval import build_report_data, render_report, write_report


def _write_json(path: Path, data: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False))
    return path


def _fixture_files(tmp_path: Path) -> dict[str, Path]:
    inventory = {
        "samples_total": 4,
        "missing_total": 0,
        "audit_sets": {"core": 3, "artifact_qa": 1},
        "samples": [
            {
                "sample_id": "gongbi_baseline_failed_subject",
                "group": "gallery_promptfix",
                "path": "gallery/chinese_gongbi.png",
                "prompt": "工笔牡丹",
                "audit_set": "core",
                "usable_for_embedding": True,
                "reject_reasons": [],
            },
            {
                "sample_id": "gongbi_promptfix_seed1",
                "group": "gallery_promptfix",
                "path": "gallery-promptfix/chinese_gongbi_seed1.png",
                "prompt": "single peony",
                "audit_set": "core",
                "usable_for_embedding": True,
                "reject_reasons": [],
            },
            {
                "sample_id": "xieyi_promptfix",
                "group": "gallery_promptfix",
                "path": "gallery-promptfix/chinese_xieyi.png",
                "prompt": "xieyi landscape",
                "audit_set": "core",
                "usable_for_embedding": True,
                "reject_reasons": [],
            },
            {
                "sample_id": "black",
                "group": "edit_inpaint",
                "path": "black.png",
                "prompt": "",
                "audit_set": "artifact_qa",
                "usable_for_embedding": False,
                "reject_reasons": ["near_black_opaque"],
            },
        ],
    }
    dinov2 = {
        "backend": "dinov2",
        "status": "ok",
        "model": "fake-dino",
        "samples_total": 3,
        "pairwise_distances_total": 3,
        "anomaly_ranking": [
            {
                "sample_id": "gongbi_baseline_failed_subject",
                "mean_distance": 1.2,
                "nearest_sample_id": "xieyi_promptfix",
                "nearest_distance": 0.4,
            }
        ],
        "excluded_samples": [{"sample_id": "black"}],
    }
    siglip = {
        "backend": "siglip",
        "status": "ok",
        "model": "fake-siglip",
        "samples_total": 3,
        "text_image_scores_total": 3,
        "samples": [
            {"sample_id": "gongbi_baseline_failed_subject", "probability": 0.01, "logit": -4, "text_source": "prompt"},
            {"sample_id": "gongbi_promptfix_seed1", "probability": 0.25, "logit": 1, "text_source": "prompt"},
            {"sample_id": "xieyi_promptfix", "probability": 0.3, "logit": 2, "text_source": "prompt"},
        ],
        "excluded_samples": [{"sample_id": "black"}],
    }
    guard = {
        "schema_version": "vulca_jepa_guard.v1",
        "status": "ok",
        "non_blocking": True,
        "guard_scope": "gallery_promptfix",
        "samples_evaluated": 3,
        "warnings_total": 1,
        "rules": {
            "subject_drift_warning": {
                "action": "warn_only",
                "siglip_probability_max": 0.001,
                "requires_nearest_family_mismatch": True,
            }
        },
        "warnings": [
            {
                "sample_id": "gongbi_baseline_failed_subject",
                "warning_type": "subject_drift_warning",
                "action": "warn_only",
                "signals": {
                    "nearest_sample_id": "xieyi_promptfix",
                    "siglip_probability": 0.00008,
                },
            }
        ],
    }
    gemini = {
        "items": [
            {
                "kind": "baseline",
                "tradition": "chinese_gongbi",
                "path": "gallery/chinese_gongbi.png",
                "total": 0,
                "passed": False,
                "scores": {"notes": "landscape instead of peony"},
            },
            {
                "kind": "experimental",
                "tradition": "chinese_gongbi",
                "seed": 1,
                "path": "gallery-promptfix/chinese_gongbi_seed1.png",
                "total": 4,
                "passed": True,
                "scores": {"notes": "peony"},
            },
        ]
    }
    eval_dir = tmp_path / "eval"
    _write_json(eval_dir / "chinese_gongbi_scores.json", {"L1": 0.8, "L2": 0.6, "L3": 0.7, "L4": 0.9, "L5": 0.5})

    return {
        "inventory": _write_json(tmp_path / "inventory.json", inventory),
        "dinov2": _write_json(tmp_path / "dinov2.json", dinov2),
        "siglip": _write_json(tmp_path / "siglip.json", siglip),
        "guard": _write_json(tmp_path / "guard.json", guard),
        "gemini": _write_json(tmp_path / "gemini.json", gemini),
        "eval_dir": eval_dir,
    }


def test_build_report_data_matches_eval_and_gemini(tmp_path: Path) -> None:
    files = _fixture_files(tmp_path)

    data = build_report_data(
        inventory_path=files["inventory"],
        dinov2_audit_path=files["dinov2"],
        siglip_audit_path=files["siglip"],
        eval_dir=files["eval_dir"],
        gemini_rescore_path=files["gemini"],
        guard_path=files["guard"],
    )

    assert data["counts"]["core_samples"] == 3
    assert data["counts"]["artifact_qa_samples"] == 1
    assert data["counts"]["matched_eval_files"] == 1
    assert data["counts"]["matched_gemini_items"] == 2
    assert data["gongbi_case"]["gemini_baseline_total"] == 0
    assert data["gongbi_case"]["dinov2_baseline_nearest"] == "xieyi_promptfix"
    assert data["gongbi_case"]["siglip_baseline_probability"] == 0.01
    assert data["gongbi_case"]["siglip_promptfix_best_probability"] == 0.25
    assert data["guard"]["warnings_total"] == 1
    assert data["guard"]["warnings"][0]["sample_id"] == "gongbi_baseline_failed_subject"


def test_render_report_contains_chinese_conclusions(tmp_path: Path) -> None:
    files = _fixture_files(tmp_path)
    data = build_report_data(
        inventory_path=files["inventory"],
        dinov2_audit_path=files["dinov2"],
        siglip_audit_path=files["siglip"],
        eval_dir=files["eval_dir"],
        gemini_rescore_path=files["gemini"],
        guard_path=files["guard"],
    )

    report = render_report(data)

    assert "# Vulca JEPA 视觉审计实验报告" in report
    assert "core=3" in report
    assert "artifact_qa=1" in report
    assert "工笔牡丹 baseline" in report
    assert "xieyi_promptfix" in report
    assert "Vulca L1-L5 文化评估观察" in report
    assert "不能替代 Vulca L1-L5" in report
    assert "Guard 原型结果" in report
    assert "subject_drift_warning" in report
    assert "siglip_probability_max" in report
    assert "warn_only" in report
    assert "--eval-inventory" in report
    assert "promptfix 牡丹样本不显示 warning" in report


def test_write_report_outputs_markdown(tmp_path: Path) -> None:
    files = _fixture_files(tmp_path)
    out = tmp_path / "report.md"

    report = write_report(
        inventory_path=files["inventory"],
        dinov2_audit_path=files["dinov2"],
        siglip_audit_path=files["siglip"],
        eval_dir=files["eval_dir"],
        gemini_rescore_path=files["gemini"],
        guard_path=files["guard"],
        out=out,
    )

    assert out.read_text() == report
    assert "matched_gemini_items=2" in report
    assert "warnings=1" in report
