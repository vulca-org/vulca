from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _source_package(tmp_path: Path, slug: str) -> Path:
    from vulca.real_brief.artifacts import write_real_brief_dry_run

    result = write_real_brief_dry_run(
        output_root=tmp_path / "source",
        slug=slug,
        date="2026-05-01",
        write_html_review=False,
    )
    return Path(result["output_dir"])


def _adapted_project(tmp_path: Path, slug: str) -> Path:
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(tmp_path, slug)
    result = adapt_real_brief_package(
        source_package=source_package,
        root=tmp_path / "repo",
        date="2026-05-01",
    )
    return Path(result["project_dir"])


def _frontmatter(markdown: str) -> dict[str, str]:
    assert markdown.startswith("---\n")
    frontmatter = markdown.split("---\n", 2)[1]
    parsed: dict[str, str] = {}
    for line in frontmatter.strip().splitlines():
        key, value = line.split(": ", 1)
        parsed[key] = value
    return parsed


def test_seed_real_brief_brainstorm_proposal_writes_draft_proposal(tmp_path):
    from vulca.real_brief.brainstorm_seed import (
        seed_real_brief_brainstorm_proposal,
    )

    project_dir = _adapted_project(tmp_path, "seattle-polish-film-festival-poster")

    result = seed_real_brief_brainstorm_proposal(
        root=tmp_path / "repo",
        slug="seattle-polish-film-festival-poster",
        date="2026-05-01",
    )

    proposal_path = project_dir / "proposal.md"
    assert result == {
        "slug": "seattle-polish-film-festival-poster",
        "status": "draft",
        "project_dir": str(project_dir),
        "proposal_md": str(proposal_path),
    }
    assert proposal_path.exists()

    proposal = proposal_path.read_text(encoding="utf-8")
    frontmatter = _frontmatter(proposal)
    assert list(frontmatter) == [
        "slug",
        "status",
        "domain",
        "tradition",
        "style_treatment",
        "generated_by",
        "created",
        "updated",
    ]
    assert frontmatter["slug"] == "seattle-polish-film-festival-poster"
    assert frontmatter["status"] == "draft"
    assert frontmatter["domain"] == "poster"
    assert frontmatter["tradition"] == "null"
    assert frontmatter["style_treatment"] == "unified"
    assert frontmatter["generated_by"] == "visual-brainstorm@0.1.0"
    assert frontmatter["created"] == "2026-05-01"
    assert frontmatter["updated"] == "2026-05-01"

    assert "# Seattle Polish Film Festival Poster" in proposal
    assert "## Intent" in proposal
    assert "Signature poster concept for the 34th festival edition." in proposal
    assert "festival attendees" in proposal
    assert "poster concept (11 x 17 in vertical, print/digital)" in proposal
    assert "bottom sponsor or patron logo band must remain available" in proposal
    assert "not specified by source" in proposal
    assert "source: https://www.polishfilms.org/submit-a-poster" in proposal
    assert "## Acceptance rubric" in proposal
    assert "- brief compliance (0-2)" in proposal
    assert "- cultural taste specificity (0-2)" in proposal
    assert "Which stakeholder approves the final direction?" in proposal
    assert "Human approval required before `/visual-spec`." in proposal


def test_seed_real_brief_brainstorm_proposal_includes_review_schema_rubric(tmp_path):
    from vulca.real_brief.brainstorm_seed import (
        seed_real_brief_brainstorm_proposal,
    )

    project_dir = _adapted_project(tmp_path, "model-young-package-unpacking-taboo")

    seed_real_brief_brainstorm_proposal(
        root=tmp_path / "repo",
        slug="model-young-package-unpacking-taboo",
        date="2026-05-01",
    )

    proposal = (project_dir / "proposal.md").read_text(encoding="utf-8")
    assert "## Acceptance rubric" in proposal
    assert "- brief compliance (0-2)" in proposal
    assert "- structural control (0-2)" in proposal
    assert "- production realism (0-2)" in proposal
    assert "- decision usefulness (0-2)" in proposal


def test_seed_real_brief_brainstorm_proposal_dry_run_writes_nothing(tmp_path):
    from vulca.real_brief.brainstorm_seed import (
        seed_real_brief_brainstorm_proposal,
    )

    project_dir = _adapted_project(tmp_path, "gsm-community-market-campaign")

    result = seed_real_brief_brainstorm_proposal(
        root=tmp_path / "repo",
        slug="gsm-community-market-campaign",
        date="2026-05-01",
        dry_run=True,
    )

    assert result["dry_run"] == "true"
    assert result["status"] == "draft"
    assert not (project_dir / "proposal.md").exists()


def test_seed_real_brief_brainstorm_proposal_refuses_ready_proposal(tmp_path):
    from vulca.real_brief.brainstorm_seed import (
        seed_real_brief_brainstorm_proposal,
    )

    project_dir = _adapted_project(tmp_path, "seattle-polish-film-festival-poster")
    (project_dir / "proposal.md").write_text(
        "---\nstatus: ready\n---\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="already finalized"):
        seed_real_brief_brainstorm_proposal(
            root=tmp_path / "repo",
            slug="seattle-polish-film-festival-poster",
            date="2026-05-01",
        )


def test_seed_real_brief_brainstorm_proposal_requires_force_for_draft(tmp_path):
    from vulca.real_brief.brainstorm_seed import (
        seed_real_brief_brainstorm_proposal,
    )

    project_dir = _adapted_project(tmp_path, "seattle-polish-film-festival-poster")
    proposal_path = project_dir / "proposal.md"
    proposal_path.write_text(
        "---\nstatus: draft\n---\n\n# Existing\n",
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="pass force=True"):
        seed_real_brief_brainstorm_proposal(
            root=tmp_path / "repo",
            slug="seattle-polish-film-festival-poster",
            date="2026-05-01",
        )

    seed_real_brief_brainstorm_proposal(
        root=tmp_path / "repo",
        slug="seattle-polish-film-festival-poster",
        date="2026-05-01",
        force=True,
    )
    assert "# Seattle Polish Film Festival Poster" in proposal_path.read_text(
        encoding="utf-8"
    )


def test_seed_real_brief_brainstorm_proposal_refuses_unsupported_seed(tmp_path):
    from vulca.real_brief.brainstorm_seed import (
        seed_real_brief_brainstorm_proposal,
    )

    _adapted_project(tmp_path, "erie-botanical-gardens-public-art")

    with pytest.raises(RuntimeError, match="not ready_for_visual_brainstorm"):
        seed_real_brief_brainstorm_proposal(
            root=tmp_path / "repo",
            slug="erie-botanical-gardens-public-art",
            date="2026-05-01",
        )


def test_seed_real_brief_brainstorm_proposal_generated_draft_has_no_secrets(
    tmp_path,
):
    from vulca.real_brief.brainstorm_seed import (
        seed_real_brief_brainstorm_proposal,
    )

    project_dir = _adapted_project(tmp_path, "model-young-package-unpacking-taboo")

    seed_real_brief_brainstorm_proposal(
        root=tmp_path / "repo",
        slug="model-young-package-unpacking-taboo",
        date="2026-05-01",
    )

    proposal = (project_dir / "proposal.md").read_text(encoding="utf-8")
    assert "sk-" not in proposal
    assert "VULCA_REAL_PROVIDER_API_KEY" not in proposal
    assert "OPENAI_API_KEY" not in proposal
    assert "globalai" not in proposal.casefold()


def test_real_brief_brainstorm_seed_cli_writes_json_result(tmp_path):
    project_dir = _adapted_project(tmp_path, "seattle-polish-film-festival-poster")

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/real_brief_brainstorm_seed.py",
            "--root",
            str(tmp_path / "repo"),
            "--slug",
            "seattle-polish-film-festival-poster",
            "--date",
            "2026-05-01",
        ],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        text=True,
        capture_output=True,
    )

    result = json.loads(completed.stdout)
    assert result["status"] == "draft"
    assert result["proposal_md"] == str(project_dir / "proposal.md")
    assert (project_dir / "proposal.md").exists()


def test_real_brief_brainstorm_seed_cli_dry_run_writes_nothing(tmp_path):
    project_dir = _adapted_project(tmp_path, "seattle-polish-film-festival-poster")

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/real_brief_brainstorm_seed.py",
            "--root",
            str(tmp_path / "repo"),
            "--slug",
            "seattle-polish-film-festival-poster",
            "--date",
            "2026-05-01",
            "--dry-run",
        ],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        text=True,
        capture_output=True,
    )

    result = json.loads(completed.stdout)
    assert result["dry_run"] == "true"
    assert result["proposal_md"] == str(project_dir / "proposal.md")
    assert not (project_dir / "proposal.md").exists()


def test_real_brief_package_lazy_exports_brainstorm_seed_without_provider_imports():
    import vulca.real_brief as real_brief

    assert callable(real_brief.seed_real_brief_brainstorm_proposal)
