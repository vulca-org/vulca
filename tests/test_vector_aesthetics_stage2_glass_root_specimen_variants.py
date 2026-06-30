from __future__ import annotations

import json
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
VARIANTS_JSON = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-glass-root-specimen-variants.json"
)
VARIANT_LAB = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-glass-root-specimen-variants"
    / "index.html"
)
PROMPTS = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-evidence-garden-prompts.json"
)


def test_glass_root_specimen_variant_pack_selects_suspended_root_lens():
    payload = json.loads(VARIANTS_JSON.read_text(encoding="utf-8"))

    assert payload["model_candidate_id"] == "glass-root-specimen"
    assert payload["status"] == "variant_prompt_pack_ready"
    assert payload["selected_variant_id"] == "suspended-root-lens"
    assert "Never one-shot accept" in payload["iteration_rule"]
    assert len(payload["variants"]) == 3
    assert [variant["id"] for variant in payload["variants"]] == [
        "suspended-root-lens",
        "oval-archive-vessel",
        "core-reliquary",
    ]


def test_glass_root_specimen_variants_have_generation_guards_and_asset_slots():
    payload = json.loads(VARIANTS_JSON.read_text(encoding="utf-8"))

    assert len(payload["asset_slots"]) == 3
    for slot in payload["asset_slots"]:
        assert slot["expected_glb_path"].endswith(".glb")
        assert "assets/generated/glass-root-specimen-" in slot["expected_glb_path"]

    for variant in payload["variants"]:
        prompt = variant["model_prompt"].lower()
        reject_text = " ".join(variant["reject_if"]).lower()
        assert "single centered" in prompt
        assert "glb-ready" in prompt
        assert "no text" in prompt
        assert "no logo" in prompt
        assert "no characters" in prompt
        assert {"glass_shell", "core", "roots", "signals", "buds"} == set(variant["spatial_contract"])
        assert "glass" in variant["spatial_contract"]["glass_shell"]
        assert "root" in variant["spatial_contract"]["roots"]
        assert "bottle" in payload["shared_negative_prompt"].lower()
        assert "pierc" in payload["shared_negative_prompt"].lower()
        assert any(term in reject_text for term in ["bottle", "pierce", "religious", "contact lens case"])


def test_glass_root_specimen_variant_lab_is_self_contained_visual_review_page():
    html_text = VARIANT_LAB.read_text(encoding="utf-8")
    lowered = html_text.lower()

    assert VARIANT_LAB.is_file()
    assert 'data-vector-stage-product="2026-06-stage-02-glass-root-specimen-variant-lab"' in html_text
    assert "__GLASS_ROOT_SPECIMEN_VARIANTS__" in html_text
    assert '<canvas id="variantCanvas"' in html_text
    assert "drawSuspendedRootLens" in html_text
    assert "drawOvalArchiveVessel" in html_text
    assert "drawCoreReliquary" in html_text
    assert "Current first try: Suspended Root Lens" in html_text
    for banned in ["<iframe", "http://", "https://", "src=", 'href="http']:
        assert banned not in lowered


def test_glass_root_specimen_variant_lab_keeps_center_stage_in_first_viewport():
    html_text = VARIANT_LAB.read_text(encoding="utf-8")

    assert "height: 100dvh;" in html_text
    assert "grid-template-columns: minmax(280px, 340px) minmax(520px, 1fr) minmax(300px, 340px);" in html_text
    assert ".stage" in html_text
    assert "height: 100%;" in html_text
    assert "min-height: 0;" in html_text


def test_variant_lab_inline_ids_match_variant_pack():
    html_text = VARIANT_LAB.read_text(encoding="utf-8")
    match = re.search(r"const VARIANTS = \[(.*?)\];", html_text, re.S)
    assert match, "inline variant data missing"
    inline_ids = re.findall(r'id: "([^"]+)"', match.group(1))
    payload = json.loads(VARIANTS_JSON.read_text(encoding="utf-8"))

    assert inline_ids == [variant["id"] for variant in payload["variants"]]


def test_evidence_garden_prompt_pack_points_to_selected_variant():
    payload = json.loads(PROMPTS.read_text(encoding="utf-8"))

    assert payload["selected_model_candidate_id"] == "glass-root-specimen"
    assert payload["selected_model_variant_id"] == "suspended-root-lens"
