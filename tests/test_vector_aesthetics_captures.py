from __future__ import annotations

import json
from pathlib import Path

import pytest


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


@pytest.mark.parametrize(
    ("path_or_url", "expected_exception", "match"),
    [
        ("../outside.png", ValueError, "escapes case_dir"),
        ("/tmp/outside.png", ValueError, "relative to case_dir"),
    ],
)
def test_add_capture_rejects_paths_outside_case_dir(
    tmp_path: Path,
    path_or_url: str,
    expected_exception: type[Exception],
    match: str,
):
    from vulca.vector_aesthetics.captures import add_capture
    from vulca.vector_aesthetics.seeds import write_seed_cases

    case_dir = write_seed_cases(tmp_path)[0]
    metadata_path = case_dir / "metadata.json"
    before = metadata_path.read_text(encoding="utf-8")

    with pytest.raises(expected_exception, match=match):
        add_capture(
            case_dir,
            {
                "id": "outside-path",
                "evidence_type": "screenshot",
                "path_or_url": path_or_url,
                "capture_method": "manual_browser",
                "viewport": "1440x900",
                "interaction": "idle",
                "captured_at": "2026-06-29",
                "source_url": "https://meshline.makio.io/",
                "confidence": "low",
                "rights_status": "local_capture",
                "notes": "Outside paths should fail.",
            },
        )

    assert metadata_path.read_text(encoding="utf-8") == before


def test_add_capture_rejects_directory_path_for_local_capture(tmp_path: Path):
    from vulca.vector_aesthetics.captures import add_capture
    from vulca.vector_aesthetics.seeds import write_seed_cases

    case_dir = write_seed_cases(tmp_path)[0]
    metadata_path = case_dir / "metadata.json"
    before = metadata_path.read_text(encoding="utf-8")
    (case_dir / "capture-directory").mkdir(parents=True)

    with pytest.raises(FileNotFoundError, match="capture-directory"):
        add_capture(
            case_dir,
            {
                "id": "directory-path",
                "evidence_type": "screenshot",
                "path_or_url": "capture-directory",
                "capture_method": "manual_browser",
                "viewport": "1440x900",
                "interaction": "idle",
                "captured_at": "2026-06-29",
                "source_url": "https://meshline.makio.io/",
                "confidence": "low",
                "rights_status": "local_capture",
                "notes": "Directory paths should fail.",
            },
        )

    assert metadata_path.read_text(encoding="utf-8") == before


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


def test_cli_failure_records_capture_failed_entry_and_prints_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    from scripts.vector_aesthetics_record_capture import main
    from vulca.vector_aesthetics.seeds import write_seed_cases

    case_dir = write_seed_cases(tmp_path)[0]

    exit_code = main(
        [
            "--case-dir",
            str(case_dir),
            "--failure",
            "--evidence-type",
            "video",
            "--source-url",
            "https://meshline.makio.io/",
            "--notes",
            "Autoplay blocked in automated browser.",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "recorded"
    assert payload["case_id"] == "makio-meshline"
    assert payload["capture_count"] == 3

    metadata = json.loads((case_dir / "metadata.json").read_text(encoding="utf-8"))
    assert any(
        capture["evidence_type"] == "video" and capture["interaction"] == "capture_failed"
        for capture in metadata["captures"]
    )


def test_cli_default_id_and_missing_path_or_url_behavior(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    from scripts.vector_aesthetics_record_capture import main
    from vulca.vector_aesthetics.seeds import write_seed_cases

    case_dir = write_seed_cases(tmp_path)[0]
    screenshot_path = case_dir / "screenshots" / "idle.png"
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    screenshot_path.write_bytes(b"fixture")

    exit_code = main(
        [
            "--case-dir",
            str(case_dir),
            "--evidence-type",
            "screenshot",
            "--path-or-url",
            "screenshots/idle.png",
            "--source-url",
            "https://meshline.makio.io/",
            "--notes",
            "Idle screenshot.",
            "--viewport",
            "1440x900",
            "--interaction",
            "idle",
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "recorded"
    assert payload["case_id"] == "makio-meshline"
    assert payload["capture_count"] == 4

    metadata = json.loads((case_dir / "metadata.json").read_text(encoding="utf-8"))
    assert any(capture["id"] == "screenshot-idle" for capture in metadata["captures"])

    with pytest.raises(SystemExit, match="--path-or-url is required unless --failure is set"):
        main(
            [
                "--case-dir",
                str(case_dir),
                "--evidence-type",
                "screenshot",
                "--source-url",
                "https://meshline.makio.io/",
                "--notes",
                "Idle screenshot.",
            ]
        )
