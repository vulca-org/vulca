import json
import subprocess
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "docs/benchmarks/learning/open_source_model_catalog_v1.json"
COMBINED_MANIFEST = (
    ROOT / "docs/benchmarks/learning/combined_case_source_manifest_v1.json"
)


def _example_with_source(source_image: str) -> dict:
    return {
        "example_id": "tiny_test",
        "source_case": {
            "case_type": "redraw_case",
            "case_id": "case_test",
            "schema_version": 1,
        },
        "input": {
            "case_record": {
                "case_type": "redraw_case",
                "case_id": "case_test",
                "source_image": source_image,
            }
        },
    }


class FakeFlorenceBackend:
    def __init__(self):
        self.calls = []

    def run(self, image_path, *, case_record, model_spec):
        self.calls.append(
            {
                "image_path": str(image_path),
                "case_id": case_record["case_id"],
                "model_id": model_spec["id"],
            }
        )
        return {
            "caption_candidates": ["a small red square"],
            "ocr_text": ["SALE"],
            "dense_region_descriptions": ["red square centered on canvas"],
        }


def test_florence_runner_returns_local_assistant_labeled_signals(tmp_path):
    from vulca.learning.florence_signal_runner import build_florence2_signal_runner

    image_path = tmp_path / "source.png"
    Image.new("RGB", (8, 6), (255, 0, 0)).save(image_path)
    backend = FakeFlorenceBackend()
    runner = build_florence2_signal_runner(
        repo_root=tmp_path,
        backend=backend,
    )

    signals = runner(
        _example_with_source("source.png"),
        {"id": "florence_2", "model_role": "vision_caption_grounding_ocr"},
    )

    assert signals["status"] == "completed"
    assert signals["signal_source"] == "local_runner"
    assert signals["label_source"] == "assistant_labeled"
    assert signals["review_status"] == "needs_human_review"
    assert signals["caption_candidates"] == ["a small red square"]
    assert signals["ocr_text"] == ["SALE"]
    assert signals["ocr_text_count"] == 1
    assert signals["source_image"] == {
        "available": True,
        "ref_kind": "repo_relative",
        "width": 8,
        "height": 6,
    }
    assert backend.calls == [
        {
            "image_path": str(image_path),
            "case_id": "case_test",
            "model_id": "florence_2",
        }
    ]


def test_florence_runner_skips_private_or_missing_source_without_leaking_path(tmp_path):
    from vulca.learning.florence_signal_runner import build_florence2_signal_runner

    runner = build_florence2_signal_runner(
        repo_root=tmp_path,
        backend=FakeFlorenceBackend(),
    )

    signals = runner(
        _example_with_source("private://local_path/abc/source.png"),
        {"id": "florence_2", "model_role": "vision_caption_grounding_ocr"},
    )

    encoded = json.dumps(signals, sort_keys=True)
    assert signals["status"] == "skipped"
    assert signals["skip_reason"] == "source_image_unavailable"
    assert signals["signal_source"] == "local_runner"
    assert signals["review_status"] == "needs_human_review"
    assert signals["source_image"] == {
        "available": False,
        "ref_kind": "private_uri",
    }
    assert "private://local_path" not in encoded
    assert "/Users/" not in encoded


def test_open_model_adapter_enables_florence_local_runner_with_factory(tmp_path):
    from vulca.learning.florence_signal_runner import build_florence2_signal_runner
    from vulca.learning.open_model_signals import run_open_model_signal_adapter

    image_path = tmp_path / "source.png"
    Image.new("RGB", (4, 3), (0, 0, 255)).save(image_path)
    case_log = tmp_path / "cases.jsonl"
    case_log.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "case_type": "redraw_case",
                "case_id": "local_florence_case",
                "created_at": "2026-05-06T00:00:00Z",
                "source_image": str(image_path),
                "review": {
                    "human_accept": False,
                    "failure_type": "style_drift",
                    "preferred_action": "adjust_instruction",
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "case_type": "learning_tiny_case_source_manifest",
                "sources": [
                    {
                        "source_id": "local_florence_case_log",
                        "kind": "manual_case_log",
                        "path": str(case_log),
                        "privacy_scope": "project",
                        "curation_status": "curated",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    output_path = tmp_path / "signals.jsonl"
    report_path = tmp_path / "report.json"
    backend = FakeFlorenceBackend()

    report = run_open_model_signal_adapter(
        repo_root=ROOT,
        output_path=output_path,
        report_path=report_path,
        model_catalog_path=CATALOG,
        case_source_manifest_path=manifest,
        model_ids=("florence_2",),
        include_local_seeds=False,
        enable_local_runners=("florence_2",),
        local_runner_factories={
            "florence_2": lambda **kwargs: build_florence2_signal_runner(
                backend=backend,
                **kwargs,
            )
        },
    )

    records = [
        json.loads(line)
        for line in output_path.read_text(encoding="utf-8").splitlines()
    ]
    assert report["record_count"] == 1
    assert report["runtime"]["uses_local_runner"] is True
    assert report["runtime"]["calls_model_provider"] is False
    assert report["runtime"]["downloads_weights"] is False
    assert report["runtime"]["weight_download_enabled"] is False
    assert records[0]["signals"]["status"] == "completed"
    assert records[0]["signals"]["signal_source"] == "local_runner"
    assert records[0]["signals"]["label_source"] == "assistant_labeled"
    assert records[0]["training_use"]["review_status"] == "needs_human_review"
    assert "review" not in json.dumps(records[0]["input_summary"], sort_keys=True)


def test_open_model_signal_adapter_cli_exposes_local_runner_flags():
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/open_model_signal_adapter.py"),
            "--help",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--enable-local-runner" in result.stdout
    assert "--allow-weight-download" in result.stdout
    assert "--max-examples" in result.stdout
