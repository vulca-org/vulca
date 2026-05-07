from __future__ import annotations

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
    Image.new("RGB", (12, 8), color=(30, 90, 150)).save(path)


def _case(case_id: str, *, source_ref: str, preferred_action: str) -> dict:
    record = {
        "schema_version": 1,
        "case_type": "layer_generate_case",
        "case_id": case_id,
        "created_at": "2026-05-07T00:00:00Z",
        "inputs": {
            "user_intent": "Create a source-dependent composition.",
            "tradition": "",
            "style_constraints": {"mode": "recovery_fixture"},
            "layer_plan": {"desired_layer_count": 3, "layers": []},
            "prompt_stack": {},
            "provider": "fixture",
            "model": "fixture",
        },
        "decisions": {
            "fallback_decisions": [],
            "layer_count": {"planned": 3, "generated": 3, "accepted": 0},
        },
        "outputs": {
            "artifact_dir": "",
            "layer_manifest_path": "assets/fixture/manifest.json",
            "layers": [
                {
                    "semantic_path": "background.ground",
                    "asset_path": "assets/fixture/background.png",
                    "status": "generated",
                }
            ],
            "composite_path": "",
            "preview_path": "",
        },
        "quality": {"gate_passed": False},
        "review": {
            "human_accept": False,
            "failure_type": "",
            "preferred_action": preferred_action,
            "reviewer": "recovery_fixture",
            "reviewed_at": "2026-05-07T00:00:00Z",
        },
    }
    if source_ref.endswith(".png"):
        record["source_image"] = source_ref
    else:
        record["source_summary"] = {"source_path_hint": source_ref}
    return record


def _write_manifest(tmp_path: Path) -> Path:
    train_source = tmp_path / "train_sources"
    train_source.mkdir()
    (train_source / "train_tang.md").write_text(
        "Tang court mural registry ambiguity.",
        encoding="utf-8",
    )
    _write_image(train_source / "train_source.png")
    train_cases = tmp_path / "train_cases.jsonl"
    user_cases = tmp_path / "user_cases.jsonl"
    _write_jsonl(
        train_cases,
        [
            {
                **_case(
                    "train_tang",
                    source_ref="train_sources/train_tang.md",
                    preferred_action="manual_review",
                ),
                "source_refs": {"source_brief_path": "train_sources/train_tang.md"},
            },
            _case(
                "train_source_image",
                source_ref="train_sources/train_source.png",
                preferred_action="manual_review",
            ),
        ],
    )
    _write_jsonl(
        user_cases,
        [
            _case(
                "user_private_artifact",
                source_ref="private://local_path/a/case-A-brief",
                preferred_action="manual_review",
            ),
            _case(
                "user_private_image",
                source_ref="private://local_path/b/source.png",
                preferred_action="manual_review",
            ),
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
    return manifest


def _write_search_roots(tmp_path: Path) -> tuple[Path, Path]:
    artifact_root = tmp_path / "artifact_root"
    source_dir = artifact_root / "case-A-brief"
    source_dir.mkdir(parents=True)
    (source_dir / "proposal.md").write_text(
        "client-only sentence: Tang mural registry ambiguity.",
        encoding="utf-8",
    )
    image_root = tmp_path / "image_root"
    _write_image(image_root / "source.png")
    return artifact_root, image_root


def test_real_source_context_recovery_audit_runs_recovery_then_audit(tmp_path):
    from vulca.learning.real_source_context_recovery_audit import (
        run_real_source_context_recovery_audit,
    )

    manifest = _write_manifest(tmp_path)
    artifact_root, image_root = _write_search_roots(tmp_path)

    report = run_real_source_context_recovery_audit(
        repo_root=tmp_path,
        case_source_manifest_path=manifest,
        artifact_search_roots=[artifact_root],
        image_search_roots=[image_root],
        output_dir=tmp_path / "recovery_audit",
        include_local_seeds=False,
    )

    assert report["case_type"] == "learning_real_source_context_recovery_audit_report"
    assert report["summary"] == {
        "private_source_artifact_ref_count": 1,
        "private_source_artifact_recovered_count": 1,
        "private_source_image_ref_count": 1,
        "private_source_image_recovered_count": 1,
        "real_user_case_count": 2,
        "source_context_available_count": 2,
        "source_context_unavailable_count": 0,
        "review_candidate_count": 2,
    }
    assert report["status"] == "source_context_ready_for_review"
    assert (
        report["audit"]["summary"]["source_context_available_count"]
        == report["summary"]["source_context_available_count"]
    )
    assert Path(
        tmp_path / "recovery_audit" / report["artifacts"]["report_path"]
    ).exists()

    encoded = json.dumps(report, sort_keys=True)
    assert str(tmp_path) not in encoded
    assert "private://local_path" not in encoded
    assert "client-only sentence" not in encoded


def test_real_source_context_recovery_audit_cli_writes_report(tmp_path):
    manifest = _write_manifest(tmp_path)
    artifact_root, image_root = _write_search_roots(tmp_path)
    output_dir = tmp_path / "recovery_audit"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/real_source_context_recovery_audit.py"),
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
        timeout=20,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    report = json.loads(
        (output_dir / "real_source_context_recovery_audit_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["summary"]["source_context_available_count"] == 2
    assert "Real source-context recovery audit:" in result.stdout
    assert "Source context available: 2/2" in result.stdout
