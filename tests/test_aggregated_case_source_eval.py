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
AGGREGATED_SCRIPT = ROOT / "scripts" / "aggregated_case_source_eval.py"

MANUAL_CURATED_FAILURE_TAXONOMY = {
    "pasteback_mismatch",
    "mask_leak",
    "style_drift",
    "layer_order",
    "occlusion",
    "over_segmentation",
    "under_segmentation",
    "prompt_ambiguity",
}


def _run_aggregated(tmp_path, *extra_args):
    output_dir = tmp_path / "aggregated_case_source_eval"
    report_path = tmp_path / "aggregated_case_source_eval_report.json"
    result = subprocess.run(
        [
            sys.executable,
            str(AGGREGATED_SCRIPT),
            "--repo-root",
            str(ROOT),
            "--output-dir",
            str(output_dir),
            "--report",
            str(report_path),
            *extra_args,
        ],
        capture_output=True,
        text=True,
        timeout=30,
        env=CLI_ENV,
        cwd=ROOT,
    )
    return result, output_dir, report_path


def test_default_aggregated_report_includes_local_seeds_manual_sources_and_policy_comparison(
    tmp_path,
):
    result, output_dir, report_path = _run_aggregated(tmp_path)

    assert result.returncode == 0, result.stderr
    assert report_path.exists()
    assert (output_dir / "tiny_training_eval_report.json").exists()

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["case_type"] == "learning_aggregated_case_source_eval_report"
    assert report["dataset_summary"]["example_count"] == 20

    bucket_metrics = report["bucket_metrics"]
    assert bucket_metrics["source_id"]["manual_curated_cases_v1"]["example_count"] == 8
    assert bucket_metrics["source.kind"]["local_seed"]["example_count"] == 12
    assert MANUAL_CURATED_FAILURE_TAXONOMY.issubset(
        set(bucket_metrics["targets.failure_type"])
    )

    policy_reports = report["policy_comparison"]["policy_reports"]
    assert (
        policy_reports["tiny_action_model_v1"]["action_accuracy"]
        >= policy_reports["tiny_agent_v0"]["action_accuracy"]
    )

    assert set(report["mismatches_by_bucket"]) >= {"source_id", "targets.failure_type"}
    for bucket_name in ("source_id", "targets.failure_type"):
        assert set(report["mismatches_by_bucket"][bucket_name]) >= {
            "tiny_agent_v0",
            "tiny_action_model_v1",
        }
        assert isinstance(
            report["mismatches_by_bucket"][bucket_name]["tiny_action_model_v1"],
            dict,
        )

    assert "Source summary:" in result.stdout
    assert "manual_curated_cases_v1: 8" in result.stdout
    assert "source.kind local_seed: 12" in result.stdout
    assert "Taxonomy summary:" in result.stdout
    assert "prompt_ambiguity: 1" in result.stdout
