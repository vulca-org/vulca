from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_build_conditions_a_through_f():
    from scripts.visual_discovery_benchmark import build_conditions
    from vulca.discovery.cards import generate_direction_cards
    from vulca.discovery.profile import infer_taste_profile

    profile = infer_taste_profile(
        slug="tea",
        intent="premium tea packaging with ink atmosphere and liu bai",
    )
    card = generate_direction_cards(profile, count=1)[0]

    conditions = build_conditions(profile.initial_intent, card)

    assert [condition["id"] for condition in conditions] == [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
    ]
    assert "raw cultural" in conditions[1]["label"].lower()
    assert card.id in conditions[-1]["source_card_id"]


def test_dry_run_report_contains_provider_matrix(tmp_path):
    from scripts.visual_discovery_benchmark import write_dry_run_report

    report = write_dry_run_report(tmp_path / "report.md")

    assert "OpenAI GPT Image 2" in report
    assert "Gemini / Nano Banana" in report
    assert "ComfyUI" in report
    assert (tmp_path / "report.md").exists()
