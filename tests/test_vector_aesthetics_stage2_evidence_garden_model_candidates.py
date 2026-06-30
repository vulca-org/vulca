from __future__ import annotations

import json
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATES_JSON = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-evidence-garden-model-candidates.json"
)
MODEL_LAB = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-evidence-garden-model-lab"
    / "index.html"
)
SMOKE = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-evidence-garden-smoke"
    / "index.html"
)


def test_model_candidate_pack_defines_three_external_generation_candidates():
    payload = json.loads(CANDIDATES_JSON.read_text(encoding="utf-8"))

    assert payload["direction_id"] == "stage-02-evidence-garden"
    assert payload["status"] == "ready_for_external_3d_generation"
    assert payload["source_baseline"]["visual_gate"] == "failed"
    assert "Never treat one generated model as final" in payload["iteration_rule"]

    candidates = payload["candidates"]
    assert [candidate["id"] for candidate in candidates] == [
        "mineral-root-island",
        "glass-root-specimen",
        "technical-data-island",
    ]


def test_model_candidate_pack_enforces_spatial_contracts_and_negative_prompts():
    payload = json.loads(CANDIDATES_JSON.read_text(encoding="utf-8"))

    for candidate in payload["candidates"]:
        prompt = candidate["model_prompt"].lower()
        negative = candidate["negative_prompt"].lower()
        contract = candidate["spatial_contract"]
        assert "single centered" in prompt
        assert "glb-ready" in prompt
        assert "no text" in prompt
        assert "no logo" in prompt
        assert "no mascot" in prompt
        assert "no text" in negative
        assert "no logo" in negative
        assert {"primary_mass", "root_logic", "route_logic", "blossom_logic", "state_anchors"} == set(contract)
        assert "socket" in contract["root_logic"] or "port" in contract["root_logic"] or "contained" in contract["root_logic"]


def test_model_candidate_lab_is_self_contained_and_renders_candidate_previews():
    html_text = MODEL_LAB.read_text(encoding="utf-8")
    lowered = html_text.lower()

    assert MODEL_LAB.is_file()
    assert 'data-vector-stage-product="2026-06-stage-02-evidence-garden-model-lab"' in html_text
    assert "__EVIDENCE_GARDEN_MODEL_CANDIDATES__" in html_text
    assert '<canvas id="previewCanvas"' in html_text
    assert "drawMineralRootIsland" in html_text
    assert "drawGlassRootSpecimen" in html_text
    assert "drawTechnicalDataIsland" in html_text
    assert "one-shot output is only a seed" in html_text
    for banned in ["<iframe", "http://", "https://", "src=", 'href="http']:
        assert banned not in lowered


def test_model_candidate_lab_inline_candidates_match_pack_ids():
    html_text = MODEL_LAB.read_text(encoding="utf-8")
    match = re.search(r"const CANDIDATES = \[(.*?)\];", html_text, re.S)
    assert match, "inline candidate data missing"
    inline_ids = re.findall(r'id: "([^"]+)"', match.group(1))
    payload = json.loads(CANDIDATES_JSON.read_text(encoding="utf-8"))

    assert inline_ids == [candidate["id"] for candidate in payload["candidates"]]


def test_smoke_page_is_marked_as_failed_visual_baseline():
    html_text = SMOKE.read_text(encoding="utf-8")

    assert "visual gate is failed" in html_text
    assert "failed baseline" in html_text
    assert "replaceable GLB loading fixture" in html_text
