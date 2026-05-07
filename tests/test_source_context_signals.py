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


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


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


def test_source_context_signal_pack_writes_promoted_safe_auxiliary_signals(tmp_path):
    from vulca.learning.private_asset_map import write_private_asset_map
    from vulca.learning.source_context_signals import write_source_context_signal_pack
    from vulca.learning.tiny_action_model import extract_tiny_action_features
    from vulca.learning.tiny_dataset import build_tiny_dataset_examples

    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "brief.md").write_text(
        "Production poster brief with sponsor band, title hierarchy, and film festival context.",
        encoding="utf-8",
    )
    private_dir = tmp_path / "private_artifacts" / "case-b"
    private_dir.mkdir(parents=True)
    (private_dir / "proposal.md").write_text(
        "client-only sentence: Tang court mural mood with registry ambiguity.",
        encoding="utf-8",
    )
    image_path = tmp_path / "private_assets" / "source.png"
    image_path.parent.mkdir()
    Image.new("RGB", (16, 9), color=(20, 80, 160)).save(image_path)

    manifest = _write_manifest(
        tmp_path,
        [
            _case(
                "repo_brief_case",
                source_refs={"source_brief_path": "docs/brief.md"},
            ),
            _case(
                "private_artifact_case",
                source_summary={
                    "source_path_hint": "private://local_path/private123/case-b",
                },
            ),
            _case(
                "private_image_case",
                source_image="private://local_path/private456/source.png",
            ),
        ],
    )
    private_map = tmp_path / "source.private.asset_map.json"
    write_private_asset_map(
        private_map,
        source_id="fixture_private_context",
        entries={
            "private://local_path/private123/case-b": str(private_dir),
            "private://local_path/private456/source.png": str(image_path),
        },
    )
    output_path = tmp_path / "signals.promoted.jsonl"
    manifest_path = tmp_path / "signals.promotion_manifest.json"
    report_path = tmp_path / "signals.report.json"

    report = write_source_context_signal_pack(
        repo_root=tmp_path,
        case_source_manifest_path=manifest,
        private_asset_map_paths=(private_map,),
        output_path=output_path,
        manifest_path=manifest_path,
        report_path=report_path,
        include_local_seeds=False,
    )

    assert report["case_type"] == "learning_source_context_signal_report"
    assert report["summary"] == {
        "example_count": 3,
        "promoted_signal_count": 3,
        "skipped_count": 0,
    }
    records = _read_jsonl(output_path)
    assert len(records) == 3
    assert all(item["case_type"] == "learning_open_model_signal_record" for item in records)
    assert all(
        item["training_use"]["review_status"] == "reviewed_promoted"
        for item in records
    )
    tags_by_case = {
        item["source_case"]["case_id"]: set(item["signals"]["source_context_tags"])
        for item in records
    }
    assert "source_tag:film_festival" in tags_by_case["repo_brief_case"]
    assert "source_tag:tang_mural" in tags_by_case["private_artifact_case"]
    assert "source_image:present" in tags_by_case["private_image_case"]
    assert "source_image.aspect:landscape" in tags_by_case["private_image_case"]

    encoded = output_path.read_text(encoding="utf-8")
    encoded += report_path.read_text(encoding="utf-8")
    encoded += manifest_path.read_text(encoding="utf-8")
    assert str(tmp_path) not in encoded
    assert "private://local_path" not in encoded
    assert "client-only sentence" not in encoded

    examples = build_tiny_dataset_examples(
        repo_root=tmp_path,
        case_source_manifest_path=manifest,
        auxiliary_signal_manifest_path=manifest_path,
        include_local_seeds=False,
    )
    target = next(
        item for item in examples if item["source_case"]["case_id"] == "repo_brief_case"
    )
    features = extract_tiny_action_features(target)
    assert "aux_signal.model:source_context_static_v1" in features
    assert "aux_signal.source_context_tag:source_tag:film_festival" in features
    assert "aux_signal.source_artifact_kind:file" in features


def test_tiny_action_model_can_learn_from_source_context_tags():
    from vulca.learning.tiny_action_model import (
        TinyActionClassifier,
        extract_tiny_action_features,
    )

    def example(example_id, split, target_action, tags):
        return {
            "example_id": example_id,
            "split": split,
            "source_case": {
                "case_id": example_id,
                "case_type": "layer_generate_case",
            },
            "input": {
                "case_record": {
                    "case_type": "layer_generate_case",
                    "quality": {"gate_passed": False},
                },
                "auxiliary_signals": [
                    {
                        "signal_id": f"source_signal_{example_id}",
                        "model": {"id": "source_context_static_v1"},
                        "signals": {
                            "status": "completed",
                            "signal_source": "source_context_static",
                            "source_context_tags": tags,
                            "source_artifacts": {
                                "artifact_kind_counts": {"directory": 1},
                            },
                        },
                        "training_use": {
                            "approved_for_auxiliary_training": True,
                            "review_status": "reviewed_promoted",
                        },
                    }
                ],
            },
            "targets": {"preferred_action": target_action},
        }

    train = example(
        "train_tang_registry",
        "train",
        "manual_review",
        ["source_tag:tang_mural", "source_tag:registry_ambiguity"],
    )
    distractor = example(
        "train_gongbi",
        "train",
        "adjust_prompt",
        ["source_tag:gongbi", "source_tag:spring_festival"],
    )
    test = example(
        "test_tang_registry",
        "test",
        "manual_review",
        ["source_tag:tang_mural", "source_tag:registry_ambiguity"],
    )

    features = extract_tiny_action_features(test)
    assert "aux_signal.source_context_tag:source_tag:tang_mural" in features
    assert "aux_signal.source_artifact_kind:directory" in features
    prediction = TinyActionClassifier.fit([train, distractor]).predict(test)

    assert prediction["recommended_action"] == "manual_review"
    assert "aux_signal.source_context_tag:source_tag:tang_mural" in prediction[
        "explanation"
    ]["matched_features"]


def test_source_context_signal_cli_writes_outputs(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "brief.md").write_text("Film festival poster brief.", encoding="utf-8")
    manifest = _write_manifest(
        tmp_path,
        [
            _case(
                "repo_brief_case",
                source_refs={"source_brief_path": "docs/brief.md"},
            )
        ],
    )
    output_path = tmp_path / "signals.promoted.jsonl"
    manifest_path = tmp_path / "signals.promotion_manifest.json"
    report_path = tmp_path / "signals.report.json"

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/source_context_signals.py"),
            "--repo-root",
            str(tmp_path),
            "--case-source-manifest",
            str(manifest),
            "--output",
            str(output_path),
            "--manifest",
            str(manifest_path),
            "--report",
            str(report_path),
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
    assert "Source context signals: 1/1" in result.stdout
    assert output_path.exists()
    assert manifest_path.exists()
    assert json.loads(report_path.read_text(encoding="utf-8"))["summary"][
        "promoted_signal_count"
    ] == 1
