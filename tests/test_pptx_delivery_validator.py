from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

from scripts.validate_pptx_delivery import validate_delivery, write_markdown_report


PNG_1X1 = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"


def write_tiny_pptx(path: Path, *, slide_count: int = 2, include_media: bool = False) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("ppt/presentation.xml", "<p:presentation/>")
        archive.writestr("ppt/_rels/presentation.xml.rels", "<Relationships/>")
        for index in range(1, slide_count + 1):
            archive.writestr(f"ppt/slides/slide{index}.xml", "<p:sld/>")
        if include_media:
            archive.writestr("ppt/media/image1.png", PNG_1X1)


def write_layout_dir(path: Path, *, slide_count: int = 2) -> None:
    path.mkdir(parents=True)
    for index in range(1, slide_count + 1):
        (path / f"slide-{index:02d}.layout.json").write_text(
            json.dumps(
                {
                    "schema": "openai.presentation.layout/v4",
                    "slide": {"frame": {"left": 0, "top": 0, "width": 1280, "height": 720}},
                    "elements": [{"kind": "text", "bbox": [10, 10, 100, 20], "text": "ok"}],
                },
            ),
            encoding="utf-8",
        )


def write_png(path: Path) -> None:
    path.write_bytes(PNG_1X1)


def test_valid_delivery_is_internal_demo_ready(tmp_path: Path) -> None:
    pptx = tmp_path / "deck.pptx"
    layout_dir = tmp_path / "layout"
    contact_sheet = tmp_path / "contact-sheet.png"
    write_tiny_pptx(pptx)
    write_layout_dir(layout_dir)
    write_png(contact_sheet)

    result = validate_delivery(
        pptx_path=pptx,
        layout_dir=layout_dir,
        contact_sheet_path=contact_sheet,
        label="Tiny deck",
        renderer_paths={"libreoffice": None, "powerpoint": None, "keynote": None},
    )

    assert result.ok is True
    assert result.delivery_gate == "internal-demo-ok-public-blocked"
    assert result.checks["slide_count"] == 2
    assert result.checks["layout_file_count"] == 2
    assert result.checks["contact_sheet"] == {"width": 1, "height": 1}
    assert any(issue.code == "native_renderer_unverified" for issue in result.issues)


def test_missing_contact_sheet_blocks_delivery(tmp_path: Path) -> None:
    pptx = tmp_path / "deck.pptx"
    layout_dir = tmp_path / "layout"
    write_tiny_pptx(pptx)
    write_layout_dir(layout_dir)

    result = validate_delivery(
        pptx_path=pptx,
        layout_dir=layout_dir,
        contact_sheet_path=tmp_path / "missing.png",
        label="Tiny deck",
        renderer_paths={},
    )

    assert result.ok is False
    assert result.delivery_gate == "blocked"
    assert any(issue.severity == "error" and issue.code == "missing_contact_sheet" for issue in result.issues)


def test_embedded_media_warns_but_allows_internal_demo(tmp_path: Path) -> None:
    pptx = tmp_path / "deck.pptx"
    layout_dir = tmp_path / "layout"
    contact_sheet = tmp_path / "contact-sheet.png"
    write_tiny_pptx(pptx, include_media=True)
    write_layout_dir(layout_dir)
    write_png(contact_sheet)

    result = validate_delivery(
        pptx_path=pptx,
        layout_dir=layout_dir,
        contact_sheet_path=contact_sheet,
        label="Tiny deck",
        renderer_paths={"libreoffice": None},
    )

    assert result.ok is True
    assert result.checks["media_entries"] == ["ppt/media/image1.png"]
    assert any(issue.severity == "warning" and issue.code == "embedded_media_present" for issue in result.issues)


def test_malformed_pptx_zip_blocks_delivery(tmp_path: Path) -> None:
    pptx = tmp_path / "deck.pptx"
    layout_dir = tmp_path / "layout"
    contact_sheet = tmp_path / "contact-sheet.png"
    pptx.write_text("not a zip", encoding="utf-8")
    write_layout_dir(layout_dir)
    write_png(contact_sheet)

    result = validate_delivery(
        pptx_path=pptx,
        layout_dir=layout_dir,
        contact_sheet_path=contact_sheet,
        label="Tiny deck",
        renderer_paths={},
    )

    assert result.ok is False
    assert any(issue.code == "invalid_pptx_zip" for issue in result.issues)


def test_missing_layout_json_blocks_delivery(tmp_path: Path) -> None:
    pptx = tmp_path / "deck.pptx"
    layout_dir = tmp_path / "layout"
    contact_sheet = tmp_path / "contact-sheet.png"
    write_tiny_pptx(pptx)
    layout_dir.mkdir()
    write_png(contact_sheet)

    result = validate_delivery(
        pptx_path=pptx,
        layout_dir=layout_dir,
        contact_sheet_path=contact_sheet,
        label="Tiny deck",
        renderer_paths={},
    )

    assert result.ok is False
    assert any(issue.code == "missing_layout_json" for issue in result.issues)


def test_markdown_report_records_gate_and_disclaimer(tmp_path: Path) -> None:
    pptx = tmp_path / "deck.pptx"
    layout_dir = tmp_path / "layout"
    contact_sheet = tmp_path / "contact-sheet.png"
    report_path = tmp_path / "report.md"
    write_tiny_pptx(pptx)
    write_layout_dir(layout_dir)
    write_png(contact_sheet)

    result = validate_delivery(
        pptx_path=pptx,
        layout_dir=layout_dir,
        contact_sheet_path=contact_sheet,
        label="Tiny deck",
        renderer_paths={"libreoffice": None},
    )
    write_markdown_report([result], report_path)

    body = report_path.read_text(encoding="utf-8")
    assert "Delivery gate" in body
    assert "internal-demo-ok-public-blocked" in body
    assert "does not prove native PowerPoint, Keynote, or Google Slides visual fidelity" in body


def test_cli_writes_report(tmp_path: Path) -> None:
    pptx = tmp_path / "deck.pptx"
    layout_dir = tmp_path / "layout"
    contact_sheet = tmp_path / "contact-sheet.png"
    report_path = tmp_path / "report.md"
    write_tiny_pptx(pptx)
    write_layout_dir(layout_dir)
    write_png(contact_sheet)

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/validate_pptx_delivery.py",
            "--pptx",
            str(pptx),
            "--layout-dir",
            str(layout_dir),
            "--contact-sheet",
            str(contact_sheet),
            "--label",
            "Tiny deck",
            "--out",
            str(report_path),
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        timeout=10,
    )

    assert completed.returncode == 0, completed.stderr
    assert "internal-demo-ok-public-blocked" in completed.stdout
    assert "Delivery gate" in report_path.read_text(encoding="utf-8")
