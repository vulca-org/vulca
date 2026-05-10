"""CLI tests for experimental eval metadata guard hints."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


VULCA = [sys.executable, "-m", "vulca"]
ROOT = Path(__file__).resolve().parents[1]
CLI_ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src")}


def _write_eval_metadata(path: Path) -> Path:
    data = {
        "schema_version": "vulca_eval_metadata.v1",
        "guards": {
            "vulca_jepa_subject_drift": {
                "status": "warning",
                "non_blocking": True,
                "scope": "gallery_promptfix",
                "warnings_total": 1,
                "warnings": [
                    {
                        "sample_id": "gongbi_baseline_failed_subject",
                        "type": "subject_drift_warning",
                        "action": "warn_only",
                        "signals": {
                            "nearest_sample_id": "xieyi_promptfix",
                            "siglip_probability": 0.00008,
                        },
                    }
                ],
            }
        },
    }
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_evaluate_help_exposes_eval_metadata_flag() -> None:
    result = subprocess.run(
        VULCA + ["evaluate", "--help"],
        capture_output=True,
        env=CLI_ENV,
        text=True,
        timeout=10,
    )

    assert result.returncode == 0
    assert "--eval-metadata" in result.stdout


def test_evaluate_json_includes_eval_metadata(tmp_path: Path) -> None:
    metadata = _write_eval_metadata(tmp_path / "eval-metadata.json")

    result = subprocess.run(
        VULCA
        + [
            "evaluate",
            "mock.png",
            "--mock",
            "--json",
            "--eval-metadata",
            str(metadata),
        ],
        capture_output=True,
        env=CLI_ENV,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    subject_guard = data["eval_metadata"]["guards"]["vulca_jepa_subject_drift"]
    assert subject_guard["status"] == "warning"
    assert subject_guard["non_blocking"] is True
    assert subject_guard["warnings"][0]["action"] == "warn_only"


def test_evaluate_json_filters_eval_metadata_by_sample_id(tmp_path: Path) -> None:
    metadata = _write_eval_metadata(tmp_path / "eval-metadata.json")

    result = subprocess.run(
        VULCA
        + [
            "evaluate",
            "mock.png",
            "--mock",
            "--json",
            "--eval-metadata",
            str(metadata),
            "--eval-sample-id",
            "unrelated_sample",
        ],
        capture_output=True,
        env=CLI_ENV,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    subject_guard = data["eval_metadata"]["guards"]["vulca_jepa_subject_drift"]
    assert subject_guard["current_sample_id"] == "unrelated_sample"
    assert subject_guard["status"] == "ok"
    assert subject_guard["warnings_total"] == 0
    assert subject_guard["warnings"] == []


def test_evaluate_text_prints_non_blocking_guard_hint(tmp_path: Path) -> None:
    metadata = _write_eval_metadata(tmp_path / "eval-metadata.json")

    result = subprocess.run(
        VULCA
        + [
            "evaluate",
            "mock.png",
            "--mock",
            "--eval-metadata",
            str(metadata),
            "--eval-sample-id",
            "gongbi_baseline_failed_subject",
        ],
        capture_output=True,
        env=CLI_ENV,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stderr
    assert "Eval Metadata Guards" in result.stdout
    assert "vulca_jepa_subject_drift" in result.stdout
    assert "warn_only" in result.stdout
    assert "non-blocking" in result.stdout


def test_evaluate_text_suppresses_guard_hint_for_other_sample(tmp_path: Path) -> None:
    metadata = _write_eval_metadata(tmp_path / "eval-metadata.json")

    result = subprocess.run(
        VULCA
        + [
            "evaluate",
            "mock.png",
            "--mock",
            "--eval-metadata",
            str(metadata),
            "--eval-sample-id",
            "unrelated_sample",
        ],
        capture_output=True,
        env=CLI_ENV,
        text=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stderr
    assert "Eval Metadata Guards" not in result.stdout
    assert "vulca_jepa_subject_drift" not in result.stdout


def test_create_json_includes_eval_metadata(tmp_path: Path) -> None:
    metadata = _write_eval_metadata(tmp_path / "eval-metadata.json")
    out = tmp_path / "created.png"

    result = subprocess.run(
        VULCA
        + [
            "create",
            "test artwork",
            "--provider",
            "mock",
            "--output",
            str(out),
            "--json",
            "--eval-metadata",
            str(metadata),
        ],
        capture_output=True,
        env=CLI_ENV,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    subject_guard = data["eval_metadata"]["guards"]["vulca_jepa_subject_drift"]
    assert subject_guard["warnings_total"] == 1
    assert subject_guard["warnings"][0]["type"] == "subject_drift_warning"
