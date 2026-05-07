import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
CLI_ENV = dict(
    os.environ,
    PYTHONPATH=str(ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
)


def _write_image(path: Path, *, size: tuple[int, int] = (8, 6)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color=(25, 80, 140)).save(path)


def _write_case_source(tmp_path: Path) -> Path:
    case_log = tmp_path / "real_user_cases.private.user_cases.jsonl"
    records = [
        {
            "schema_version": 1,
            "case_type": "redraw_case",
            "case_id": "recoverable_source",
            "source_image": "private://local_path/a/source.png",
            "review": {
                "reviewed_at": "2026-05-07T00:00:00Z",
                "human_accept": False,
                "failure_type": "missing_detail",
                "preferred_action": "adjust_instruction",
            },
        },
        {
            "schema_version": 1,
            "case_type": "layer_generate_case",
            "case_id": "missing_source",
            "source_image": "private://local_path/b/missing.png",
            "review": {
                "reviewed_at": "2026-05-07T00:00:00Z",
                "human_accept": False,
                "failure_type": "provider_failure",
                "preferred_action": "fallback_to_agent",
            },
        },
    ]
    case_log.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "real_user_case_source_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "case_type": "learning_tiny_case_source_manifest",
                "sources": [
                    {
                        "source_id": "real_user_cases_fixture",
                        "kind": "user_case_log",
                        "path": case_log.name,
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


def test_recover_private_asset_map_writes_local_map_and_safe_report(tmp_path):
    from vulca.learning.real_user_asset_map_recovery import (
        recover_real_user_private_asset_map,
    )

    manifest = _write_case_source(tmp_path)
    search_root = tmp_path / "assets"
    _write_image(search_root / "source.png")

    report = recover_real_user_private_asset_map(
        repo_root=tmp_path,
        case_source_manifest_path=manifest,
        search_roots=[search_root],
        output_dir=tmp_path / "recovery",
    )

    assert report["case_type"] == "learning_real_user_private_asset_recovery_report"
    assert report["summary"] == {
        "private_source_ref_count": 2,
        "recovered_count": 1,
        "ambiguous_count": 0,
        "unresolved_count": 1,
    }
    assert report["recovered"][0]["case_id"] == "recoverable_source"
    assert report["unresolved"][0]["case_id"] == "missing_source"

    report_path = tmp_path / "recovery" / "real_user_private_asset_recovery_report.json"
    asset_map_path = tmp_path / "recovery" / "real_user_recovered.private.asset_map.json"
    encoded_report = report_path.read_text(encoding="utf-8")
    assert str(tmp_path) not in encoded_report
    assert "private://local_path/a/source.png" not in encoded_report
    assert "source.png" in encoded_report

    asset_map = json.loads(asset_map_path.read_text(encoding="utf-8"))
    assert asset_map["case_type"] == "learning_private_asset_map"
    assert asset_map["entries"] == [
        {
            "private_ref": "private://local_path/a/source.png",
            "local_path": str(search_root / "source.png"),
        }
    ]


def test_recover_private_asset_map_does_not_auto_select_ambiguous_names(tmp_path):
    from vulca.learning.real_user_asset_map_recovery import (
        recover_real_user_private_asset_map,
    )

    manifest = _write_case_source(tmp_path)
    _write_image(tmp_path / "assets_a" / "source.png")
    _write_image(tmp_path / "assets_b" / "source.png")

    report = recover_real_user_private_asset_map(
        repo_root=tmp_path,
        case_source_manifest_path=manifest,
        search_roots=[tmp_path / "assets_a", tmp_path / "assets_b"],
        output_dir=tmp_path / "recovery",
    )

    assert report["summary"]["recovered_count"] == 0
    assert report["summary"]["ambiguous_count"] == 1
    assert report["ambiguous"][0]["case_id"] == "recoverable_source"

    asset_map = json.loads(
        (tmp_path / "recovery" / "real_user_recovered.private.asset_map.json").read_text(
            encoding="utf-8"
        )
    )
    assert asset_map["entries"] == []


def test_recover_private_asset_map_supports_explicit_filename_alias(tmp_path):
    from vulca.learning.real_user_asset_map_recovery import (
        recover_real_user_private_asset_map,
    )

    manifest = _write_case_source(tmp_path)
    search_root = tmp_path / "assets"
    _write_image(search_root / "source_asset.png")

    report = recover_real_user_private_asset_map(
        repo_root=tmp_path,
        case_source_manifest_path=manifest,
        search_roots=[search_root],
        output_dir=tmp_path / "recovery",
        filename_aliases={"source.png": "source_asset.png"},
    )

    assert report["summary"]["recovered_count"] == 1
    assert report["recovered"][0]["basename"] == "source.png"
    assert report["recovered"][0]["matched_basename"] == "source_asset.png"

    asset_map = json.loads(
        (tmp_path / "recovery" / "real_user_recovered.private.asset_map.json").read_text(
            encoding="utf-8"
        )
    )
    assert asset_map["entries"][0]["local_path"] == str(search_root / "source_asset.png")


def test_real_user_asset_map_recovery_cli_writes_outputs(tmp_path):
    manifest = _write_case_source(tmp_path)
    search_root = tmp_path / "assets"
    output_dir = tmp_path / "recovery"
    _write_image(search_root / "source.png")

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/real_user_asset_map_recovery.py"),
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
    assert "Recovered private source refs: 1/2" in result.stdout
    assert (output_dir / "real_user_private_asset_recovery_report.json").exists()
    assert (output_dir / "real_user_recovered.private.asset_map.json").exists()
