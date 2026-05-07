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
SCRIPT = ROOT / "scripts" / "fallback_residual_audit.py"


def _decision(
    case_id: str,
    *,
    case_type: str,
    action: str,
    confidence: float,
    failure_hint: str,
    fallback_reasons: list[str],
    data_gap_tags: list[str] | None = None,
    source_context_available: bool = True,
) -> dict:
    return {
        "schema_version": 1,
        "case_type": "learning_dry_run_decision",
        "example_id": f"tiny_{case_id}",
        "case_id": case_id,
        "source_case_type": case_type,
        "action_router": {
            "policy_name": "tiny_action_model_v1",
            "recommended_action": action,
            "confidence": confidence,
            "failure_hint": failure_hint,
            "rule_reason": "fixture",
        },
        "source_dependency_router": {
            "recommended_source_dependency": "required",
            "recommended_decision_basis": "artifact_source",
            "confidence": 0.8,
            "rule_reason": "fixture",
        },
        "source_context": {
            "available": source_context_available,
            "source": "auxiliary_signal" if source_context_available else "",
            "signal_count": 1 if source_context_available else 0,
        },
        "dispatch": {
            "fallback_agent": True,
            "fallback_reasons": fallback_reasons,
            "data_gap_tags": data_gap_tags or [],
            "decision_owner": "tiny_model",
            "execution_owner": "fallback_agent",
        },
    }


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )


def _fixture_decisions() -> list[dict]:
    return [
        _decision(
            "seed_low_confidence",
            case_type="layer_generate_case",
            action="accept",
            confidence=0.4,
            failure_hint="",
            fallback_reasons=["low_action_confidence"],
            data_gap_tags=["low_action_confidence"],
        ),
        _decision(
            "redraw_under_split",
            case_type="redraw_case",
            action="fallback_to_agent",
            confidence=0.82,
            failure_hint="under_split",
            fallback_reasons=["action_fallback_to_agent"],
        ),
        _decision(
            "decompose_occlusion",
            case_type="decompose_case",
            action="fallback_to_agent",
            confidence=0.82,
            failure_hint="occlusion",
            fallback_reasons=["action_fallback_to_agent"],
        ),
        _decision(
            "layer_provider_failure",
            case_type="layer_generate_case",
            action="fallback_to_agent",
            confidence=0.88,
            failure_hint="provider_failure",
            fallback_reasons=["action_fallback_to_agent"],
            source_context_available=False,
        ),
        _decision(
            "manual_provider_failure",
            case_type="layer_generate_case",
            action="fallback_to_agent",
            confidence=0.88,
            failure_hint="provider_failure",
            fallback_reasons=["action_fallback_to_agent"],
            source_context_available=False,
        ),
        _decision(
            "resolved_case",
            case_type="redraw_case",
            action="adjust_mask",
            confidence=0.91,
            failure_hint="mask_leak",
            fallback_reasons=[],
        )
        | {"dispatch": {"fallback_agent": False, "fallback_reasons": [], "data_gap_tags": []}},
    ]


def test_fallback_residual_audit_classifies_remaining_agent_work(tmp_path):
    from vulca.learning.fallback_residual_audit import run_fallback_residual_audit

    decision_path = tmp_path / "dry_run_decisions.jsonl"
    report_path = tmp_path / "fallback_residual_audit_report.json"
    _write_jsonl(decision_path, _fixture_decisions())

    report = run_fallback_residual_audit(
        decision_path=decision_path,
        report_path=report_path,
    )

    assert report["case_type"] == "learning_fallback_residual_audit_report"
    assert report["status"] == "needs_agent_or_router_boundary_work"
    assert report["summary"] == {
        "decision_count": 6,
        "fallback_agent_count": 5,
        "agent_required_count": 4,
        "tiny_router_candidate_count": 1,
        "source_context_gap_count": 0,
    }
    assert report["counts_by_residual_kind"] == {
        "agent_boundary_complex_visual_ownership": 2,
        "provider_runtime_fallback": 2,
        "tiny_router_confidence_gap": 1,
    }
    assert report["counts_by_recommended_next_step"] == {
        "keep_agent_boundary": 2,
        "route_provider_failure_to_runtime_handler": 2,
        "add_confidence_calibration_or_label": 1,
    }
    assert [item["case_id"] for item in report["residual_cases"]] == [
        "decompose_occlusion",
        "redraw_under_split",
        "layer_provider_failure",
        "manual_provider_failure",
        "seed_low_confidence",
    ]
    seed = next(item for item in report["residual_cases"] if item["case_id"] == "seed_low_confidence")
    assert seed["residual_kind"] == "tiny_router_confidence_gap"
    assert seed["recommended_next_step"] == "add_confidence_calibration_or_label"
    assert report_path.exists()


def test_fallback_residual_audit_cli_writes_summary(tmp_path):
    decision_path = tmp_path / "dry_run_decisions.jsonl"
    report_path = tmp_path / "fallback_residual_audit_report.json"
    _write_jsonl(decision_path, _fixture_decisions())

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--decision-path",
            str(decision_path),
            "--report",
            str(report_path),
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Fallback residual audit:" in result.stdout
    assert "Fallback agent decisions: 5" in result.stdout
    assert "Tiny router candidates: 1" in result.stdout
    assert "Agent-required residuals: 4" in result.stdout
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["summary"]["fallback_agent_count"] == 5
