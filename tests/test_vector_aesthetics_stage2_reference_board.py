from __future__ import annotations

import json
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_JSON = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-reference-board.json"
)
REFERENCE_HTML = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-reference-board"
    / "index.html"
)


def test_stage02_reference_board_json_defines_reference_gate():
    payload = json.loads(REFERENCE_JSON.read_text(encoding="utf-8"))

    assert payload["board_id"] == "stage-02-central-scroll-object-reference-board"
    assert payload["status"] == "reference_gate_before_next_visual_iteration"
    assert "technically stable but visually weak" in payload["diagnosis"]
    assert payload["decision"]["reject"].startswith("continuing to polish")
    assert payload["decision"]["selected_card_id"] == "archive-instrument"
    assert payload["decision"]["selected_prototype"].endswith(
        "3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html"
    )
    assert len(payload["references"]) == 8
    assert len(payload["recommended_cards"]) == 3
    assert payload["next_recommendation"].startswith("Do not continue polishing")


def test_stage02_reference_board_cases_have_translation_commands():
    payload = json.loads(REFERENCE_JSON.read_text(encoding="utf-8"))
    ids = [item["id"] for item in payload["references"]]

    assert ids == [
        "codrops-scroll-driven-3d-world",
        "weleda-open-garden",
        "iyo-webgl-exploded-view",
        "spline-ai-single-object-rule",
        "false-earth-webgpu-world",
        "webgpu-scanning-depth-maps",
        "matrix-sentinels-particle-trails-tsl",
        "codrops-meshline-family",
    ]
    for item in payload["references"]:
        assert item["url"].startswith("https://")
        assert item["shape_language"]
        assert item["material_language"]
        assert item["state_language"]
        assert item["current_preview_gap"]
        assert item["translation_command"]
        assert item["avoid"].startswith("Do not")


def test_stage02_reference_board_html_is_reviewable_and_source_grounded():
    html_text = REFERENCE_HTML.read_text(encoding="utf-8")

    assert REFERENCE_HTML.is_file()
    assert 'data-vector-stage-product="2026-07-stage-02-reference-board"' in html_text
    assert "window.__STAGE02_REFERENCE_BOARD__" in html_text
    assert "referenceCount: REFERENCE_CARDS.length" in html_text
    assert "directionCount: DIRECTION_CARDS.length" in html_text
    assert "Archive Instrument" in html_text
    assert "Living Specimen" in html_text
    assert "Contained World" in html_text
    assert "No more polishing the procedural object" not in html_text
    assert "no more polishing the procedural object" in html_text


def test_stage02_reference_board_inline_ids_match_json():
    html_text = REFERENCE_HTML.read_text(encoding="utf-8")
    payload = json.loads(REFERENCE_JSON.read_text(encoding="utf-8"))
    html_block = re.search(r"const REFERENCE_CARDS = \[(.*?)\];", html_text, re.S)
    assert html_block, "inline reference cards missing"
    html_ids = re.findall(r'^\s+id: "([^"]+)"', html_block.group(1), re.M)

    assert html_ids == [item["id"] for item in payload["references"]]
    for card in payload["recommended_cards"]:
        assert card["id"] in html_text
        assert card["label"] in html_text
