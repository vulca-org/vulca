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
                        "id": "screenshot-capture-failure",
                        "evidence_type": "screenshot",
                        "path_or_url": "https://meshline.makio.io/",
                        "capture_method": "manual_browser",
                        "viewport": "1440x900",
                        "interaction": "capture_failed",
                        "captured_at": "2026-06-29",
                        "source_url": "https://meshline.makio.io/",
                        "confidence": "medium",
                        "rights_status": "source_link_only",
                        "notes": "Screenshot capture failed because the page was still rendering.",
                    },
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
                        "notes": "Video capture failed because autoplay and timing blocked automation.",
                    },
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
        "# Anatomy\n\nPrimitive: animated 3D route line.\nTechnique: layered sweep motion.\n",
        encoding="utf-8",
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
    assert record.coverage["screenshots"] == "partial"
    assert record.coverage["video"] == "partial"


def test_validate_case_folder_rejects_unknown_module(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["modules"][0]["module_type"] = "retro_plotter"
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="unknown module_type"):
        validate_case_folder(case_dir)


def test_validate_case_folder_rejects_id_that_does_not_match_folder(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["id"] = "different-id"
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="metadata id must match case folder name"):
        validate_case_folder(case_dir)


def test_validate_case_folder_rejects_missing_screenshot_and_video_coverage(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["captures"] = [
        capture
        for capture in payload["captures"]
        if capture["evidence_type"] not in {"screenshot", "video"}
    ]
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="case folder must include screenshot and video coverage"):
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


def test_validate_case_folder_rejects_empty_modules(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["modules"] = []
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="at least one module"):
        validate_case_folder(case_dir)


@pytest.mark.parametrize(
    ("anatomy_text", "match"),
    [
        ("# Anatomy\n\nTechnique: layered sweep motion.\n", "Primitive: and Technique:"),
        ("# Anatomy\n\nPrimitive: animated 3D route line.\n", "Primitive: and Technique:"),
    ],
)
def test_validate_case_folder_rejects_incomplete_anatomy(tmp_path: Path, anatomy_text: str, match: str):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    (case_dir / "anatomy.md").write_text(anatomy_text, encoding="utf-8")

    with pytest.raises(ValueError, match=match):
        validate_case_folder(case_dir)


def test_validate_case_folder_rejects_lesson_without_minimal_rebuild(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    (case_dir / "lesson.md").write_text(
        "# Lesson\n\nBuild notes only. No exercise provided.\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="minimal_rebuild_exercise or Minimal rebuild"):
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


@pytest.mark.parametrize(
    ("path_or_url", "expected_exception", "match"),
    [
        ("../outside.png", ValueError, "escapes case_dir"),
        ("/tmp/outside.png", ValueError, "relative to case_dir"),
        ("screenshots", FileNotFoundError, "screenshots"),
    ],
)
def test_validate_case_folder_rejects_invalid_local_capture_paths(
    tmp_path: Path,
    path_or_url: str,
    expected_exception: type[Exception],
    match: str,
):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    if path_or_url == "screenshots":
        (case_dir / "screenshots").mkdir(parents=True)
    payload["captures"].append(
        {
            "id": f"local-{path_or_url.replace('/', '-')}",
            "evidence_type": "screenshot",
            "path_or_url": path_or_url,
            "capture_method": "manual_browser",
            "viewport": "1440x900",
            "interaction": "idle",
            "captured_at": "2026-06-29",
            "source_url": "https://meshline.makio.io/",
            "confidence": "medium",
            "rights_status": "local_capture",
            "notes": "Regression coverage for local capture path validation.",
        }
    )
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(expected_exception, match=match):
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


def test_source_link_only_capture_without_failure_does_not_satisfy_coverage(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["captures"] = [
        {
            "id": "screenshot-source-link-only",
            "evidence_type": "screenshot",
            "path_or_url": "https://meshline.makio.io/",
            "capture_method": "manual_browser",
            "viewport": "1440x900",
            "interaction": "none",
            "captured_at": "2026-06-29",
            "source_url": "https://meshline.makio.io/",
            "confidence": "medium",
            "rights_status": "source_link_only",
            "notes": "Reference link only.",
        },
        {
            "id": "video-source-link-only",
            "evidence_type": "video",
            "path_or_url": "https://meshline.makio.io/",
            "capture_method": "manual_browser",
            "viewport": "none",
            "interaction": "none",
            "captured_at": "2026-06-29",
            "source_url": "https://meshline.makio.io/",
            "confidence": "medium",
            "rights_status": "source_link_only",
            "notes": "Reference link only.",
        },
    ]
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="case folder must include screenshot and video coverage"):
        validate_case_folder(case_dir)


def test_capture_failure_requires_explanatory_notes(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["captures"][0]["notes"] = "  "
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="capture_failed must include non-empty notes"):
        validate_case_folder(case_dir)


def test_local_screenshot_capture_takes_precedence_over_failure_record(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    screenshot_path = case_dir / "screenshots" / "desktop-idle.png"
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    screenshot_path.write_bytes(b"not a real png, just a fixture file")

    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["captures"].append(
        {
            "id": "desktop-idle",
            "evidence_type": "screenshot",
            "path_or_url": "screenshots/desktop-idle.png",
            "capture_method": "manual_browser",
            "viewport": "1440x900",
            "interaction": "idle",
            "captured_at": "2026-06-29",
            "source_url": "https://meshline.makio.io/",
            "confidence": "medium",
            "rights_status": "local_capture",
            "notes": "Local screenshot captured from the case folder.",
        }
    )
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    record = validate_case_folder(case_dir)

    assert record.coverage["screenshots"] == "complete"


def test_asset_manifest_coverage_comes_from_evidence_not_module_presence(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["modules"].append(
        {
            "module_type": "asset_pipeline",
            "payload": {
                "learning_primitive": "asset manifest authoring",
            },
            "evidence_refs": [],
            "confidence": "medium",
            "review_status": "partial",
            "review_notes": "Pipeline exists, but no manifest evidence yet.",
        }
    )
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    record = validate_case_folder(case_dir)

    assert record.coverage["asset_manifest"] == "missing"

    manifest_path = case_dir / "assets" / "asset_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text("{\n  \"assets\": []\n}\n", encoding="utf-8")

    record = validate_case_folder(case_dir)

    assert record.coverage["asset_manifest"] == "partial"


def test_seed_stub_content_downgrades_learning_coverage(tmp_path: Path):
    from vulca.vector_aesthetics.schema import case_to_review_dict, validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["modules"][0]["payload"] = {
        "learning_primitive": "meshline learning primitive",
        "seed_status": "metadata_only",
    }
    payload["modules"][0]["confidence"] = "low"
    payload["modules"][0]["review_notes"] = "Seed module; requires ingestion review."
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    (case_dir / "anatomy.md").write_text(
        "# Anatomy\n\nPrimitive: meshline reference primitive.\n\n"
        "Technique: seed-level public-source review; deeper implementation anatomy is pending.\n",
        encoding="utf-8",
    )
    (case_dir / "lesson.md").write_text(
        "# Lesson\n\nminimal_rebuild_exercise: Describe a small meshline rebuild using generated placeholders before shortlist promotion.\n",
        encoding="utf-8",
    )
    (case_dir / "vulca_translation.md").write_text(
        "# VULCA Translation\n\nSeed translation. Review must map this case to source trail.\n",
        encoding="utf-8",
    )

    review = case_to_review_dict(validate_case_folder(case_dir))

    assert review["coverage"]["code_anatomy"] == "seed_stub"
    assert review["coverage"]["lesson"] == "seed_stub"
    assert review["coverage"]["vulca_translation"] == "seed_stub"
    assert review["coverage"]["module_payloads"] == "seed_stub"
    assert set(review["data_quality_flags"]) >= {
        "seed_anatomy",
        "seed_lesson",
        "seed_vulca_translation",
        "metadata_only_modules",
    }


def test_asset_manifest_capture_failure_counts_as_partial(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder

    case_dir = write_case(tmp_path)
    metadata_path = case_dir / "metadata.json"
    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    payload["captures"].append(
        {
            "id": "asset-manifest-capture-failure",
            "evidence_type": "asset_manifest",
            "path_or_url": "assets/asset_manifest.json",
            "capture_method": "manual_browser",
            "viewport": "none",
            "interaction": "capture_failed",
            "captured_at": "2026-06-29",
            "source_url": "https://meshline.makio.io/",
            "confidence": "medium",
            "rights_status": "source_link_only",
            "notes": "Manifest capture failed because the asset pipeline output was not published yet.",
        }
    )
    metadata_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    record = validate_case_folder(case_dir)

    assert record.coverage["asset_manifest"] == "partial"


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
