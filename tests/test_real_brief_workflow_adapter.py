from __future__ import annotations

import json
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


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_adapt_real_brief_package_writes_supported_visual_workflow(tmp_path):
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(
        tmp_path,
        "seattle-polish-film-festival-poster",
    )
    original_manifest = (source_package / "manifest.json").read_text(encoding="utf-8")

    result = adapt_real_brief_package(
        source_package=source_package,
        root=tmp_path / "repo",
        date="2026-05-01",
    )

    project_dir = (
        tmp_path
        / "repo"
        / "docs"
        / "visual-specs"
        / "seattle-polish-film-festival-poster"
    )
    real_brief_dir = project_dir / "real_brief"
    discovery_dir = project_dir / "discovery"

    assert result["slug"] == "seattle-polish-film-festival-poster"
    assert result["status"] == "ready_for_visual_brainstorm"
    assert Path(result["project_dir"]) == project_dir
    assert Path(result["workflow_seed_md"]) == project_dir / "workflow_seed.md"
    assert Path(result["adapter_manifest_json"]) == (
        real_brief_dir / "adapter_manifest.json"
    )
    assert Path(result["discovery_md"]) == discovery_dir / "discovery.md"

    for rel in [
        "discovery/discovery.md",
        "discovery/taste_profile.json",
        "discovery/direction_cards.json",
        "discovery/sketch_prompts.json",
        "real_brief/adapter_manifest.json",
        "real_brief/source_package_manifest.json",
        "real_brief/structured_brief.json",
        "real_brief/workflow_handoff.json",
        "real_brief/decision_package.md",
        "real_brief/production_package.md",
        "real_brief/review_schema.json",
        "real_brief/source_brief.md",
        "real_brief/summary.md",
        "real_brief/conditions/A-one-shot.md",
        "real_brief/prompts/D.txt",
        "workflow_seed.md",
    ]:
        assert (project_dir / rel).exists(), rel

    manifest = _read_json(real_brief_dir / "adapter_manifest.json")
    assert manifest["schema_version"] == "0.1"
    assert manifest["adapter"] == "real-brief-workflow-adapter"
    assert manifest["source_experiment"] == "real-brief-benchmark"
    assert manifest["slug"] == "seattle-polish-film-festival-poster"
    assert manifest["workflow_status"] == "ready_for_visual_brainstorm"
    assert manifest["human_gate_required"] is True
    assert manifest["simulation_only"] is True
    assert manifest["domain"] == "poster"
    assert manifest["visual_workflow_domain"] == "poster"
    assert manifest["created"] == "2026-05-01"
    assert manifest["workflow_artifacts"]["discovery_md"] == (
        "../discovery/discovery.md"
    )
    assert manifest["next_steps"] == [
        "/visual-brainstorm seattle-polish-film-festival-poster",
        "/visual-spec seattle-polish-film-festival-poster",
        "/visual-plan seattle-polish-film-festival-poster",
        "/evaluate seattle-polish-film-festival-poster",
    ]

    discovery_md = (discovery_dir / "discovery.md").read_text(encoding="utf-8")
    assert "ready_for_brainstorm" in discovery_md
    assert "Ready for /visual-brainstorm" in discovery_md
    assert "Seattle Polish Film Festival Poster" in discovery_md

    workflow_seed = (project_dir / "workflow_seed.md").read_text(encoding="utf-8")
    assert "ready_for_visual_brainstorm" in workflow_seed
    assert "/visual-brainstorm seattle-polish-film-festival-poster" in workflow_seed
    assert "/visual-spec must resolve design.md" in workflow_seed
    assert "not a substitute for `proposal.md`" in workflow_seed

    assert (source_package / "manifest.json").read_text(encoding="utf-8") == (
        original_manifest
    )


def test_adapt_real_brief_package_generated_artifacts_do_not_leak_secrets(tmp_path):
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(
        tmp_path,
        "seattle-polish-film-festival-poster",
    )

    adapt_real_brief_package(
        source_package=source_package,
        root=tmp_path / "repo",
        date="2026-05-01",
    )

    project_dir = (
        tmp_path
        / "repo"
        / "docs"
        / "visual-specs"
        / "seattle-polish-film-festival-poster"
    )
    generated_files = sorted(
        path
        for path in project_dir.rglob("*")
        if path.suffix in {".md", ".json", ".txt"}
    )

    assert generated_files
    for generated_file in generated_files:
        text = generated_file.read_text(encoding="utf-8")
        assert "sk-" not in text, generated_file
        assert "VULCA_REAL_PROVIDER_API_KEY" not in text, generated_file
        assert "OPENAI_API_KEY" not in text, generated_file
        assert "globalai" not in text.casefold(), generated_file


def test_adapt_real_brief_package_dry_run_writes_nothing(tmp_path):
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(tmp_path, "gsm-community-market-campaign")
    root = tmp_path / "repo"

    result = adapt_real_brief_package(
        source_package=source_package,
        root=root,
        date="2026-05-01",
        dry_run=True,
    )

    assert result["slug"] == "gsm-community-market-campaign"
    assert result["status"] == "ready_for_visual_brainstorm"
    assert result["dry_run"] == "true"
    assert not (root / "docs").exists()


@pytest.mark.parametrize(
    ("filename", "status"),
    [
        ("proposal.md", "ready"),
        ("design.md", "resolved"),
        ("plan.md", "completed"),
        ("plan.md", "partial"),
        ("plan.md", "aborted"),
    ],
)
def test_adapt_real_brief_package_refuses_finalized_workflow_files(
    tmp_path,
    filename,
    status,
):
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(tmp_path, "seattle-polish-film-festival-poster")
    project_dir = (
        tmp_path
        / "repo"
        / "docs"
        / "visual-specs"
        / "seattle-polish-film-festival-poster"
    )
    project_dir.mkdir(parents=True)
    (project_dir / filename).write_text(f"status: {status}\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="refusing finalized workflow overwrite"):
        adapt_real_brief_package(
            source_package=source_package,
            root=tmp_path / "repo",
            date="2026-05-01",
        )


def test_adapt_real_brief_package_requires_force_for_existing_generated_dirs(tmp_path):
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(tmp_path, "seattle-polish-film-festival-poster")
    project_dir = (
        tmp_path
        / "repo"
        / "docs"
        / "visual-specs"
        / "seattle-polish-film-festival-poster"
    )
    (project_dir / "discovery").mkdir(parents=True)

    with pytest.raises(RuntimeError, match="force_discovery=True"):
        adapt_real_brief_package(
            source_package=source_package,
            root=tmp_path / "repo",
            date="2026-05-01",
        )

    (project_dir / "discovery").rmdir()
    (project_dir / "real_brief").mkdir()

    with pytest.raises(RuntimeError, match="force_real_brief=True"):
        adapt_real_brief_package(
            source_package=source_package,
            root=tmp_path / "repo",
            date="2026-05-01",
        )

    result = adapt_real_brief_package(
        source_package=source_package,
        root=tmp_path / "repo",
        date="2026-05-01",
        force_discovery=True,
        force_real_brief=True,
    )
    assert result["status"] == "ready_for_visual_brainstorm"


@pytest.mark.parametrize(
    ("path", "mutate"),
    [
        ("manifest.json", lambda data: data.update({"schema_version": "9.9"})),
        ("manifest.json", lambda data: data.update({"provider_execution": "enabled"})),
        ("workflow_handoff.json", lambda data: data.update({"schema_version": "9.9"})),
        (
            "workflow_handoff.json",
            lambda data: data.update({"human_gate_required": False}),
        ),
        ("structured_brief.json", lambda data: data.update({"slug": "different-slug"})),
    ],
)
def test_adapt_real_brief_package_validates_source_package(tmp_path, path, mutate):
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(tmp_path, "seattle-polish-film-festival-poster")
    payload_path = source_package / path
    payload = _read_json(payload_path)
    mutate(payload)
    _write_json(payload_path, payload)

    with pytest.raises(ValueError):
        adapt_real_brief_package(
            source_package=source_package,
            root=tmp_path / "repo",
            date="2026-05-01",
        )


def test_adapt_real_brief_package_requires_core_source_files(tmp_path):
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(tmp_path, "seattle-polish-film-festival-poster")
    (source_package / "production_package.md").unlink()

    with pytest.raises(FileNotFoundError, match="production_package.md"):
        adapt_real_brief_package(
            source_package=source_package,
            root=tmp_path / "repo",
            date="2026-05-01",
        )


@pytest.mark.parametrize(
    ("slug", "expected_domain"),
    [
        ("erie-botanical-gardens-public-art", "public_art"),
        ("music-video-treatment-low-budget", "video_treatment"),
    ],
)
def test_adapt_real_brief_package_preserves_unsupported_domain_without_discovery(
    tmp_path,
    slug,
    expected_domain,
):
    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    source_package = _source_package(tmp_path, slug)

    result = adapt_real_brief_package(
        source_package=source_package,
        root=tmp_path / "repo",
        date="2026-05-01",
    )

    project_dir = (
        tmp_path
        / "repo"
        / "docs"
        / "visual-specs"
        / slug
    )
    real_brief_dir = project_dir / "real_brief"

    assert result["status"] == "unsupported_for_visual_chain"
    assert "discovery_md" not in result
    assert Path(result["workflow_seed_md"]) == project_dir / "workflow_seed.md"
    assert (real_brief_dir / "adapter_manifest.json").exists()
    assert (real_brief_dir / "source_package_manifest.json").exists()
    assert (real_brief_dir / "structured_brief.json").exists()
    assert not (project_dir / "discovery").exists()

    manifest = _read_json(real_brief_dir / "adapter_manifest.json")
    assert manifest["workflow_status"] == "unsupported_for_visual_chain"
    assert manifest["domain"] == expected_domain
    assert manifest["visual_workflow_domain"] is None
    assert manifest["unsupported_reason"] == (
        "source domain is outside /visual-brainstorm static 2D scope"
    )
    assert manifest["workflow_artifacts"]["discovery_md"] is None

    workflow_seed = (project_dir / "workflow_seed.md").read_text(encoding="utf-8")
    assert "unsupported_for_visual_chain" in workflow_seed
    assert "does not start `/visual-brainstorm`" in workflow_seed


def test_real_brief_workflow_adapter_cli_dry_run(tmp_path, capsys):
    from scripts.real_brief_workflow_adapter import main

    source_package = _source_package(tmp_path, "seattle-polish-film-festival-poster")

    rc = main(
        [
            "--source-package",
            str(source_package),
            "--root",
            str(tmp_path / "repo"),
            "--date",
            "2026-05-01",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert rc == 0
    assert payload["slug"] == "seattle-polish-film-festival-poster"
    assert payload["status"] == "ready_for_visual_brainstorm"
    assert payload["dry_run"] == "true"
    assert not (tmp_path / "repo" / "docs").exists()


def test_real_brief_workflow_adapter_cli_writes_files(tmp_path, capsys):
    from scripts.real_brief_workflow_adapter import main

    source_package = _source_package(tmp_path, "gsm-community-market-campaign")

    rc = main(
        [
            "--source-package",
            str(source_package),
            "--root",
            str(tmp_path / "repo"),
            "--date",
            "2026-05-01",
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    project_dir = tmp_path / "repo" / "docs" / "visual-specs" / (
        "gsm-community-market-campaign"
    )

    assert rc == 0
    assert payload["status"] == "ready_for_visual_brainstorm"
    assert (project_dir / "workflow_seed.md").exists()


def test_real_brief_workflow_adapter_can_resolve_source_root_slug_date(tmp_path):
    from scripts.real_brief_workflow_adapter import main

    _source_package(tmp_path, "gsm-community-market-campaign")

    rc = main(
        [
            "--source-root",
            str(tmp_path / "source"),
            "--slug",
            "gsm-community-market-campaign",
            "--root",
            str(tmp_path / "repo"),
            "--date",
            "2026-05-01",
            "--dry-run",
        ]
    )

    assert rc == 0


def test_real_brief_workflow_adapter_validates_selector_before_adapter_import():
    from scripts.real_brief_workflow_adapter import main

    sys.modules.pop("vulca.real_brief.workflow_adapter", None)

    with pytest.raises(RuntimeError, match="--source-package"):
        main(["--date", "2026-05-01"])

    assert "vulca.real_brief.workflow_adapter" not in sys.modules


def test_real_brief_workflow_adapter_public_export_is_lazy():
    from vulca.real_brief import adapt_real_brief_package

    assert callable(adapt_real_brief_package)
