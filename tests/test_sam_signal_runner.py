import json
import subprocess
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "docs/benchmarks/learning/open_source_model_catalog_v1.json"


def _example_with_source(source_image: str, case_type: str = "decompose_case") -> dict:
    return {
        "example_id": "tiny_test",
        "source_case": {
            "case_type": case_type,
            "case_id": "case_test",
            "schema_version": 1,
        },
        "input": {
            "case_record": {
                "case_type": case_type,
                "case_id": "case_test",
                "source_image": source_image,
            }
        },
    }


class FakeSamBackend:
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
            "masks": [
                {
                    "area_pixels": 8,
                    "bbox": [0, 0, 4, 2],
                    "predicted_iou": 0.91,
                    "stability_score": 0.87,
                },
                {
                    "area_pixels": 4,
                    "bbox": [4, 2, 2, 2],
                    "predicted_iou": 0.72,
                    "stability_score": 0.66,
                },
            ],
            "boundary_complexity": {
                "mean_edge_density": 0.18,
                "high_complexity_mask_count": 1,
            },
        }


def test_sam_runner_returns_mask_coverage_and_boundary_signals(tmp_path):
    from vulca.learning.sam_signal_runner import build_sam_vit_signal_runner

    image_path = tmp_path / "source.png"
    Image.new("RGB", (8, 6), (255, 255, 255)).save(image_path)
    backend = FakeSamBackend()
    runner = build_sam_vit_signal_runner(
        repo_root=tmp_path,
        backend=backend,
    )

    signals = runner(
        _example_with_source("source.png"),
        {"id": "segment_anything_sam_vit", "model_role": "mask_proposal"},
    )

    assert signals["status"] == "completed"
    assert signals["signal_source"] == "local_runner"
    assert signals["label_source"] == "assistant_labeled"
    assert signals["review_status"] == "needs_human_review"
    assert signals["mask_count"] == 2
    assert signals["total_mask_area_pct"] == 25.0
    assert signals["mask_coverage_candidates"] == [
        {
            "area_pct": 16.6667,
            "bbox": [0, 0, 4, 2],
            "predicted_iou": 0.91,
            "stability_score": 0.87,
        },
        {
            "area_pct": 8.3333,
            "bbox": [4, 2, 2, 2],
            "predicted_iou": 0.72,
            "stability_score": 0.66,
        },
    ]
    assert signals["boundary_complexity"] == {
        "mean_edge_density": 0.18,
        "high_complexity_mask_count": 1,
    }
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
            "model_id": "segment_anything_sam_vit",
        }
    ]


def test_sam_runner_skips_private_source_without_leaking_ref(tmp_path):
    from vulca.learning.sam_signal_runner import build_sam_vit_signal_runner

    runner = build_sam_vit_signal_runner(
        repo_root=tmp_path,
        backend=FakeSamBackend(),
    )

    signals = runner(
        _example_with_source("private://local_path/abc/source.png"),
        {"id": "segment_anything_sam_vit", "model_role": "mask_proposal"},
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


def test_open_model_adapter_enables_sam_local_runner_with_factory(tmp_path):
    from vulca.learning.open_model_signals import run_open_model_signal_adapter
    from vulca.learning.sam_signal_runner import build_sam_vit_signal_runner

    image_path = tmp_path / "source.png"
    Image.new("RGB", (4, 3), (0, 255, 0)).save(image_path)
    case_log = tmp_path / "cases.jsonl"
    case_log.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "case_type": "decompose_case",
                "case_id": "local_sam_case",
                "created_at": "2026-05-06T00:00:00Z",
                "input": {
                    "source_image": str(image_path),
                },
                "review": {
                    "human_accept": False,
                    "failure_type": "under_segmentation",
                    "preferred_action": "split_layer_further",
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
                        "source_id": "local_sam_case_log",
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
    backend = FakeSamBackend()

    report = run_open_model_signal_adapter(
        repo_root=ROOT,
        output_path=output_path,
        report_path=report_path,
        model_catalog_path=CATALOG,
        case_source_manifest_path=manifest,
        model_ids=("segment_anything_sam_vit",),
        include_local_seeds=False,
        enable_local_runners=("segment_anything_sam_vit",),
        local_runner_factories={
            "segment_anything_sam_vit": lambda **kwargs: build_sam_vit_signal_runner(
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
    assert records[0]["signals"]["status"] == "completed"
    assert records[0]["signals"]["signal_source"] == "local_runner"
    assert records[0]["signals"]["label_source"] == "assistant_labeled"
    assert records[0]["signals"]["mask_count"] == 2
    assert records[0]["training_use"]["review_status"] == "needs_human_review"
    assert "review" not in json.dumps(records[0]["input_summary"], sort_keys=True)


def test_open_model_signal_adapter_cli_exposes_sam_local_runner_flags():
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
    assert "--sam-checkpoint" in result.stdout
    assert "--sam-model-type" in result.stdout
    assert "--sam-device" in result.stdout
    assert "--sam-points-per-side" in result.stdout
