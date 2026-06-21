from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import vulca.solution_pack_preflight as preflight
from vulca.solution_pack_preflight import read_artifact_text, scan_paths, scan_text


ROOT = Path(__file__).resolve().parent.parent


def test_scan_text_flags_internal_material_with_line_numbers() -> None:
    text = "\n".join(
        [
            "VULCA customer-facing sample.",
            "Use /Users/yhryzy/.codex/worktrees/f7cb/vulca/assets/raw.png.",
            "The layout still contains an INTERNAL CROP ribbon.",
            "Keep capture-batch-02 source data out of exports.",
            "Alibaba case-study material should not be visual proof.",
        ]
    )

    report = scan_text(text, source="sample.md")

    assert report.ok is False
    assert [(issue.rule_id, issue.line) for issue in report.issues] == [
        ("local_path", 2),
        ("internal_label", 3),
        ("capture_batch", 4),
        ("internal_reference_material", 5),
    ]


def test_scan_text_allows_boundary_copy_and_public_example_language() -> None:
    text = "\n".join(
        [
            "Named companies are public examples only.",
            "They are not VULCA customers, partners, endorsers, authorization sources, or audit targets.",
            "This sample is not legal advice, compliance certification, platform approval, or model-safety certification.",
            "The first contact asks for feedback on the sample pack.",
        ]
    )

    report = scan_text(text, source="safe.md")

    assert report.ok is True
    assert report.issues == []


def test_scan_text_flags_linux_home_paths() -> None:
    report = scan_text("Do not export /home/reviewer/customer-pack/raw.png", source="linux.md")

    assert report.ok is False
    assert [(issue.rule_id, issue.line) for issue in report.issues] == [("local_path", 1)]


def test_cli_reports_json_and_nonzero_exit_for_forbidden_text(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate.md"
    candidate.write_text(
        "This customer PDF still references file:///Users/example/raw.png\n"
        "and includes debug overlay notes.\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/customer_pdf_preflight.py"),
            "--json",
            str(candidate),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert {issue["rule_id"] for issue in payload["issues"]} == {
        "file_url",
        "local_path",
        "debug_overlay",
    }


def test_read_artifact_text_uses_pdftotext_fallback_when_pypdf_is_missing(
    tmp_path: Path,
    monkeypatch,
) -> None:
    pdf = tmp_path / "candidate.pdf"
    pdf.write_bytes(b"%PDF-1.4 placeholder")

    monkeypatch.setitem(sys.modules, "pypdf", None)
    monkeypatch.setattr(preflight.shutil, "which", lambda name: "/usr/bin/pdftotext" if name == "pdftotext" else None)

    def fake_run(args, capture_output, text, check):
        assert args == ["/usr/bin/pdftotext", "-layout", str(pdf), "-"]
        assert capture_output is True
        assert text is True
        assert check is False
        return subprocess.CompletedProcess(args, 0, stdout="PDF text with source-safe fields", stderr="")

    monkeypatch.setattr(preflight.subprocess, "run", fake_run)

    assert read_artifact_text(pdf) == "PDF text with source-safe fields"


def test_scan_paths_reports_missing_file_as_read_error(tmp_path: Path) -> None:
    missing = tmp_path / "missing.md"

    report = scan_paths([missing])[0]

    assert report.ok is False
    assert report.issues[0].rule_id == "read_error"
    assert report.issues[0].line == 0
    assert str(missing) in report.issues[0].match
