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


def _example(
    example_id: str,
    *,
    split: str,
    case_id: str,
    preferred_action: str,
    case_record: dict,
) -> dict:
    case_record = {
        "schema_version": 1,
        "case_type": "layer_generate_case",
        "case_id": case_id,
        **case_record,
    }
    return {
        "schema_version": 1,
        "case_type": "learning_tiny_dataset_example",
        "example_id": example_id,
        "split": split,
        "source_case": {
            "case_type": "layer_generate_case",
            "case_id": case_id,
            "schema_version": 1,
        },
        "input": {"case_record": case_record},
        "targets": {"preferred_action": preferred_action},
    }


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )


def _ablation_fixture() -> list[dict]:
    return [
        _example(
            "train_accept_1",
            split="train",
            case_id="train_accept_1",
            preferred_action="accept",
            case_record={},
        ),
        _example(
            "train_accept_2",
            split="train",
            case_id="train_accept_2",
            preferred_action="accept",
            case_record={},
        ),
        _example(
            "train_style_drift",
            split="train",
            case_id="train_style_drift",
            preferred_action="adjust_prompt",
            case_record={
                "quality": {
                    "gate_passed": False,
                    "failures": ["style_drift"],
                }
            },
        ),
        _example(
            "train_provider_failure",
            split="train",
            case_id="train_provider_failure",
            preferred_action="fallback_to_agent",
            case_record={
                "decisions": {
                    "fallback_decisions": [
                        {
                            "reason": "provider rejected edit request",
                            "suggested_action": "fallback_to_agent",
                        }
                    ]
                }
            },
        ),
        _example(
            "test_style_drift",
            split="test",
            case_id="test_style_drift",
            preferred_action="adjust_prompt",
            case_record={
                "quality": {
                    "gate_passed": False,
                    "failures": ["style_drift"],
                }
            },
        ),
        _example(
            "test_provider_failure",
            split="test",
            case_id="test_provider_failure",
            preferred_action="fallback_to_agent",
            case_record={
                "decisions": {
                    "fallback_decisions": [
                        {
                            "reason": "provider rejected edit request",
                            "suggested_action": "fallback_to_agent",
                        }
                    ]
                }
            },
        ),
    ]


def test_tiny_feature_ablation_reports_dependency_on_strong_input_hints(tmp_path):
    from vulca.learning.tiny_feature_ablation import run_tiny_feature_ablation_report

    output = tmp_path / "ablation.json"
    report = run_tiny_feature_ablation_report(
        examples=_ablation_fixture(),
        output_path=output,
        eval_split="test",
        train_split="train",
    )

    variants = {item["variant_id"]: item for item in report["variant_reports"]}
    assert variants["full"]["policy_report"]["action_accuracy"] == 1.0
    assert variants["without_failure_hints"]["policy_report"]["action_accuracy"] == 0.5
    assert variants["without_action_hints"]["policy_report"]["action_accuracy"] == 0.5
    assert (
        variants["without_failure_and_action_hints"]["policy_report"][
            "action_accuracy"
        ]
        == 0.0
    )
    assert variants["full"]["fallback_reason_counts"] == {
        "failure_hint_prior": 1,
        "visible_action_hint": 1,
    }
    assert variants["without_failure_and_action_hints"]["accuracy_delta_vs_full"] == -1.0
    assert variants["without_failure_hints"]["removed_feature_groups"] == [
        "quality.failure_hints"
    ]
    assert json.loads(output.read_text(encoding="utf-8")) == report


def test_tiny_feature_ablation_cli_writes_report(tmp_path):
    dataset = tmp_path / "dataset.jsonl"
    output = tmp_path / "report.json"
    _write_jsonl(dataset, _ablation_fixture())

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/tiny_feature_ablation.py"),
            "--dataset",
            str(dataset),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["case_type"] == "learning_tiny_feature_ablation_report"
    assert "without_failure_and_action_hints action_accuracy: 0.0" in result.stdout
