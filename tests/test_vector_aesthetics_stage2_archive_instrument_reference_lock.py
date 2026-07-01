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
    / "3d-vector-aesthetic-stage-02-archive-instrument-reference-lock.json"
)
REFERENCE_HTML = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-archive-instrument-reference-lock"
    / "index.html"
)

EXPECTED_REFERENCE_IDS = [
    "archive-instrument-current-prototype",
    "natural-history-museum-spirit-collection",
    "apple-vision-pro-formed-glass",
    "zeiss-microscopy-instrument-system",
    "iyo-webgl-exploded-view",
    "webgpu-scanning-depth-maps",
    "spline-ai-single-object-rule",
    "codrops-meshline-family",
]
EXPECTED_VISUAL_CRITERIA = [
    "The specimen reads as a real object before reading as a diagram.",
    "The glass reads as a vitrine or wet-specimen container, not a transparent UI shell.",
    "The root and support geometry cannot be mistaken for legs or random lines.",
    "Each scroll state changes inspection logic, not just position or opacity.",
    "The palette has warm material contrast and does not collapse into gray-green technical UI.",
]
EXPECTED_STILL_WEAK = [
    "real-world specimen fidelity",
    "glass thickness",
    "bottom support readability",
    "reference-level lighting",
    "lack of high-quality model or texture assets",
]
EXPECTED_NEXT_PASS_MOVES = [
    "replace or supplement procedural plant geometry with a better modeled or generated specimen asset",
    "rebuild glass as a believable thick container with edge highlights and refraction cues",
    "define one strong hero camera and only modest scroll-state camera changes",
    "reduce annotation density and make scan/section states behave like instrument modes",
    "add screenshot-based browser review checkpoints for mobile and desktop",
]
EXPECTED_LOCAL_PROTOTYPE_CARD_HREF = (
    "../3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html"
)
ALLOWED_REFERENCE_PAIRS = {
    ("local_prototype", "baseline"),
    ("museum_science_reference", "specimen"),
    ("product_material_reference", "glass"),
    ("scientific_instrument_reference", "instrument"),
    ("external_inspiration", "sectioning"),
    ("shader_demo_reference", "scanning"),
    ("tool_documentation", "asset_pipeline"),
    ("creative_coding_family", "root_routes"),
}
REQUIRED_REFERENCE_FIELDS = {
    "id",
    "label",
    "source_kind",
    "url",
    "dimension",
    "borrow",
    "do_not_copy",
    "quality_line",
    "confidence",
}


def _payload() -> dict:
    assert REFERENCE_JSON.is_file()
    return json.loads(REFERENCE_JSON.read_text(encoding="utf-8"))


def test_stage02_archive_instrument_reference_lock_json_contract():
    payload = _payload()

    assert payload["lock_id"] == "stage-02-archive-instrument-reference-lock"
    assert payload["status"] == "reference_lock_before_next_archive_instrument_pass"
    assert payload["created"] == "2026-07-01"
    assert payload["selected_direction"] == "realistic specimen plus luxury scientific instrument"
    assert (
        payload["direction_statement"]
        == "Archive Instrument = realistic preserved specimen + luxury instrument object + restrained scientific inspection."
    )
    assert (
        payload["prototype_path"]
        == "docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html"
    )
    assert (
        payload["reference_board_path"]
        == "docs/product/experiments/3d-vector-aesthetic-stage-02-reference-board/index.html"
    )
    assert (
        payload["reference_discovery_path"]
        == "docs/product/experiments/3d-vector-aesthetic-stage-02-reference-discovery.md"
    )


def test_stage02_archive_instrument_reference_lock_references_are_bounded():
    payload = _payload()
    references = payload["references"]

    assert [item["id"] for item in references] == EXPECTED_REFERENCE_IDS
    for item in references:
        assert REQUIRED_REFERENCE_FIELDS <= set(item)
        assert (item["source_kind"], item["dimension"]) in ALLOWED_REFERENCE_PAIRS
        assert item["do_not_copy"].startswith("Do not")
        assert item["confidence"] in {"high", "medium", "low"}


def test_stage02_archive_instrument_reference_lock_diagnosis_and_next_moves():
    payload = _payload()

    assert payload["current_diagnosis"]["improved"] == [
        "central object",
        "warmer materiality",
        "four-state logic",
        "less abstract roots",
    ]
    assert payload["current_diagnosis"]["still_weak"] == EXPECTED_STILL_WEAK
    assert payload["current_diagnosis"]["risk"].startswith(
        "continuing to polish procedural shapes"
    )
    assert payload["visual_criteria"] == EXPECTED_VISUAL_CRITERIA
    assert payload["next_pass_moves"] == EXPECTED_NEXT_PASS_MOVES


def test_stage02_archive_instrument_reference_lock_html_is_reviewable():
    assert REFERENCE_HTML.is_file()
    html_text = REFERENCE_HTML.read_text(encoding="utf-8")

    assert (
        'data-vector-stage-product="2026-07-stage-02-archive-instrument-reference-lock"'
        in html_text
    )
    assert "<title>Archive Instrument Reference Lock</title>" in html_text
    assert "window.__ARCHIVE_INSTRUMENT_REFERENCE_LOCK__" in html_text
    assert "referenceCount: REFERENCE_LOCK.references.length" in html_text
    assert "criteriaCount: REFERENCE_LOCK.visual_criteria.length" in html_text
    assert 'direction: "archive-instrument"' in html_text
    assert "Archive Instrument = realistic preserved specimen" in html_text
    assert "Direction is locked; execution quality is not." in html_text
    assert "Reference Matrix" in html_text
    assert "Current Prototype Diagnosis" in html_text
    assert "Visual Criteria For Next Pass" in html_text
    assert "Next-Pass Moves" in html_text
    assert (
        "../3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html"
        in html_text
    )
    assert "../3d-vector-aesthetic-stage-02-reference-board/index.html" in html_text
    assert "../3d-vector-aesthetic-stage-02-reference-discovery.md" in html_text


def test_stage02_archive_instrument_reference_lock_inline_data_matches_json():
    payload = _payload()
    html_text = REFERENCE_HTML.read_text(encoding="utf-8")
    html_block = re.search(r"const REFERENCE_LOCK = (\{.*?\});", html_text, re.S)

    assert html_block, "inline reference lock data missing"
    inline_payload = json.loads(html_block.group(1))
    assert inline_payload == payload
    assert [item["id"] for item in inline_payload["references"]] == EXPECTED_REFERENCE_IDS
    assert inline_payload["references"] == payload["references"]
    assert inline_payload["visual_criteria"] == EXPECTED_VISUAL_CRITERIA
    assert inline_payload["next_pass_moves"] == EXPECTED_NEXT_PASS_MOVES
    assert inline_payload["current_diagnosis"]["still_weak"] == EXPECTED_STILL_WEAK
    assert (
        inline_payload["current_diagnosis"]["risk"]
        == payload["current_diagnosis"]["risk"]
    )
    assert payload["current_diagnosis"]["risk"] in html_block.group(1)
    for value in payload["visual_criteria"]:
        assert value in html_block.group(1)
    for value in payload["next_pass_moves"]:
        assert value in html_block.group(1)
    for item in payload["references"]:
        assert item["id"] in html_block.group(1)
        assert item["label"] in html_block.group(1)
        assert item["borrow"] in html_block.group(1)
        assert item["do_not_copy"] in html_block.group(1)
        assert item["label"] in html_text
        assert item["borrow"] in html_text
        assert item["do_not_copy"] in html_text


def test_stage02_archive_instrument_reference_lock_local_card_href_resolves():
    payload = _payload()
    html_text = REFERENCE_HTML.read_text(encoding="utf-8")
    local_reference = next(
        item for item in payload["references"] if item["source_kind"] == "local_prototype"
    )

    assert (
        local_reference["url"]
        == "docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html"
    )
    assert f'return "{EXPECTED_LOCAL_PROTOTYPE_CARD_HREF}";' in html_text
    assert "source.href = referenceHref(item);" in html_text
    assert "source.href = item.url;" not in html_text
    assert (
        REFERENCE_HTML.parent / EXPECTED_LOCAL_PROTOTYPE_CARD_HREF
    ).resolve().is_file()
