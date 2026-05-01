from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _source_package(tmp_path: Path, slug: str) -> Path:
    from vulca.real_brief.artifacts import write_real_brief_dry_run

    result = write_real_brief_dry_run(
        output_root=tmp_path / "source",
        slug=slug,
        date="2026-05-01",
        write_html_review=False,
    )
    return Path(result["output_dir"])


def _workflow_root_with_supported_and_unsupported(tmp_path: Path) -> Path:
    from vulca.real_brief.brainstorm_seed import (
        seed_real_brief_brainstorm_proposal,
    )
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    root = tmp_path / "workflow"
    for slug in [
        "seattle-polish-film-festival-poster",
        "erie-botanical-gardens-public-art",
    ]:
        adapt_real_brief_package(
            source_package=_source_package(tmp_path, slug),
            root=root,
            date="2026-05-01",
        )

    seed_real_brief_brainstorm_proposal(
        root=root,
        slug="seattle-polish-film-festival-poster",
        date="2026-05-01",
    )
    return root


def test_workflow_review_html_summarizes_supported_and_unsupported_briefs(tmp_path):
    from vulca.real_brief.workflow_review_html import write_workflow_review_html

    root = _workflow_root_with_supported_and_unsupported(tmp_path)

    html_path = write_workflow_review_html(root)

    assert html_path == root / "real_brief_workflow_review.html"
    html = html_path.read_text(encoding="utf-8")
    assert "Real Brief Workflow Review" in html
    assert "Seattle Polish Film Festival Poster" in html
    assert "Buffalo and Erie County Botanical Gardens Public Art" in html
    assert "ready_for_visual_brainstorm" in html
    assert "unsupported_for_visual_chain" in html
    assert "source domain is outside /visual-brainstorm static 2D scope" in html
    assert "proposal.md" in html
    assert "Proposal: draft" in html
    assert "Human approval required before /visual-spec" in html
    assert "brief compliance (0-2)" in html
    assert "decision usefulness (0-2)" in html
    assert "Which stakeholder approves the final direction?" in html
    assert "real_brief/decision_package.md" in html
    assert "real_brief/review_schema.json" in html


def test_workflow_review_html_redacts_secrets_from_proposal_excerpt(tmp_path):
    from vulca.real_brief.workflow_review_html import write_workflow_review_html

    root = _workflow_root_with_supported_and_unsupported(tmp_path)
    proposal_path = (
        root
        / "docs"
        / "visual-specs"
        / "seattle-polish-film-festival-poster"
        / "proposal.md"
    )
    proposal_path.write_text(
        proposal_path.read_text(encoding="utf-8")
        + "\nProvider key: sk-test-secret-for-redaction\n",
        encoding="utf-8",
    )

    html = write_workflow_review_html(root).read_text(encoding="utf-8")

    assert "sk-test-secret-for-redaction" not in html
    assert "[redacted]" in html


def test_workflow_review_html_cli_writes_json_result(tmp_path):
    root = _workflow_root_with_supported_and_unsupported(tmp_path)

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/build_real_brief_workflow_review.py",
            "--root",
            str(root),
        ],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        text=True,
        capture_output=True,
    )

    result = json.loads(completed.stdout)
    assert result["status"] == "written"
    assert result["html"] == str(root / "real_brief_workflow_review.html")
    assert (root / "real_brief_workflow_review.html").exists()
