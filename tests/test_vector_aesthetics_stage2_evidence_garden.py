from __future__ import annotations

import json
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
BRIEF = REPO_ROOT / "docs" / "product" / "experiments" / "3d-vector-aesthetic-stage-02-evidence-garden.md"
PROMPTS = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-evidence-garden-prompts.json"
)
CANDIDATE_HTML = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-candidates"
    / "index.html"
)


def test_evidence_garden_direction_brief_locks_selected_working_direction():
    text = BRIEF.read_text(encoding="utf-8")

    assert BRIEF.is_file()
    assert "Selected working direction for Stage 02." in text
    assert "Evidence Garden is now anchored on the Glass Root Specimen branch" in text
    assert "quiet museum object" in text
    assert "not text-led" in text
    assert "3D generation tool" in text
    assert "Do not generate the full web scene" in text
    assert "procedural Three.js preview" in text
    assert "3d-vector-aesthetic-stage-02-suspended-root-lens-preview/index.html" in text
    assert "Current Recommendation" in text


def test_evidence_garden_direction_brief_defines_four_page_states():
    text = BRIEF.read_text(encoding="utf-8")

    for state in [
        "Dormant Island",
        "Root Scan",
        "Data Bloom",
        "Archive Constellation",
    ]:
        assert state in text

    for rejected in ["Depth Typography Poster", "VECTOR"]:
        assert rejected not in text
    assert "not fantasy terrain, dashboard UI, product perfume bottle, or text poster" in text


def test_evidence_garden_prompt_pack_is_structured_for_model_generation():
    payload = json.loads(PROMPTS.read_text(encoding="utf-8"))

    assert payload["direction_id"] == "stage-02-evidence-garden"
    assert payload["status"] == "selected_working_direction"
    assert payload["selected_model_candidate_id"] == "glass-root-specimen"
    assert payload["asset_target"]["format"] == "glb"
    assert payload["asset_target"]["subject"] == "single centered 3D glass root specimen object"
    base_prompt = payload["base_prompt"].lower()
    assert "single centered 3d" in base_prompt
    assert "glass root specimen" in base_prompt
    assert "export as glb" in base_prompt
    assert len(payload["state_requirements"]) == 4

    for forbidden in ["text", "logo", "characters", "mascot", "dashboard UI"]:
        assert forbidden in payload["asset_target"]["do_not_generate"]
        assert forbidden in payload["negative_prompt"]

    assert {"spline_ai", "tripo", "meshy", "image_to_3d_seed"} == set(payload["tool_prompts"])


def test_candidate_page_marks_evidence_garden_as_selected_direction():
    html_text = CANDIDATE_HTML.read_text(encoding="utf-8")
    match = re.search(r"const CANDIDATES = (\[.*?\]);", html_text, re.S)
    assert match, "candidate data block missing"
    candidates = json.loads(match.group(1))

    selected = [candidate for candidate in candidates if candidate.get("status") == "selected_working_direction"]
    assert len(selected) == 1
    assert selected[0]["id"] == "evidence-garden"
    assert 'status": "selected_working_direction"' in html_text
    assert 'status.replaceAll("_", " ")' in html_text
