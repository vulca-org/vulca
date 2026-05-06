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


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _reviewed_redraw_case() -> dict:
    return {
        "schema_version": 1,
        "case_type": "redraw_case",
        "case_id": "redraw_user_001",
        "created_at": "2026-05-05T15:00:00Z",
        "source_image": "/Users/alice/private-client/source.png",
        "instruction": (
            "Redraw the sign edge using alice@example.com reference "
            "from /Users/alice/private-client/ref.png; call +1 415 555 0134."
        ),
        "observables": {
            "alpha_edge_delta": 0.42,
            "texture_mismatch_score": 0.78,
        },
        "artifacts": {
            "source_layer_path": "/Users/alice/private-client/layers/sign.png",
            "redrawn_layer_path": "/Users/alice/private-client/out/sign_redraw.png",
        },
        "review": {
            "human_accept": False,
            "failure_type": "texture_leak",
            "preferred_action": "adjust_instruction",
            "reviewer": "alice@example.com",
            "reviewed_at": "2026-05-05T16:00:00Z",
            "notes": "Observable texture leak; private notes at /Users/alice/private-client/notes.txt.",
        },
    }


def test_user_case_intake_writes_private_manifest_and_sanitized_log(tmp_path):
    from vulca.learning.tiny_dataset import write_tiny_dataset
    from vulca.learning.user_case_intake import write_user_case_intake

    input_path = tmp_path / "reviewed_user_cases.jsonl"
    _write_jsonl(input_path, [_reviewed_redraw_case()])

    result = write_user_case_intake(
        input_path=input_path,
        output_dir=tmp_path / "intake",
        source_id="user_session_2026_05",
    )

    assert result.source_id == "user_session_2026_05"
    assert result.record_count == 1
    manifest = json.loads(Path(result.manifest_path).read_text(encoding="utf-8"))
    assert manifest == {
        "schema_version": 1,
        "case_type": "learning_tiny_case_source_manifest",
        "sources": [
            {
                "source_id": "user_session_2026_05",
                "kind": "user_case_log",
                "path": "user_session_2026_05.private.user_cases.jsonl",
                "privacy_scope": "private",
                "curation_status": "reviewed",
            }
        ],
    }

    records = _read_jsonl(Path(result.output_path))
    assert records[0]["case_id"] == "redraw_user_001"
    assert records[0]["review"]["human_accept"] is False
    assert records[0]["review"]["failure_type"] == "texture_leak"
    assert records[0]["review"]["preferred_action"] == "adjust_instruction"
    assert records[0]["observables"] == {
        "alpha_edge_delta": 0.42,
        "texture_mismatch_score": 0.78,
    }
    assert records[0]["user_case_intake"] == {
        "schema_version": 1,
        "source_id": "user_session_2026_05",
        "privacy_scope": "private",
        "curation_status": "reviewed",
        "record_index": 0,
    }

    serialized = json.dumps(records[0], sort_keys=True)
    assert "/Users/alice" not in serialized
    assert "alice@example.com" not in serialized
    assert "415 555 0134" not in serialized
    assert "private://local_path/" in serialized
    assert "<email:redacted>" in serialized
    assert "<phone:redacted>" in serialized

    dataset_path = tmp_path / "tiny_dataset.jsonl"
    dataset_result = write_tiny_dataset(
        repo_root=ROOT,
        output_path=dataset_path,
        include_local_seeds=False,
        case_source_manifest_path=result.manifest_path,
    )
    assert dataset_result.example_count == 1
    example = _read_jsonl(dataset_path)[0]
    assert example["source"]["source_id"] == "user_session_2026_05"
    assert example["source"]["privacy_scope"] == "private"
    assert example["source"]["curation_status"] == "reviewed"
    assert example["source_case"]["case_id"] == "redraw_user_001"


def test_user_case_intake_rejects_unreviewed_cases(tmp_path):
    from vulca.learning.user_case_intake import write_user_case_intake

    unreviewed = _reviewed_redraw_case()
    unreviewed["review"] = {"human_accept": False}
    input_path = tmp_path / "unreviewed.jsonl"
    _write_jsonl(input_path, [unreviewed])

    with pytest.raises(ValueError, match="reviewed_at is required"):
        write_user_case_intake(
            input_path=input_path,
            output_dir=tmp_path / "intake",
            source_id="user_session_2026_05",
        )


def test_cases_intake_user_cli_writes_manifest_and_private_log(tmp_path):
    input_path = tmp_path / "reviewed_user_cases.jsonl"
    output_dir = tmp_path / "intake"
    _write_jsonl(input_path, [_reviewed_redraw_case()])

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "vulca.cli",
            "cases",
            "intake-user",
            str(input_path),
            "--source-id",
            "cli_user_session",
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        timeout=10,
        env=CLI_ENV,
    )

    assert result.returncode == 0, result.stderr
    assert "User case log:" in result.stdout
    assert "Case source manifest:" in result.stdout
    manifest_path = output_dir / "cli_user_session.case_source_manifest.json"
    log_path = output_dir / "cli_user_session.private.user_cases.jsonl"
    assert manifest_path.exists()
    assert log_path.exists()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["sources"][0]["source_id"] == "cli_user_session"
    assert manifest["sources"][0]["kind"] == "user_case_log"
    assert manifest["sources"][0]["privacy_scope"] == "private"
    assert manifest["sources"][0]["curation_status"] == "reviewed"
