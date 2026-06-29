from __future__ import annotations

import json
from pathlib import Path

import pytest


def write_case(root: Path, *, case_id: str = "makio-meshline") -> Path:
    case_dir = root / case_id
    case_dir.mkdir(parents=True)
    (case_dir / "metadata.json").write_text(
        json.dumps(
            {
                "id": case_id,
                "title": "Makio MeshLine",
                "canonical_url": "https://meshline.makio.io/",
                "source_type": "demo",
                "year": 2025,
                "author_or_studio": "Makio64",
                "currentness": "still_current",
                "summary": "Modern Three.js wide-line rendering reference.",
                "why_relevant": "Core reference for 3D route and trail primitives.",
                "review_status": "candidate",
                "quality_scores": {
                    "aesthetic_relevance": 3,
                    "technical_learnability": 3,
                    "multimodal_completeness": 1,
                    "interaction_clarity": 2,
                    "vulca_transfer_value": 3,
                    "license_safety": 2,
                },
                "visual_families": ["meshline", "data_tunnel"],
                "modules": [
                    {
                        "module_type": "meshline",
                        "payload": {
                            "path_source": "curve_points",
                            "line_form": "thick_ribbon",
                            "material": ["gradient", "dash"],
                            "animation": ["trail_reveal"],
                            "spatial_role": "route",
                            "learning_primitive": "animated 3D route line",
                        },
                        "evidence_refs": [],
                        "confidence": "medium",
                        "review_status": "partial",
                        "review_notes": "Seeded from public project page.",
                    }
                ],
                "captures": [
                    {
                        "id": "metadata-source",
                        "evidence_type": "external_doc",
                        "path_or_url": "https://meshline.makio.io/",
                        "capture_method": "source_read",
                        "viewport": "none",
                        "interaction": "none",
                        "captured_at": "2026-06-29",
                        "source_url": "https://meshline.makio.io/",
                        "confidence": "high",
                        "rights_status": "source_link_only",
                        "notes": "Metadata seed only.",
                    }
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (case_dir / "anatomy.md").write_text(
        "# Anatomy\n\nPrimitive: animated 3D route line.\n", encoding="utf-8"
    )
    (case_dir / "lesson.md").write_text(
        "# Lesson\n\nMinimal rebuild: 12 nodes connected by animated thick lines.\n",
        encoding="utf-8",
    )
    (case_dir / "vulca_translation.md").write_text(
        "# VULCA Translation\n\nMaps to source trail and route decision.\n",
        encoding="utf-8",
    )
    return case_dir


def test_validate_case_folder_accepts_complete_seed(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    record = validate_case_folder(write_case(tmp_path))

    assert record.id == "makio-meshline"
    assert record.quality_score_total == 14
    assert record.metadata["visual_families"] == ["meshline", "data_tunnel"]
    assert record.coverage["metadata"] == "complete"
    assert record.coverage["lesson"] == "complete"


def test_validate_case_folder_rejects_unknown_module(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["modules"][0]["module_type"] = "retro_plotter"
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="unknown module_type"):
        validate_case_folder(case_dir)


def test_validate_case_folder_rejects_missing_core_field(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    del payload["canonical_url"]
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required metadata fields"):
        validate_case_folder(case_dir)


def test_case_to_review_dict_redacts_secret_like_values(tmp_path: Path):
    from vulca.vector_aesthetics.schema import case_to_review_dict, validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["summary"] = "accidental keys sk-proj-abc123 github_pat_abcdef1234567890 token=abcdef1234567890"
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    review = case_to_review_dict(validate_case_folder(case_dir))

    assert "sk-proj" not in json.dumps(review)
    assert "github_pat_" not in json.dumps(review)
    assert "abcdef1234567890" not in json.dumps(review)
    assert "[redacted]" in json.dumps(review)


def test_validate_case_folder_rejects_non_https_url(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["canonical_url"] = "http://meshline.makio.io/"
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="canonical_url must start with https://"):
        validate_case_folder(case_dir)


def test_validate_case_folder_rejects_out_of_range_score(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["quality_scores"]["aesthetic_relevance"] = 4
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="quality score aesthetic_relevance"):
        validate_case_folder(case_dir)


def test_capture_failure_counts_as_partial_not_complete(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["captures"].append(
        {
            "id": "video-capture-failure",
            "evidence_type": "video",
            "path_or_url": "https://meshline.makio.io/",
            "capture_method": "manual_browser",
            "viewport": "none",
            "interaction": "capture_failed",
            "captured_at": "2026-06-29",
            "source_url": "https://meshline.makio.io/",
            "confidence": "medium",
            "rights_status": "source_link_only",
            "notes": "Autoplay blocked in automated capture.",
        }
    )
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    record = validate_case_folder(case_dir)

    assert record.coverage["video"] == "partial"


def test_validate_case_folder_rejects_missing_local_capture_file(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["captures"].append(
        {
            "id": "desktop-idle",
            "evidence_type": "screenshot",
            "path_or_url": "screenshots/missing.png",
            "capture_method": "manual_browser",
            "viewport": "1440x900",
            "interaction": "idle",
            "captured_at": "2026-06-29",
            "source_url": "https://meshline.makio.io/",
            "confidence": "medium",
            "rights_status": "local_capture",
            "notes": "This local file should be present before validation succeeds.",
        }
    )
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="screenshots/missing.png"):
        validate_case_folder(case_dir)
