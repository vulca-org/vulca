"""Preflight checks for VULCA customer-facing solution-pack artifacts."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence
from xml.etree import ElementTree


@dataclass(frozen=True)
class PreflightIssue:
    rule_id: str
    line: int
    match: str
    message: str
    source: str


@dataclass(frozen=True)
class PreflightReport:
    source: str
    issues: list[PreflightIssue]

    @property
    def ok(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "ok": self.ok,
            "issue_count": len(self.issues),
            "issues": [asdict(issue) for issue in self.issues],
        }


@dataclass(frozen=True)
class PreflightRule:
    rule_id: str
    pattern: re.Pattern[str]
    message: str


RULES: tuple[PreflightRule, ...] = (
    PreflightRule(
        "file_url",
        re.compile(r"file://", re.IGNORECASE),
        "Customer-facing artifacts must not contain local file URLs.",
    ),
    PreflightRule(
        "local_path",
        re.compile(r"(/Users/|/home/|/private/var/|/var/folders/|\.codex/|[A-Za-z]:\\)", re.IGNORECASE),
        "Customer-facing artifacts must not contain local filesystem paths.",
    ),
    PreflightRule(
        "internal_label",
        re.compile(r"\binternal\s+(crop|proof|only|reserve|reference)\b", re.IGNORECASE),
        "Internal labels must be removed or rewritten before customer export.",
    ),
    PreflightRule(
        "capture_batch",
        re.compile(r"capture-batch-\d+", re.IGNORECASE),
        "Capture-batch identifiers are internal provenance and must not be exported.",
    ),
    PreflightRule(
        "debug_overlay",
        re.compile(r"debug\s+(overlay|label|labels|note|notes)", re.IGNORECASE),
        "Debug overlay or label language must not be customer-visible.",
    ),
    PreflightRule(
        "raw_crop",
        re.compile(r"raw\s+(source\s+)?crop", re.IGNORECASE),
        "Raw crop language indicates untreated internal evidence material.",
    ),
    PreflightRule(
        "crop_box",
        re.compile(r"(crop\s+boxes?|crop\s+coordinates?|data-crop)", re.IGNORECASE),
        "Crop boxes and crop coordinates belong in the internal source matrix.",
    ),
    PreflightRule(
        "source_log",
        re.compile(r"source-log", re.IGNORECASE),
        "Source-log filenames belong in internal provenance notes only.",
    ),
    PreflightRule(
        "internal_reference_material",
        re.compile(r"(alibaba\s+case-study|case-study/alibaba|03-creatify-case-study)", re.IGNORECASE),
        "Alibaba case-study material is internal reference by default.",
    ),
    PreflightRule(
        "unsupported_relationship_claim",
        re.compile(r"\b(is|are|as)\s+(a\s+)?VULCA\s+(customer|partner|endorser)\b", re.IGNORECASE),
        "Named companies must not be framed as VULCA customers, partners, or endorsers.",
    ),
    PreflightRule(
        "unsupported_certification_claim",
        re.compile(r"\b(VULCA\s+certifies|certified\s+by\s+VULCA|approved\s+by\s+VULCA)\b", re.IGNORECASE),
        "VULCA must not be framed as a certification or approval authority.",
    ),
)


def scan_text(text: str, *, source: str = "<text>", rules: Sequence[PreflightRule] = RULES) -> PreflightReport:
    issues: list[PreflightIssue] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule in rules:
            match = rule.pattern.search(line)
            if match:
                issues.append(
                    PreflightIssue(
                        rule_id=rule.rule_id,
                        line=line_number,
                        match=match.group(0),
                        message=rule.message,
                        source=source,
                    )
                )
    return PreflightReport(source=source, issues=issues)


def _read_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        pdftotext = shutil.which("pdftotext")
        if not pdftotext:
            raise RuntimeError("PDF scanning requires pypdf or pdftotext to be available.")
        result = subprocess.run(
            [pdftotext, "-layout", str(path), "-"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"pdftotext failed for {path}: {result.stderr.strip()}")
        return result.stdout

    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _read_pptx_text(path: Path) -> str:
    slide_pattern = re.compile(r"ppt/slides/slide(\d+)\.xml$")
    pieces: list[str] = []
    try:
        with zipfile.ZipFile(path) as archive:
            slide_names = []
            for name in archive.namelist():
                match = slide_pattern.match(name)
                if match:
                    slide_names.append((int(match.group(1)), name))

            for _index, slide_name in sorted(slide_names):
                root = ElementTree.fromstring(archive.read(slide_name))
                runs = [
                    node.text or ""
                    for node in root.iter()
                    if node.tag.endswith("}t") and (node.text or "").strip()
                ]
                if runs:
                    pieces.append(" ".join(runs))
    except zipfile.BadZipFile as exc:
        raise RuntimeError(f"Could not open PPTX archive {path}: {exc}") from exc
    except ElementTree.ParseError as exc:
        raise RuntimeError(f"Could not parse PPTX slide XML in {path}: {exc}") from exc
    return "\n".join(pieces)


def read_artifact_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf_text(path)
    if suffix == ".pptx":
        return _read_pptx_text(path)
    return path.read_text(encoding="utf-8", errors="replace")


def scan_paths(paths: Iterable[Path]) -> list[PreflightReport]:
    reports = []
    for path in paths:
        try:
            reports.append(scan_text(read_artifact_text(path), source=str(path)))
        except Exception as exc:
            reports.append(
                PreflightReport(
                    source=str(path),
                    issues=[
                        PreflightIssue(
                            rule_id="read_error",
                            line=0,
                            match=str(path),
                            message=f"Could not read artifact: {exc}",
                            source=str(path),
                        )
                    ],
                )
            )
    return reports


def reports_to_json(reports: Sequence[PreflightReport]) -> str:
    payload = {
        "ok": all(report.ok for report in reports),
        "report_count": len(reports),
        "issue_count": sum(len(report.issues) for report in reports),
        "reports": [report.to_dict() for report in reports],
        "issues": [asdict(issue) for report in reports for issue in report.issues],
    }
    return json.dumps(payload, indent=2, sort_keys=True)
