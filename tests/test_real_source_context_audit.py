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


def _write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )


def _layer_case(
    case_id: str,
    *,
    source_brief_path: str | None,
    preferred_action: str,
    reviewer: str,
) -> dict:
    record = {
        "schema_version": 1,
        "case_type": "layer_generate_case",
        "case_id": case_id,
        "created_at": "2026-05-07T00:00:00Z",
        "inputs": {
            "user_intent": "Create a source-dependent composition.",
            "tradition": "",
            "style_constraints": {"mode": "audit_fixture"},
            "layer_plan": {
                "desired_layer_count": 3,
                "layers": [
                    {
                        "semantic_path": "background.ground",
                        "role": "background",
                        "required": True,
                        "z_index": 0,
                        "alpha_strategy": "opaque_full_canvas",
                    },
                    {
                        "semantic_path": "midground.subject",
                        "role": "midground",
                        "required": True,
                        "z_index": 20,
                        "alpha_strategy": "transparent_subject",
                    },
                    {
                        "semantic_path": "foreground.accent",
                        "role": "foreground",
                        "required": True,
                        "z_index": 40,
                        "alpha_strategy": "transparent_subject",
                    },
                ],
            },
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
                },
                {
                    "semantic_path": "midground.subject",
                    "asset_path": "assets/fixture/midground.png",
                    "status": "generated",
                },
                {
                    "semantic_path": "foreground.accent",
                    "asset_path": "assets/fixture/foreground.png",
                    "status": "generated",
                },
            ],
            "composite_path": "",
            "preview_path": "",
        },
        "quality": {"gate_passed": False},
        "review": {
            "human_accept": False,
            "failure_type": "",
            "preferred_action": preferred_action,
            "reviewer": reviewer,
            "reviewed_at": "2026-05-07T00:00:00Z",
        },
    }
    if source_brief_path:
        record["source_refs"] = {"source_brief_path": source_brief_path}
    return record


def _write_audit_fixture(tmp_path: Path) -> Path:
    source_dir = tmp_path / "sources"
    source_dir.mkdir()
    (source_dir / "train_tang.md").write_text(
        "client-only sentence: Tang court mural registry ambiguity.",
        encoding="utf-8",
    )
    (source_dir / "train_gongbi.md").write_text(
        "Gongbi Spring Festival prompt tuning source.",
        encoding="utf-8",
    )
    (source_dir / "user_tang.md").write_text(
        "Tang mural packet with registry ambiguity and unregistered source.",
        encoding="utf-8",
    )
    (source_dir / "user_gongbi.md").write_text(
        "Gongbi source packet for Spring Festival linework.",
        encoding="utf-8",
    )

    train_cases = tmp_path / "train_cases.jsonl"
    user_cases = tmp_path / "user_cases.jsonl"
    _write_jsonl(
        train_cases,
        [
            _layer_case(
                "train_tang",
                source_brief_path="sources/train_tang.md",
                preferred_action="manual_review",
                reviewer="fixture_train",
            ),
            _layer_case(
                "train_gongbi",
                source_brief_path="sources/train_gongbi.md",
                preferred_action="adjust_prompt",
                reviewer="fixture_train",
            ),
        ],
    )
    _write_jsonl(
        user_cases,
        [
            _layer_case(
                "user_tang_source_dependent",
                source_brief_path="sources/user_tang.md",
                preferred_action="manual_review",
                reviewer="fixture_user",
            ),
            _layer_case(
                "user_gongbi_source_dependent",
                source_brief_path="sources/user_gongbi.md",
                preferred_action="adjust_prompt",
                reviewer="fixture_user",
            ),
            _layer_case(
                "user_missing_source_context",
                source_brief_path=None,
                preferred_action="manual_review",
                reviewer="fixture_user",
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


def test_real_source_context_audit_ranks_user_cases_without_leaking_sources(tmp_path):
    from vulca.learning.real_source_context_audit import (
        run_real_source_context_audit_report,
    )

    manifest = _write_audit_fixture(tmp_path)

    report = run_real_source_context_audit_report(
        repo_root=tmp_path,
        case_source_manifest_path=manifest,
        output_dir=tmp_path / "audit",
        include_local_seeds=False,
    )

    assert report["case_type"] == "learning_real_source_context_audit_report"
    assert report["summary"] == {
        "dataset_example_count": 5,
        "real_user_case_count": 3,
        "source_context_available_count": 2,
        "source_context_unavailable_count": 1,
        "prediction_changed_with_source_context_count": 1,
        "source_context_feature_matched_count": 2,
        "review_candidate_count": 3,
    }
    by_case = {item["case_id"]: item for item in report["records"]}

    tang = by_case["user_tang_source_dependent"]
    assert tang["candidate_reason"] == "prediction_changed_with_source_context"
    assert tang["recommended_review_action"] == "human_review_source_dependency"
    assert tang["predictions"] == {
        "full_action": "manual_review",
        "without_auxiliary_signals_action": "adjust_prompt",
        "action_changed_with_source_context": True,
        "full_matches_target": True,
        "without_auxiliary_signals_matches_target": False,
    }
    assert {
        "source_tag:tang_mural",
        "source_tag:registry_ambiguity",
    } <= set(tang["source_context"]["tags"])

    gongbi = by_case["user_gongbi_source_dependent"]
    assert gongbi["candidate_reason"] == "source_context_used_no_action_change"
    assert gongbi["recommended_review_action"] == "verify_source_dependency_label"
    assert gongbi["predictions"]["action_changed_with_source_context"] is False

    missing = by_case["user_missing_source_context"]
    assert missing["candidate_reason"] == "needs_source_context"
    assert missing["recommended_review_action"] == "recover_source_context"
    assert missing["source_context"]["available"] is False

    encoded = json.dumps(report, sort_keys=True)
    assert str(tmp_path) not in encoded
    assert "private://local_path" not in encoded
    assert "client-only sentence" not in encoded


def test_real_source_context_audit_cli_writes_report(tmp_path):
    manifest = _write_audit_fixture(tmp_path)
    output_dir = tmp_path / "audit"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/real_source_context_audit.py"),
            "--repo-root",
            str(tmp_path),
            "--case-source-manifest",
            str(manifest),
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
        (output_dir / "real_source_context_audit_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert report["summary"]["review_candidate_count"] == 3
    assert "Real source-context audit:" in result.stdout
    assert "Review candidates: 3/3" in result.stdout
