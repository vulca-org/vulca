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


def _case(case_id: str, **extra) -> dict:
    return {
        "schema_version": 1,
        "case_type": "layer_generate_case",
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


def test_recover_private_source_artifact_map_writes_local_map_and_safe_report(tmp_path):
    from vulca.learning.real_user_source_artifact_map_recovery import (
        recover_real_user_private_source_artifact_map,
    )

    manifest = _write_manifest(
        tmp_path,
        [
            _case(
                "recoverable_brief",
                source_summary={
                    "source_path_hint": "private://local_path/a/case-A-brief",
                },
            ),
            _case(
                "missing_brief",
                source_summary={
                    "source_path_hint": "private://local_path/b/case-B-brief",
                },
            ),
            _case(
                "ambiguous_brief",
                source_summary={
                    "source_path_hint": "private://local_path/c/case-C-brief",
                },
            ),
        ],
    )
    search_root = tmp_path / "artifacts"
    (search_root / "case-A-brief").mkdir(parents=True)
    (search_root / "case-A-brief" / "proposal.md").write_text(
        "brief",
        encoding="utf-8",
    )
    (tmp_path / "alt_a" / "case-C-brief").mkdir(parents=True)
    (tmp_path / "alt_b" / "case-C-brief").mkdir(parents=True)

    report = recover_real_user_private_source_artifact_map(
        repo_root=tmp_path,
        case_source_manifest_path=manifest,
        search_roots=[search_root, tmp_path / "alt_a", tmp_path / "alt_b"],
        output_dir=tmp_path / "recovery",
    )

    assert report["case_type"] == (
        "learning_real_user_private_source_artifact_recovery_report"
    )
    assert report["summary"] == {
        "private_source_artifact_ref_count": 3,
        "recovered_count": 1,
        "ambiguous_count": 1,
        "unresolved_count": 1,
    }
    assert report["recovered"][0]["case_id"] == "recoverable_brief"
    assert report["recovered"][0]["basename"] == "case-A-brief"
    assert report["ambiguous"][0]["case_id"] == "ambiguous_brief"
    assert report["unresolved"][0]["case_id"] == "missing_brief"

    encoded_report = json.dumps(report, sort_keys=True)
    assert str(tmp_path) not in encoded_report
    assert "private://local_path" not in encoded_report

    asset_map = json.loads(
        (tmp_path / "recovery" / "real_user_source_artifacts.private.asset_map.json")
        .read_text(encoding="utf-8")
    )
    assert asset_map["case_type"] == "learning_private_asset_map"
    assert asset_map["entries"] == [
        {
            "private_ref": "private://local_path/a/case-A-brief",
            "local_path": str(search_root / "case-A-brief"),
        }
    ]


def test_recover_private_source_artifact_map_supports_explicit_filename_alias(tmp_path):
    from vulca.learning.real_user_source_artifact_map_recovery import (
        recover_real_user_private_source_artifact_map,
    )

    manifest = _write_manifest(
        tmp_path,
        [
            _case(
                "aliased_brief",
                source_summary={
                    "source_path_hint": "private://local_path/a/case-A-brief",
                },
            )
        ],
    )
    search_root = tmp_path / "artifacts"
    (search_root / "spring_case").mkdir(parents=True)
    (search_root / "spring_case" / "proposal.md").write_text(
        "brief",
        encoding="utf-8",
    )

    report = recover_real_user_private_source_artifact_map(
        repo_root=tmp_path,
        case_source_manifest_path=manifest,
        search_roots=[search_root],
        filename_aliases={"case-A-brief": "spring_case"},
        output_dir=tmp_path / "recovery",
    )

    assert report["summary"]["recovered_count"] == 1
    assert report["recovered"][0]["matched_basename"] == "spring_case"


def test_recover_private_source_artifact_map_cli_writes_outputs(tmp_path):
    manifest = _write_manifest(
        tmp_path,
        [
            _case(
                "recoverable_brief",
                source_summary={
                    "source_path_hint": "private://local_path/a/case-A-brief",
                },
            )
        ],
    )
    search_root = tmp_path / "artifacts"
    output_dir = tmp_path / "recovery"
    (search_root / "case-A-brief").mkdir(parents=True)

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/real_user_source_artifact_map_recovery.py"),
            "--repo-root",
            str(tmp_path),
            "--case-source-manifest",
            str(manifest),
            "--search-root",
            str(search_root),
            "--output-dir",
            str(output_dir),
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Recovered private source artifact refs: 1/1" in result.stdout
    assert (
        output_dir / "real_user_source_artifact_recovery_report.json"
    ).exists()
    assert (
        output_dir / "real_user_source_artifacts.private.asset_map.json"
    ).exists()
