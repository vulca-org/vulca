import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CLI_ENV = dict(
    os.environ,
    PYTHONPATH=str(ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
)


def _read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_build_tiny_dataset_from_local_seeds_strips_label_leakage():
    from vulca.learning.tiny_dataset import build_tiny_dataset_examples

    examples = build_tiny_dataset_examples(repo_root=ROOT)

    assert len(examples) == 12
    assert {
        item["source_case"]["case_type"] for item in examples
    } == {"redraw_case", "decompose_case", "layer_generate_case"}
    assert sum(
        1 for item in examples if item["source_case"]["case_type"] == "redraw_case"
    ) == 6
    assert sum(
        1
        for item in examples
        if item["source_case"]["case_type"] == "decompose_case"
    ) == 1
    assert sum(
        1
        for item in examples
        if item["source_case"]["case_type"] == "layer_generate_case"
    ) == 5

    first = examples[0]
    assert first["case_type"] == "learning_tiny_dataset_example"
    assert first["schema_version"] == 1
    assert first["source"]["kind"] == "local_seed"
    assert first["targets"]["preferred_action"]
    assert first["tasks"]["tiny_agent"]["next_action_policy"] == first["targets"][
        "preferred_action"
    ]

    encoded_inputs = json.dumps([item["input"] for item in examples], sort_keys=True)
    assert '"review"' not in encoded_inputs
    assert '"learning_targets"' not in encoded_inputs
    assert '"accepted"' not in encoded_inputs


def test_write_tiny_dataset_writes_jsonl_and_index(tmp_path):
    from vulca.learning.tiny_dataset import write_tiny_dataset

    output_path = tmp_path / "tiny_dataset.jsonl"

    result = write_tiny_dataset(repo_root=ROOT, output_path=output_path)

    assert result.output_path == str(output_path)
    assert result.example_count == 12
    assert result.counts_by_case_type == {
        "decompose_case": 1,
        "layer_generate_case": 5,
        "redraw_case": 6,
    }
    assert Path(result.index_path).exists()

    records = _read_jsonl(output_path)
    index = json.loads(Path(result.index_path).read_text(encoding="utf-8"))
    assert len(records) == 12
    assert index["case_type"] == "learning_tiny_dataset_index"
    assert index["example_count"] == 12
    assert index["counts_by_case_type"]["layer_generate_case"] == 5
    assert index["counts_by_split"] == {
        "dev": 2,
        "test": 2,
        "train": 8,
    }


def test_tiny_dataset_assigns_deterministic_train_dev_test_splits():
    from vulca.learning.tiny_dataset import build_tiny_dataset_examples

    examples = build_tiny_dataset_examples(repo_root=ROOT)
    repeated = build_tiny_dataset_examples(repo_root=ROOT)

    assert [item["split"] for item in examples] == [
        item["split"] for item in repeated
    ]
    assert Counter(item["split"] for item in examples) == {
        "dev": 2,
        "test": 2,
        "train": 8,
    }

    split_by_case_type = {
        case_type: Counter(
            item["split"]
            for item in examples
            if item["source_case"]["case_type"] == case_type
        )
        for case_type in {item["source_case"]["case_type"] for item in examples}
    }
    assert split_by_case_type["redraw_case"] == {
        "dev": 1,
        "test": 1,
        "train": 4,
    }
    assert split_by_case_type["decompose_case"] == {"train": 1}
    assert split_by_case_type["layer_generate_case"] == {
        "dev": 1,
        "test": 1,
        "train": 3,
    }


def test_tiny_dataset_merges_additional_case_logs(tmp_path):
    from vulca.learning.seed_cases import build_local_seed_cases
    from vulca.learning.tiny_dataset import build_tiny_dataset_examples

    seed = build_local_seed_cases(ROOT)["redraw_case"][0]
    extra = json.loads(json.dumps(seed))
    extra["case_id"] = "redraw_extra_case"
    extra["review"]["preferred_action"] = "manual_review"
    log_path = tmp_path / "extra_redraw_cases.jsonl"
    log_path.write_text(json.dumps(extra) + "\n", encoding="utf-8")

    examples = build_tiny_dataset_examples(
        repo_root=ROOT,
        case_log_paths=[log_path],
    )

    assert len(examples) == 13
    extra_examples = [
        item for item in examples if item["source_case"]["case_id"] == "redraw_extra_case"
    ]
    assert len(extra_examples) == 1
    assert extra_examples[0]["source"]["kind"] == "case_log"
    assert extra_examples[0]["targets"]["preferred_action"] == "manual_review"


def test_cases_export_dataset_cli_writes_dataset(tmp_path):
    output_path = tmp_path / "tiny_dataset.jsonl"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "vulca.cli",
            "cases",
            "export-dataset",
            "--repo-root",
            str(ROOT),
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        timeout=20,
        env=CLI_ENV,
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stderr
    assert output_path.exists()
    assert "Tiny dataset:" in result.stdout
    assert "redraw_case: 6" in result.stdout
    assert "layer_generate_case: 5" in result.stdout
    assert "train: 8" in result.stdout
    assert "dev: 2" in result.stdout
    assert "test: 2" in result.stdout
    assert (tmp_path / "tiny_dataset.index.json").exists()


def test_tiny_dataset_eval_scores_redraw_observable_signal(tmp_path):
    from vulca.learning.tiny_dataset import (
        evaluate_tiny_dataset_examples,
        write_tiny_dataset,
    )

    output_path = tmp_path / "tiny_dataset.jsonl"
    write_tiny_dataset(repo_root=ROOT, output_path=output_path)
    examples = _read_jsonl(output_path)

    report = evaluate_tiny_dataset_examples(
        examples,
        policy_name="redraw_observable_signal",
    )

    assert report["case_type"] == "learning_tiny_dataset_eval_report"
    assert report["policy_name"] == "redraw_observable_signal"
    assert report["example_count"] == 12
    assert report["evaluated_count"] == 6
    assert report["skipped_count"] == 6
    assert report["action_accuracy"] == 1.0
    assert report["mismatches"] == []


def test_tiny_dataset_eval_filters_to_requested_split(tmp_path):
    from vulca.learning.tiny_dataset import (
        evaluate_tiny_dataset_examples,
        write_tiny_dataset,
    )

    output_path = tmp_path / "tiny_dataset.jsonl"
    write_tiny_dataset(repo_root=ROOT, output_path=output_path)
    examples = _read_jsonl(output_path)

    report = evaluate_tiny_dataset_examples(
        examples,
        policy_name="redraw_observable_signal",
        dataset_split="test",
    )

    assert report["split"] == "test"
    assert report["example_count"] == 2
    assert report["evaluated_count"] == 1
    assert report["skipped_by_case_type"] == {"layer_generate_case": 1}
    assert report["action_accuracy"] == 1.0


def test_tiny_dataset_comparison_report_compares_rule_and_majority_baselines(tmp_path):
    from vulca.learning.tiny_dataset import (
        build_tiny_dataset_comparison_report,
        write_tiny_dataset,
    )

    output_path = tmp_path / "tiny_dataset.jsonl"
    write_tiny_dataset(repo_root=ROOT, output_path=output_path)
    examples = _read_jsonl(output_path)

    report = build_tiny_dataset_comparison_report(
        examples,
        train_split="train",
        eval_split="test",
    )

    assert report["case_type"] == "learning_tiny_dataset_comparison_report"
    assert report["train_split"] == "train"
    assert report["eval_split"] == "test"
    assert set(report["policy_reports"]) == {
        "majority_action",
        "redraw_observable_signal",
    }
    assert report["policy_reports"]["majority_action"]["majority_action"] == "accept"
    assert report["policy_reports"]["majority_action"]["evaluated_count"] == 2
    assert report["policy_reports"]["redraw_observable_signal"]["evaluated_count"] == 1
    assert report["ranked_policies"][0]["policy_name"] == "redraw_observable_signal"


def test_tiny_dataset_eval_script_writes_report(tmp_path):
    from vulca.learning.tiny_dataset import write_tiny_dataset

    dataset_path = tmp_path / "tiny_dataset.jsonl"
    report_path = tmp_path / "tiny_dataset_eval.json"
    write_tiny_dataset(repo_root=ROOT, output_path=dataset_path)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "tiny_dataset_eval.py"),
            str(dataset_path),
            "--output",
            str(report_path),
        ],
        capture_output=True,
        text=True,
        timeout=20,
        env=CLI_ENV,
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["evaluated_count"] == 6
    assert report["action_accuracy"] == 1.0
    assert "redraw_observable_signal action_accuracy: 1.0" in result.stdout


def test_tiny_dataset_eval_script_writes_comparison_report(tmp_path):
    from vulca.learning.tiny_dataset import write_tiny_dataset

    dataset_path = tmp_path / "tiny_dataset.jsonl"
    report_path = tmp_path / "tiny_dataset_comparison.json"
    write_tiny_dataset(repo_root=ROOT, output_path=dataset_path)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "tiny_dataset_eval.py"),
            str(dataset_path),
            "--compare",
            "--split",
            "test",
            "--output",
            str(report_path),
        ],
        capture_output=True,
        text=True,
        timeout=20,
        env=CLI_ENV,
        cwd=ROOT,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["case_type"] == "learning_tiny_dataset_comparison_report"
    assert "majority_action action_accuracy:" in result.stdout
    assert "redraw_observable_signal action_accuracy:" in result.stdout
