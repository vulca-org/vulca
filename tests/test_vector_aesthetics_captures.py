from __future__ import annotations

import json
from pathlib import Path


def test_record_capture_failure_adds_explicit_missing_evidence(tmp_path: Path):
    from vulca.vector_aesthetics.captures import record_capture_failure
    from vulca.vector_aesthetics.schema import validate_case_folder
    from vulca.vector_aesthetics.seeds import write_seed_cases

    case_dir = write_seed_cases(tmp_path)[0]

    record_capture_failure(
        case_dir,
        evidence_type="video",
        notes="Autoplay blocked in automated browser.",
        source_url="https://meshline.makio.io/",
    )

    metadata = json.loads((case_dir / "metadata.json").read_text(encoding="utf-8"))
    assert any(capture["evidence_type"] == "video" for capture in metadata["captures"])
    assert validate_case_folder(case_dir).coverage["video"] == "partial"


def test_add_capture_rejects_missing_local_file(tmp_path: Path):
    from vulca.vector_aesthetics.captures import add_capture
    from vulca.vector_aesthetics.seeds import write_seed_cases

    case_dir = write_seed_cases(tmp_path)[0]

    try:
        add_capture(
            case_dir,
            {
                "id": "missing-screenshot",
                "evidence_type": "screenshot",
                "path_or_url": "screenshots/missing.png",
                "capture_method": "manual_browser",
                "viewport": "1440x900",
                "interaction": "idle",
                "captured_at": "2026-06-29",
                "source_url": "https://meshline.makio.io/",
                "confidence": "low",
                "rights_status": "local_capture",
                "notes": "Missing file should fail.",
            },
        )
    except FileNotFoundError as exc:
        assert "screenshots/missing.png" in str(exc)
    else:
        raise AssertionError("missing local file was accepted")


def test_add_capture_restores_metadata_when_validation_fails(tmp_path: Path):
    from vulca.vector_aesthetics.captures import add_capture
    from vulca.vector_aesthetics.seeds import write_seed_cases

    case_dir = write_seed_cases(tmp_path)[0]
    metadata_path = case_dir / "metadata.json"
    before = metadata_path.read_text(encoding="utf-8")

    try:
        add_capture(
            case_dir,
            {
                "id": "bad-confidence",
                "evidence_type": "screenshot",
                "path_or_url": "https://meshline.makio.io/",
                "capture_method": "manual_browser",
                "viewport": "none",
                "interaction": "capture_failed",
                "captured_at": "2026-06-29",
                "source_url": "https://meshline.makio.io/",
                "confidence": "certain",
                "rights_status": "source_link_only",
                "notes": "Invalid confidence should not persist.",
            },
        )
    except ValueError as exc:
        assert "invalid capture confidence" in str(exc)
    else:
        raise AssertionError("invalid capture was accepted")

    assert metadata_path.read_text(encoding="utf-8") == before
