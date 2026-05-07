from __future__ import annotations

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
SCRIPT = ROOT / "scripts" / "real_source_context_recovery_eval.py"


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )


def _case(case_id: str, *, source_ref: str, preferred_split: str = "") -> dict:
    record = {
        "schema_version": 1,
        "case_type": "layer_generate_case",
        "case_id": case_id,
        "created_at": "2026-05-07T00:00:00Z",
        "inputs": {
            "user_intent": "Create a Tang court mural poster from the attached source.",
            "tradition": "",
            "style_constraints": {"mode": "recovery_eval_fixture"},
            "layer_plan": {
                "desired_layer_count": 3,
                "layers": [
                    {
                        "semantic_path": "poster.ground",
                        "role": "background",
                        "z_index": 0,
                        "required": True,
                    }
                ],
            },
            "prompt_stack": {},
            "provider": "fixture",
            "model": "fixture",
        },
        "decisions": {
            "fallback_decisions": [
                {
                    "semantic_path": "prompt.tradition",
                    "suggested_action": "manual_review",
                    "reason": "source registry ambiguity",
                }
            ],
            "layer_count": {"planned": 3, "generated": 0},
        },
        "outputs": {
            "artifact_dir": "",
            "layer_manifest_path": "",
            "layers": [],
            "composite_path": "",
            "preview_path": "",
        },
        "quality": {"gate_passed": False, "failures": ["prompt_ambiguity"]},
        "review": {
            "human_accept": False,
            "failure_type": "prompt_ambiguity",
            "preferred_action": "manual_review",
            "reviewer": "recovery_eval_fixture",
            "reviewed_at": "2026-05-07T00:00:00Z",
        },
    }
    if source_ref.startswith("private://"):
        record["source_summary"] = {"source_path_hint": source_ref}
    else:
        record["source_refs"] = {"source_brief_path": source_ref}
    if preferred_split:
        record["_preferred_split"] = preferred_split
    return record


def _write_manifest(tmp_path: Path) -> tuple[Path, Path, Path]:
    source_dir = tmp_path / "repo_sources"
    source_dir.mkdir()
    (source_dir / "train_tang.md").write_text(
        "Tang court mural registry ambiguity and manual review signal.",
        encoding="utf-8",
    )
    artifact_root = tmp_path / "private_artifacts"
    private_dir = artifact_root / "case-B-winter-solstice-error3"
    private_dir.mkdir(parents=True)
    (private_dir / "brief.md").write_text(
        "client-only source text: Tang mural registry ambiguity.",
        encoding="utf-8",
    )

    train_cases = tmp_path / "train_cases.jsonl"
    user_cases = tmp_path / "user_cases.jsonl"
    _write_jsonl(
        train_cases,
        [_case("train_tang_registry", source_ref="repo_sources/train_tang.md")],
    )
    _write_jsonl(
        user_cases,
        [
            _case(
                "user_private_tang_registry",
                source_ref="private://local_path/fixture/case-B-winter-solstice-error3",
            )
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
                        "source_id": "fixture_train",
                        "kind": "synthetic_case_log",
                        "path": train_cases.name,
                        "privacy_scope": "project",
                        "curation_status": "synthetic_reviewed",
                        "preferred_split": "train",
                    },
                    {
                        "source_id": "fixture_user",
                        "kind": "user_case_log",
                        "path": user_cases.name,
                        "privacy_scope": "private",
                        "curation_status": "reviewed",
                        "preferred_split": "test",
                    },
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest, artifact_root, artifact_root


def test_real_source_context_recovery_eval_closes_private_artifact_dry_run_gap(
    tmp_path,
):
    from vulca.learning.real_source_context_recovery_eval import (
        run_real_source_context_recovery_eval,
    )

    manifest, artifact_root, image_root = _write_manifest(tmp_path)

    report = run_real_source_context_recovery_eval(
        repo_root=tmp_path,
        case_source_manifest_path=manifest,
        artifact_search_roots=[artifact_root],
        image_search_roots=[image_root],
        output_dir=tmp_path / "recovery_eval",
        report_path=tmp_path
        / "recovery_eval"
        / "real_source_context_recovery_eval_report.json",
        include_local_seeds=False,
    )

    assert report["case_type"] == "learning_real_source_context_recovery_eval_report"
    assert report["status"] == "recovered_source_context_improves_dry_run"
    assert report["recovery"]["summary"]["private_source_artifact_recovered_count"] == 1
    assert report["baseline"]["source_context_signal_count"] == 1
    assert report["recovered"]["source_context_signal_count"] == 2
    assert report["baseline"]["fallback_agent_count"] == 1
    assert report["recovered"]["fallback_agent_count"] == 0
    assert report["delta"] == {
        "source_context_signal_count": 1,
        "fallback_agent_count": -1,
        "fallback_agent_count_reduction": 1,
        "no_source_context_for_required_source": -1,
        "no_source_context_for_required_source_reduction": 1,
    }
    assert report["recovered_eval_cases"] == [
        {
            "case_id": "user_private_tang_registry",
            "case_type": "layer_generate_case",
            "example_id": report["recovered_eval_cases"][0]["example_id"],
            "removed_data_gap_tags": ["no_source_context_for_required_source"],
            "source_context": {
                "available": True,
                "signal_count": 1,
                "source": "auxiliary_signal",
            },
        }
    ]
    assert Path(tmp_path / "recovery_eval" / report["artifacts"]["report_path"]).exists()

    encoded = json.dumps(report, sort_keys=True)
    assert str(tmp_path) not in encoded
    assert "private://local_path" not in encoded
    assert "client-only source text" not in encoded


def test_real_source_context_recovery_eval_cli_writes_summary(tmp_path):
    manifest, artifact_root, image_root = _write_manifest(tmp_path)
    output_dir = tmp_path / "recovery_eval"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo-root",
            str(tmp_path),
            "--case-source-manifest",
            str(manifest),
            "--artifact-search-root",
            str(artifact_root),
            "--image-search-root",
            str(image_root),
            "--output-dir",
            str(output_dir),
            "--no-local-seeds",
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Real source-context recovery eval:" in result.stdout
    assert "Source context signals: 1 -> 2 (delta 1)" in result.stdout
    assert "Dry-run fallback_agent_count: 1 -> 0 (reduction 1)" in result.stdout
    assert "Recovered eval cases: 1" in result.stdout
    report = json.loads(
        (output_dir / "real_source_context_recovery_eval_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["delta"]["fallback_agent_count_reduction"] == 1


def test_real_source_context_recovery_eval_cli_supports_success_thresholds(tmp_path):
    manifest, artifact_root, image_root = _write_manifest(tmp_path)
    output_dir = tmp_path / "recovery_eval"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo-root",
            str(tmp_path),
            "--case-source-manifest",
            str(manifest),
            "--artifact-search-root",
            str(artifact_root),
            "--image-search-root",
            str(image_root),
            "--output-dir",
            str(output_dir),
            "--no-local-seeds",
            "--max-recovered-source-context-gaps",
            "0",
            "--min-fallback-agent-reduction",
            "1",
            "--min-recovered-eval-cases",
            "1",
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Thresholds: passed" in result.stdout


def test_real_source_context_recovery_eval_cli_fails_when_thresholds_miss(tmp_path):
    manifest, artifact_root, image_root = _write_manifest(tmp_path)
    output_dir = tmp_path / "recovery_eval"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--repo-root",
            str(tmp_path),
            "--case-source-manifest",
            str(manifest),
            "--artifact-search-root",
            str(artifact_root),
            "--image-search-root",
            str(image_root),
            "--output-dir",
            str(output_dir),
            "--no-local-seeds",
            "--max-recovered-source-context-gaps",
            "0",
            "--min-fallback-agent-reduction",
            "2",
        ],
        cwd=ROOT,
        env=CLI_ENV,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    assert result.returncode == 1
    assert "Thresholds: failed" in result.stderr
    assert "fallback_agent_count_reduction 1 < 2" in result.stderr
