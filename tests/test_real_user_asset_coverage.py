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


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )


def _write_image(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (4, 3), (255, 0, 0)).save(path)


def _case(case_id: str, case_type: str, **extra) -> dict:
    return {
        "schema_version": 1,
        "case_type": case_type,
        "case_id": case_id,
        "created_at": "2026-05-07T00:00:00Z",
        "review": {
            "human_accept": False,
            "failure_type": "style_drift",
            "preferred_action": "adjust_prompt",
        },
        **extra,
    }


def test_real_user_asset_coverage_classifies_safe_source_image_states(tmp_path):
    from vulca.learning.private_asset_map import write_private_asset_map
    from vulca.learning.real_user_asset_coverage import run_real_user_asset_coverage_report

    repo_image = tmp_path / "repo_image.png"
    mapped_image = tmp_path / "mapped_private.png"
    _write_image(repo_image)
    _write_image(mapped_image)

    cases = tmp_path / "cases.jsonl"
    _write_jsonl(
        cases,
        [
            _case(
                "repo_ready",
                "redraw_case",
                source_image=str(repo_image),
            ),
            _case(
                "private_ready",
                "decompose_case",
                input={
                    "source_image": "private://local_path/private123/source.png",
                },
            ),
            _case(
                "private_missing_map",
                "decompose_case",
                input={
                    "source_image": "private://local_path/private456/source.png",
                },
            ),
            _case(
                "brief_hint_only",
                "layer_generate_case",
                source_summary={
                    "source_path_hint": "private://local_path/brief789/case-brief",
                },
            ),
            _case("no_source", "layer_generate_case"),
        ],
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "case_type": "learning_tiny_case_source_manifest",
                "sources": [
                    {
                        "source_id": "real_user_fixture",
                        "kind": "user_case_log",
                        "path": str(cases),
                        "privacy_scope": "private",
                        "curation_status": "reviewed",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    private_map = tmp_path / "fixture.private.asset_map.json"
    write_private_asset_map(
        private_map,
        source_id="fixture_private_map",
        entries={
            "private://local_path/private123/source.png": str(mapped_image),
        },
    )

    report = run_real_user_asset_coverage_report(
        repo_root=ROOT,
        case_source_manifest_path=manifest,
        private_asset_map_paths=(private_map,),
        output_path=tmp_path / "report.json",
    )

    assert report["summary"] == {
        "example_count": 5,
        "available_source_image_count": 2,
        "open_model_runnable_count": 2,
        "needs_private_asset_map_count": 1,
        "source_hint_only_count": 1,
        "missing_source_reference_count": 1,
        "invalid_image_count": 0,
    }
    by_case = {item["case_id"]: item for item in report["records"]}
    assert by_case["repo_ready"]["asset_status"] == "available"
    assert by_case["repo_ready"]["source_image"]["ref_kind"] == "absolute_path"
    assert by_case["private_ready"]["asset_status"] == "available"
    assert by_case["private_ready"]["source_image"]["ref_kind"] == "private_uri_mapped"
    assert by_case["private_missing_map"]["asset_status"] == "needs_private_asset_map"
    assert by_case["brief_hint_only"]["asset_status"] == "source_hint_only"
    assert by_case["no_source"]["asset_status"] == "missing_source_reference"

    encoded = json.dumps(report, sort_keys=True)
    assert str(tmp_path) not in encoded
    assert "private://local_path" not in encoded


def test_real_user_asset_coverage_cli_writes_report(tmp_path):
    image_path = tmp_path / "source.png"
    _write_image(image_path)
    cases = tmp_path / "cases.jsonl"
    _write_jsonl(
        cases,
        [_case("repo_ready", "redraw_case", source_image=str(image_path))],
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "case_type": "learning_tiny_case_source_manifest",
                "sources": [
                    {
                        "source_id": "real_user_fixture",
                        "kind": "user_case_log",
                        "path": str(cases),
                        "privacy_scope": "private",
                        "curation_status": "reviewed",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "coverage.json"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/real_user_asset_coverage.py"),
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
    assert output.exists()
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["summary"]["open_model_runnable_count"] == 1
    assert "Open-model runnable: 1/1" in result.stdout
