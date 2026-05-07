from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CLI_ENV = dict(
    os.environ,
    PYTHONPATH=str(ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
)


def _write_audit_report(tmp_path: Path) -> Path:
    audit = {
        "schema_version": 1,
        "case_type": "learning_real_source_context_audit_report",
        "status": "needs_review",
        "summary": {
            "real_user_case_count": 3,
            "source_context_available_count": 2,
            "source_context_unavailable_count": 1,
            "prediction_changed_with_source_context_count": 1,
            "source_context_feature_matched_count": 2,
            "review_candidate_count": 3,
        },
        "records": [
            {
                "case_id": "changed_by_source",
                "case_type": "layer_generate_case",
                "source": {
                    "source_id": "real_user_fixture",
                    "kind": "user_case_log",
                    "privacy_scope": "private",
                    "curation_status": "reviewed",
                    "record_index": 0,
                    "split": "test",
                },
                "targets": {
                    "preferred_action": "manual_review",
                    "failure_type": "",
                },
                "source_context": {
                    "available": True,
                    "signal_count": 1,
                    "tags": ["source_tag:tang_mural", "source_tag:registry_ambiguity"],
                    "source_image_available": False,
                    "source_artifact_available_count": 1,
                    "source_artifact_kind_counts": {"directory": 1},
                    "source_artifact_text_file_count": 2,
                },
                "predictions": {
                    "full_action": "manual_review",
                    "without_auxiliary_signals_action": "adjust_prompt",
                    "action_changed_with_source_context": True,
                    "full_matches_target": True,
                    "without_auxiliary_signals_matches_target": False,
                },
                "model_explanation": {
                    "source_context_feature_match_count": 2,
                    "matched_source_context_features": [
                        "aux_signal.source_context_tag:source_tag:tang_mural"
                    ],
                    "fallback_reason": "scored_features",
                },
                "candidate_reason": "prediction_changed_with_source_context",
                "recommended_review_action": "human_review_source_dependency",
            },
            {
                "case_id": "used_no_change",
                "case_type": "decompose_case",
                "source": {
                    "source_id": "real_user_fixture",
                    "kind": "user_case_log",
                    "privacy_scope": "private",
                    "curation_status": "reviewed",
                    "record_index": 1,
                    "split": "test",
                },
                "targets": {
                    "preferred_action": "split_layer_further",
                    "failure_type": "under_segmentation",
                },
                "source_context": {
                    "available": True,
                    "signal_count": 1,
                    "tags": ["source_image:present", "source_image.aspect:landscape"],
                    "source_image_available": True,
                    "source_artifact_available_count": 0,
                    "source_artifact_kind_counts": {},
                    "source_artifact_text_file_count": 0,
                },
                "predictions": {
                    "full_action": "split_layer_further",
                    "without_auxiliary_signals_action": "split_layer_further",
                    "action_changed_with_source_context": False,
                    "full_matches_target": True,
                    "without_auxiliary_signals_matches_target": True,
                },
                "model_explanation": {
                    "source_context_feature_match_count": 1,
                    "matched_source_context_features": [
                        "aux_signal.source_image:present"
                    ],
                    "fallback_reason": "scored_features",
                },
                "candidate_reason": "source_context_used_no_action_change",
                "recommended_review_action": "verify_source_dependency_label",
            },
            {
                "case_id": "missing_source_context",
                "case_type": "layer_generate_case",
                "source": {
                    "source_id": "real_user_fixture",
                    "kind": "user_case_log",
                    "privacy_scope": "private",
                    "curation_status": "reviewed",
                    "record_index": 2,
                    "split": "test",
                },
                "targets": {
                    "preferred_action": "manual_review",
                    "failure_type": "prompt_ambiguity",
                },
                "source_context": {
                    "available": False,
                    "signal_count": 0,
                    "tags": [],
                    "source_image_available": False,
                    "source_artifact_available_count": 0,
                    "source_artifact_kind_counts": {},
                    "source_artifact_text_file_count": 0,
                },
                "predictions": {
                    "full_action": "manual_review",
                    "without_auxiliary_signals_action": "manual_review",
                    "action_changed_with_source_context": False,
                    "full_matches_target": True,
                    "without_auxiliary_signals_matches_target": True,
                },
                "model_explanation": {
                    "source_context_feature_match_count": 0,
                    "matched_source_context_features": [],
                    "fallback_reason": "failure_hint_prior",
                },
                "candidate_reason": "needs_source_context",
                "recommended_review_action": "recover_source_context",
            },
        ],
    }
    path = tmp_path / "real_source_context_audit_report.json"
    path.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _write_recovery_report(tmp_path: Path, audit_report_path: Path) -> Path:
    output_dir = tmp_path / "recovery"
    audit_dir = output_dir / "audit"
    audit_dir.mkdir(parents=True)
    copied_audit = audit_dir / "real_source_context_audit_report.json"
    copied_audit.write_text(audit_report_path.read_text(encoding="utf-8"), encoding="utf-8")
    report = {
        "schema_version": 1,
        "case_type": "learning_real_source_context_recovery_audit_report",
        "status": "source_context_ready_for_review",
        "artifacts": {
            "audit_report_path": "audit/real_source_context_audit_report.json",
        },
        "summary": {
            "real_user_case_count": 3,
            "source_context_available_count": 2,
            "source_context_unavailable_count": 1,
            "review_candidate_count": 3,
        },
    }
    path = output_dir / "real_source_context_recovery_audit_report.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_real_source_dependency_review_writes_safe_human_review_pack(tmp_path):
    from vulca.learning.real_source_dependency_review import (
        write_real_source_dependency_review_pack,
    )

    audit_report = _write_audit_report(tmp_path)
    output_dir = tmp_path / "review"

    report = write_real_source_dependency_review_pack(
        audit_report_path=audit_report,
        output_dir=output_dir,
    )

    assert report["case_type"] == "learning_real_source_dependency_review_report"
    assert report["status"] == "needs_human_review"
    assert report["summary"] == {
        "audit_record_count": 3,
        "review_item_count": 3,
        "counts_by_suggested_source_dependency": {
            "helpful": 1,
            "required": 1,
            "unknown": 1,
        },
        "counts_by_suggested_decision_basis": {
            "artifact_source": 1,
            "image_source": 1,
            "unknown": 1,
        },
        "counts_by_review_priority": {
            "high": 1,
            "medium": 1,
            "recovery": 1,
        },
    }
    assert report["artifacts"] == {
        "report_path": "real_source_dependency_review_report.json",
        "review_template_jsonl_path": "real_source_dependency_review.template.jsonl",
        "markdown_checklist_path": "real_source_dependency_review.md",
    }

    items = _read_jsonl(output_dir / "real_source_dependency_review.template.jsonl")
    assert [item["case_id"] for item in items] == [
        "changed_by_source",
        "missing_source_context",
        "used_no_change",
    ]
    changed = items[0]
    assert changed["suggested_review"] == {
        "source_dependency": "required",
        "decision_basis": "artifact_source",
        "review_priority": "high",
    }
    assert changed["human_review"] == {
        "source_dependency": "unknown",
        "decision_basis": "unknown",
        "preferred_action_confirmed": None,
        "corrected_preferred_action": "",
        "review_notes": "",
    }
    assert changed["allowed_values"]["source_dependency"] == [
        "required",
        "helpful",
        "not_needed",
        "unknown",
    ]
    assert changed["allowed_values"]["decision_basis"] == [
        "metadata_only",
        "source_context",
        "image_source",
        "artifact_source",
        "unknown",
    ]

    markdown = (output_dir / "real_source_dependency_review.md").read_text(
        encoding="utf-8"
    )
    assert "changed_by_source" in markdown
    assert "missing_source_context" in markdown
    assert "used_no_change" in markdown
    assert "source_dependency" in markdown

    encoded = json.dumps(report, sort_keys=True)
    encoded += "\n".join(json.dumps(item, sort_keys=True) for item in items)
    encoded += markdown
    assert str(tmp_path) not in encoded
    assert "private://local_path" not in encoded
    assert "/Users/" not in encoded


def test_real_source_dependency_review_accepts_recovery_audit_report(tmp_path):
    from vulca.learning.real_source_dependency_review import (
        write_real_source_dependency_review_pack,
    )

    audit_report = _write_audit_report(tmp_path)
    recovery_report = _write_recovery_report(tmp_path, audit_report)

    report = write_real_source_dependency_review_pack(
        audit_report_path=recovery_report,
        output_dir=tmp_path / "review",
    )

    assert report["inputs"]["source_report_case_type"] == (
        "learning_real_source_context_recovery_audit_report"
    )
    assert report["summary"]["review_item_count"] == 3


def test_real_source_dependency_review_cli_writes_pack(tmp_path):
    audit_report = _write_audit_report(tmp_path)
    output_dir = tmp_path / "review"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/real_source_dependency_review.py"),
            "--audit-report",
            str(audit_report),
            "--output-dir",
            str(output_dir),
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(
        (output_dir / "real_source_dependency_review_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["summary"]["review_item_count"] == 3
    assert "Real source dependency review:" in result.stdout
    assert "Review items: 3" in result.stdout
