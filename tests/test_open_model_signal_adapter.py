import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "docs/benchmarks/learning/open_source_model_catalog_v1.json"
COMBINED_MANIFEST = (
    ROOT / "docs/benchmarks/learning/combined_case_source_manifest_v1.json"
)
CLI_ENV = dict(
    os.environ,
    PYTHONPATH=str(ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
)


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_open_model_signal_adapter_writes_safe_dry_run_records(tmp_path):
    from vulca.learning.open_model_signals import run_open_model_signal_adapter
    from vulca.learning.tiny_dataset import build_tiny_dataset_examples

    output_path = tmp_path / "signals.jsonl"
    report_path = tmp_path / "report.json"

    report = run_open_model_signal_adapter(
        repo_root=ROOT,
        output_path=output_path,
        report_path=report_path,
        model_catalog_path=CATALOG,
        case_source_manifest_path=COMBINED_MANIFEST,
        model_ids=("florence_2", "segment_anything_sam_vit"),
    )

    examples = build_tiny_dataset_examples(
        repo_root=ROOT,
        case_source_manifest_path=COMBINED_MANIFEST,
    )
    expected_count = sum(
        1
        for item in examples
        if item["source_case"]["case_type"]
        in {"redraw_case", "decompose_case", "layer_generate_case"}
    )
    expected_count += sum(
        1
        for item in examples
        if item["source_case"]["case_type"] in {"redraw_case", "decompose_case"}
    )

    records = _read_jsonl(output_path)
    encoded = output_path.read_text(encoding="utf-8")
    assert len(records) == expected_count
    assert report["record_count"] == expected_count
    assert json.loads(report_path.read_text(encoding="utf-8")) == report
    assert "/Users/" not in encoded
    assert "private://local_path/" not in encoded

    counts_by_model = Counter(item["model"]["id"] for item in records)
    assert counts_by_model["florence_2"] == len(examples)
    assert counts_by_model["segment_anything_sam_vit"] == sum(
        1
        for item in examples
        if item["source_case"]["case_type"] in {"redraw_case", "decompose_case"}
    )

    first = records[0]
    assert first["case_type"] == "learning_open_model_signal_record"
    assert first["schema_version"] == 1
    assert first["signal_id"].startswith("open_signal_")
    assert first["model"]["default_runtime_enabled"] is False
    assert first["training_use"] == {
        "default_training_input": False,
        "requires_manual_review_for_training_labels": True,
        "review_status": "needs_human_review",
        "output_training_policy": first["model"]["output_training_policy"],
    }
    assert first["signals"]["status"] == "dry_run_pending_model_execution"
    assert first["signals"]["signal_source"] == "dry_run"
    assert "review" not in json.dumps(first["input_summary"], sort_keys=True)
    assert "learning_targets" not in json.dumps(first["input_summary"], sort_keys=True)


def test_open_model_signal_adapter_rejects_blocked_models_by_default():
    from vulca.learning.open_model_signals import select_open_model_specs

    with pytest.raises(ValueError, match="not eligible for signal pilot"):
        select_open_model_specs(
            CATALOG,
            model_ids=("flux_kontext_dev",),
        )

    with pytest.raises(ValueError, match="unknown open model id"):
        select_open_model_specs(
            CATALOG,
            model_ids=("missing_model",),
        )


def test_open_model_signal_adapter_uses_injected_runner_outputs():
    from vulca.learning.open_model_signals import (
        build_open_model_signal_records,
        select_open_model_specs,
    )
    from vulca.learning.tiny_dataset import build_tiny_dataset_examples

    examples = build_tiny_dataset_examples(
        repo_root=ROOT,
        case_source_manifest_path=COMBINED_MANIFEST,
    )
    model_specs = select_open_model_specs(CATALOG, model_ids=("florence_2",))

    def fake_florence_runner(example, model):
        return {
            "status": "completed",
            "caption_candidates": [
                f"{model['id']} saw {example['source_case']['case_type']}"
            ],
            "ocr_text_count": 0,
        }

    records = build_open_model_signal_records(
        examples[:2],
        model_specs=model_specs,
        runners={"florence_2": fake_florence_runner},
    )

    assert len(records) == 2
    assert records[0]["signals"]["status"] == "completed"
    assert records[0]["signals"]["signal_source"] == "injected_runner"
    assert records[0]["signals"]["caption_candidates"] == [
        f"florence_2 saw {examples[0]['source_case']['case_type']}"
    ]
    assert records[0]["training_use"]["review_status"] == "needs_human_review"


def test_open_model_signal_adapter_passes_private_asset_maps_to_local_runner_factory(
    tmp_path,
):
    from vulca.learning.open_model_signals import run_open_model_signal_adapter

    captured = {}
    asset_map_path = tmp_path / "session.private.asset_map.json"

    def fake_factory(**kwargs):
        captured.update(kwargs)

        def run(_example, _model):
            return {
                "status": "completed",
                "signal_source": "local_runner",
                "review_status": "needs_human_review",
            }

        return run

    report = run_open_model_signal_adapter(
        repo_root=ROOT,
        output_path=tmp_path / "signals.jsonl",
        report_path=tmp_path / "report.json",
        model_catalog_path=CATALOG,
        case_source_manifest_path=COMBINED_MANIFEST,
        model_ids=("florence_2",),
        include_local_seeds=False,
        enable_local_runners=("florence_2",),
        local_runner_factories={"florence_2": fake_factory},
        private_asset_map_paths=(asset_map_path,),
        max_examples=1,
    )

    assert report["runtime"]["uses_local_runner"] is True
    assert captured["private_asset_map_paths"] == (asset_map_path,)


def test_open_model_signal_adapter_cli_writes_report(tmp_path):
    output_path = tmp_path / "signals.jsonl"
    report_path = tmp_path / "report.json"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/open_model_signal_adapter.py"),
            "--output",
            str(output_path),
            "--report",
            str(report_path),
            "--model",
            "florence_2",
            "--model",
            "segment_anything_sam_vit",
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert output_path.exists()
    assert report["case_type"] == "learning_open_model_signal_report"
    assert report["record_count"] == len(_read_jsonl(output_path))
    assert "Open model signal records:" in result.stdout


def test_open_model_signal_adapter_cli_exposes_private_asset_map_flag():
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/open_model_signal_adapter.py"),
            "--help",
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--private-asset-map" in result.stdout
