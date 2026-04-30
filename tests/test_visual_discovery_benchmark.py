from __future__ import annotations

import json
import importlib
import os
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_experiment_projects_match_protocol_domains():
    from scripts.visual_discovery_benchmark import build_experiment_projects

    projects = build_experiment_projects()

    assert [project.slug for project in projects] == [
        "premium-tea-packaging",
        "spiritual-editorial-poster",
        "cultural-material-campaign",
    ]
    assert "xieyi restraint" in projects[0].prompt
    assert "spiritual but non-religious" in projects[1].prompt
    assert "material references" in projects[2].prompt


def test_build_conditions_a_through_d():
    from scripts.visual_discovery_benchmark import (
        build_conditions,
        build_experiment_projects,
        select_direction_card,
    )

    project = build_experiment_projects()[0]
    card = select_direction_card(project)

    conditions = build_conditions(project.prompt, card)

    assert [condition["id"] for condition in conditions] == ["A", "B", "C", "D"]
    assert conditions[0]["label"] == "User prompt only"
    assert conditions[0]["source_card_id"] == ""
    assert "cultural terms" in conditions[1]["label"].lower()
    assert card.culture_terms[0] in conditions[1]["prompt"]
    assert "Visual operations:" in conditions[2]["prompt"]
    assert conditions[3]["label"] == "Full direction-card prompt"
    assert conditions[3]["negative_prompt"]
    assert conditions[3]["evaluation_focus"]["L1"]
    assert conditions[3]["source_card_id"] == card.id


def test_write_experiment_dry_run_artifacts(tmp_path):
    from scripts.visual_discovery_benchmark import write_experiment_dry_run

    result = write_experiment_dry_run(
        output_root=tmp_path,
        slug="premium-tea-packaging",
        date="2026-04-30",
    )

    out_dir = Path(result["output_dir"])
    assert out_dir == tmp_path / "2026-04-30-premium-tea-packaging"
    for condition_id in ["A", "B", "C", "D"]:
        assert (out_dir / "prompts" / f"{condition_id}.txt").exists()
    assert (out_dir / "images" / "README.md").exists()
    assert (out_dir / "evaluations" / "README.md").exists()

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "0.1"
    assert manifest["experiment"] == "cultural-term-efficacy"
    assert manifest["mode"] == "dry_run"
    assert manifest["provider_execution"] == "disabled"
    assert manifest["project"]["slug"] == "premium-tea-packaging"
    assert [condition["id"] for condition in manifest["conditions"]] == [
        "A",
        "B",
        "C",
        "D",
    ]
    assert {provider["execution"] for provider in manifest["providers"]} == {
        "not_run"
    }

    human_ranking = json.loads(
        (out_dir / "human_ranking.json").read_text(encoding="utf-8")
    )
    provider_costs = json.loads(
        (out_dir / "provider_costs.json").read_text(encoding="utf-8")
    )
    assert human_ranking["status"] == "not_collected"
    assert provider_costs["status"] == "not_collected"
    assert "No image quality conclusion" in (
        out_dir / "summary.md"
    ).read_text(encoding="utf-8")


def test_real_provider_execution_fails_closed():
    from scripts.visual_discovery_benchmark import run_real_provider_experiment

    with pytest.raises(RuntimeError, match="explicit opt-in"):
        run_real_provider_experiment(real_provider=False)


def test_harness_forces_litellm_local_cost_map(monkeypatch):
    import scripts.visual_discovery_benchmark as benchmark

    monkeypatch.delenv("LITELLM_LOCAL_MODEL_COST_MAP", raising=False)
    importlib.reload(benchmark)

    assert os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] == "true"
