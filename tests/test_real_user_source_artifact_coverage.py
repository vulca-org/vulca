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


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )


def _case(case_id: str, case_type: str = "layer_generate_case", **extra) -> dict:
    return {
        "schema_version": 1,
        "case_type": case_type,
        "case_id": case_id,
        "created_at": "2026-05-07T00:00:00Z",
        "review": {
            "reviewed_at": "2026-05-07T00:00:00Z",
            "human_accept": False,
            "failure_type": "prompt_ambiguity",
            "preferred_action": "manual_review",
        },
        **extra,
    }


def _write_manifest(tmp_path: Path, records: list[dict]) -> Path:
    cases = tmp_path / "real_user_cases.private.user_cases.jsonl"
    _write_jsonl(cases, records)
    manifest = tmp_path / "real_user_case_source_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "case_type": "learning_tiny_case_source_manifest",
                "sources": [
                    {
                        "source_id": "real_user_fixture",
                        "kind": "user_case_log",
                        "path": cases.name,
                        "privacy_scope": "private",
                        "curation_status": "reviewed",
                    }
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest


def test_source_artifact_coverage_classifies_brief_artifact_states(tmp_path):
    from vulca.learning.private_asset_map import write_private_asset_map
    from vulca.learning.real_user_source_artifact_coverage import (
        run_real_user_source_artifact_coverage_report,
    )

    (tmp_path / "docs/brief.md").parent.mkdir(parents=True)
    (tmp_path / "docs/brief.md").write_text("brief", encoding="utf-8")
    (tmp_path / "docs/structured.json").write_text("{}", encoding="utf-8")
    private_dir = tmp_path / "private-source-artifacts/case-a"
    private_dir.mkdir(parents=True)
    (private_dir / "proposal.md").write_text("private brief", encoding="utf-8")

    records = [
        _case(
            "source_image_case",
            source_image="private://local_path/a/source.png",
        ),
        _case(
            "repo_brief_ready",
            source_refs={
                "source_brief_path": "docs/brief.md",
                "structured_brief_path": "docs/structured.json",
            },
            inputs={
                "prompt_stack": {
                    "plan_prompt_path": "docs/brief.md",
                    "layer_prompt_refs": ["docs/structured.json"],
                }
            },
        ),
        _case(
            "private_hint_ready",
            source_summary={
                "source_path_hint": "private://local_path/private123/case-a",
            },
        ),
        _case(
            "private_hint_unmapped",
            source_summary={
                "source_path_hint": "private://local_path/private456/case-b",
            },
        ),
        _case(
            "repo_path_missing",
            source_refs={"source_brief_path": "docs/missing.md"},
        ),
        _case("no_source_artifact"),
    ]
    manifest = _write_manifest(tmp_path, records)
    private_map = tmp_path / "source_artifacts.private.asset_map.json"
    write_private_asset_map(
        private_map,
        source_id="source_artifacts_fixture",
        entries={
            "private://local_path/private123/case-a": str(private_dir),
        },
    )

    report = run_real_user_source_artifact_coverage_report(
        repo_root=tmp_path,
        case_source_manifest_path=manifest,
        private_artifact_map_paths=(private_map,),
        output_path=tmp_path / "report.json",
    )

    assert report["case_type"] == "learning_real_user_source_artifact_coverage_report"
    assert report["summary"] == {
        "example_count": 6,
        "source_image_present_count": 1,
        "available_source_artifact_count": 2,
        "needs_private_artifact_map_count": 1,
        "missing_artifact_path_count": 1,
        "missing_source_artifact_count": 1,
        "source_context_available_count": 3,
    }
    by_case = {item["case_id"]: item for item in report["records"]}
    assert by_case["source_image_case"]["artifact_status"] == "source_image_present"
    assert by_case["repo_brief_ready"]["artifact_status"] == "available"
    assert by_case["repo_brief_ready"]["artifact_count"] == 4
    assert by_case["private_hint_ready"]["artifact_status"] == "available"
    assert by_case["private_hint_unmapped"]["artifact_status"] == (
        "needs_private_artifact_map"
    )
    assert by_case["repo_path_missing"]["artifact_status"] == "missing_artifact_path"
    assert by_case["no_source_artifact"]["artifact_status"] == "missing_source_artifact"

    encoded = json.dumps(report, sort_keys=True)
    assert str(tmp_path) not in encoded
    assert "private://local_path" not in encoded


def test_source_artifact_coverage_cli_writes_report(tmp_path):
    (tmp_path / "docs/brief.md").parent.mkdir(parents=True)
    (tmp_path / "docs/brief.md").write_text("brief", encoding="utf-8")
    manifest = _write_manifest(
        tmp_path,
        [
            _case(
                "repo_brief_ready",
                source_refs={"source_brief_path": "docs/brief.md"},
            )
        ],
    )
    output = tmp_path / "source_artifact_coverage.json"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/real_user_source_artifact_coverage.py"),
            "--repo-root",
            str(tmp_path),
            "--case-source-manifest",
            str(manifest),
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
    assert report["summary"]["available_source_artifact_count"] == 1
    assert "Source context available: 1/1" in result.stdout
