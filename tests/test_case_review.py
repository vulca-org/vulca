import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
CLI_ENV = dict(
    os.environ,
    PYTHONPATH=str(ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
)


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )


def test_review_case_log_updates_target_case_without_dropping_fields(tmp_path):
    from vulca.learning.case_review import load_cases, review_case_log

    input_path = tmp_path / "cases.jsonl"
    output_path = tmp_path / "reviewed.jsonl"
    original_target = {
        "schema_version": 1,
        "case_type": "redraw_case",
        "case_id": "redraw_a",
        "provider": "openai",
        "nested": {"keep": True},
        "review": {"human_accept": None, "failure_type": "", "preferred_action": ""},
    }
    untouched = {
        "schema_version": 1,
        "case_type": "redraw_case",
        "case_id": "redraw_b",
        "provider": "nb2",
        "review": {"human_accept": None},
    }
    _write_jsonl(input_path, [original_target, untouched])

    result = review_case_log(
        input_path,
        case_id="redraw_a",
        output_path=output_path,
        human_accept=False,
        failure_type="mask_too_broad",
        preferred_action="adjust_mask",
        reviewer="alice",
        reviewed_at="2026-05-05T12:34:56Z",
        notes="mask included broad hedge texture",
    )

    reread = load_cases(output_path)
    assert result.updated is True
    assert result.case_id == "redraw_a"
    assert result.output_path == str(output_path)
    assert len(reread) == 2
    assert reread[0]["case_id"] == "redraw_a"
    assert reread[0]["provider"] == "openai"
    assert reread[0]["nested"] == {"keep": True}
    assert reread[0]["review"] == {
        "human_accept": False,
        "failure_type": "mask_too_broad",
        "preferred_action": "adjust_mask",
        "reviewer": "alice",
        "reviewed_at": "2026-05-05T12:34:56Z",
        "notes": "mask included broad hedge texture",
    }
    assert reread[1] == untouched


def test_review_case_log_rejects_invalid_labels(tmp_path):
    from vulca.learning.case_review import review_case_log

    input_path = tmp_path / "cases.jsonl"
    _write_jsonl(
        input_path,
        [
            {
                "schema_version": 1,
                "case_type": "redraw_case",
                "case_id": "redraw_a",
                "review": {},
            }
        ],
    )

    with pytest.raises(ValueError, match="unsupported redraw failure_type"):
        review_case_log(
            input_path,
            case_id="redraw_a",
            failure_type="not_a_taxonomy_label",
        )

    with pytest.raises(ValueError, match="unsupported redraw preferred_action"):
        review_case_log(
            input_path,
            case_id="redraw_a",
            preferred_action="not_an_action",
        )


def test_review_case_log_can_append_review_sidecar(tmp_path):
    from vulca.learning.case_review import review_case_log

    input_path = tmp_path / "cases.jsonl"
    output_path = tmp_path / "reviewed.jsonl"
    sidecar_path = tmp_path / "reviews.jsonl"
    _write_jsonl(
        input_path,
        [
            {
                "schema_version": 1,
                "case_type": "redraw_case",
                "case_id": "redraw_a",
                "review": {},
            }
        ],
    )

    result = review_case_log(
        input_path,
        case_id="redraw_a",
        output_path=output_path,
        sidecar_output_path=sidecar_path,
        human_accept=True,
        failure_type="",
        preferred_action="accept",
        reviewed_at="2026-05-05T12:40:00Z",
    )

    sidecar = [json.loads(line) for line in sidecar_path.read_text().splitlines()]
    assert result.sidecar_path == str(sidecar_path)
    assert sidecar == [
        {
            "case_id": "redraw_a",
            "case_type": "redraw_case",
            "review": {
                "failure_type": "",
                "human_accept": True,
                "preferred_action": "accept",
                "reviewed_at": "2026-05-05T12:40:00Z",
            },
        }
    ]


def test_review_case_log_errors_when_case_id_missing(tmp_path):
    from vulca.learning.case_review import review_case_log

    input_path = tmp_path / "cases.jsonl"
    _write_jsonl(
        input_path,
        [{"schema_version": 1, "case_type": "redraw_case", "case_id": "redraw_a"}],
    )

    with pytest.raises(ValueError, match="case_id 'missing' not found"):
        review_case_log(input_path, case_id="missing")


def test_cases_review_cli_writes_reviewed_jsonl(tmp_path):
    input_path = tmp_path / "cases.jsonl"
    output_path = tmp_path / "reviewed.jsonl"
    _write_jsonl(
        input_path,
        [
            {
                "schema_version": 1,
                "case_type": "redraw_case",
                "case_id": "redraw_cli",
                "review": {},
            }
        ],
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "vulca.cli",
            "cases",
            "review",
            str(input_path),
            "--case-id",
            "redraw_cli",
            "--human-accept",
            "true",
            "--failure-type",
            "texture_leak",
            "--preferred-action",
            "adjust_instruction",
            "--reviewer",
            "bob",
            "--reviewed-at",
            "2026-05-05T13:00:00Z",
            "--notes",
            "localized but wrong texture",
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        timeout=10,
        env=CLI_ENV,
    )

    assert result.returncode == 0, result.stderr
    assert "redraw_cli" in result.stdout
    reviewed = [json.loads(line) for line in output_path.read_text().splitlines()]
    assert reviewed[0]["review"]["human_accept"] is True
    assert reviewed[0]["review"]["failure_type"] == "texture_leak"
    assert reviewed[0]["review"]["preferred_action"] == "adjust_instruction"
