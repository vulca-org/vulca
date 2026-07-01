from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[1]
SPECIMEN_JSON = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01.json"
)
SPECIMEN_HTML = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-archive-instrument-specimen-asset-pass-01"
    / "index.html"
)
CURRENT_PROTOTYPE = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-archive-instrument-prototype"
    / "index.html"
)
CURRENT_PROTOTYPE_RELATIVE = (
    "docs/product/experiments/"
    "3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html"
)
CURRENT_PROTOTYPE_HREF = (
    "../3d-vector-aesthetic-stage-02-archive-instrument-prototype/index.html"
)
REFERENCE_LOCK_HREF = (
    "../3d-vector-aesthetic-stage-02-archive-instrument-reference-lock/index.html"
)
THREE_IMPORT = "https://unpkg.com/three@0.165.0/build/three.module.js"

EXPECTED_PAYLOAD = {
    "candidate_id": "stage-02-archive-instrument-specimen-asset-pass-01",
    "status": "specimen_asset_candidate_before_prototype_merge",
    "created": "2026-07-01",
    "direction": "realistic preserved specimen plus luxury scientific instrument",
    "goal": "Does the central specimen read as a preserved real object before it reads as a diagram?",
    "current_prototype_path": CURRENT_PROTOTYPE_RELATIVE,
    "reference_lock_path": "docs/product/experiments/3d-vector-aesthetic-stage-02-archive-instrument-reference-lock/index.html",
    "recommended_approach": "separate procedural specimen candidate",
    "explicit_non_goal": "do not modify the current Archive Instrument prototype in this pass",
    "required_anatomy_parts": [
        "woody stem",
        "leaf cluster",
        "petiole",
        "root crown",
        "fine roots",
        "mounting wire",
    ],
    "candidate_traits": [
        "asymmetric woody stem with taper, knots, scars, and bark rings",
        "5 to 7 leaves with varied size, age, bend, pitch, and yaw",
        "petioles visibly attach leaves to the stem",
        "root crown or soil plug with roots emerging from believable sockets",
        "short branching fine roots and root hairs",
        "mounting wires read as specimen support, not legs",
        "warm brown, olive, pale vein, and amber material accents",
    ],
    "first_read": "preserved organic sample",
    "not_read_as": ["plant icon", "wireframe diagram", "random tubes", "technical toy"],
    "visual_criteria": [
        "The specimen reads as a real object before reading as a diagram.",
        "The glass reads as a vitrine or wet-specimen container, not a transparent UI shell.",
        "The root and support geometry cannot be mistaken for legs or random lines.",
        "Each scroll state changes inspection logic, not just position or opacity.",
        "The palette has warm material contrast and does not collapse into gray-green technical UI.",
    ],
    "secondary_success_criteria": [
        "roots no longer read as legs",
        "leaves have credible attachment and orientation",
        "root crown feels physically connected to the stem",
        "material palette is warmer and less gray-green",
        "the candidate can be moved into the current prototype without changing the direction",
    ],
    "handoff_notes": [
        "accepted: merge candidate anatomy into the main Archive Instrument prototype",
        "still weak: move to generated GLB or modeled-asset exploration",
        "glass/instrument/scroll-state changes remain later passes",
    ],
}


def _payload() -> dict:
    assert SPECIMEN_JSON.is_file()
    return json.loads(SPECIMEN_JSON.read_text(encoding="utf-8"))


def _html() -> str:
    assert SPECIMEN_HTML.is_file()
    return SPECIMEN_HTML.read_text(encoding="utf-8")


def test_stage02_archive_instrument_specimen_asset_pass01_json_contract():
    payload = _payload()

    assert payload == EXPECTED_PAYLOAD


def test_stage02_archive_instrument_specimen_asset_pass01_files_and_prototype_state():
    assert SPECIMEN_HTML.is_file()
    assert CURRENT_PROTOTYPE.is_file()

    prototype_status = subprocess.run(
        ["git", "status", "--porcelain", "--", CURRENT_PROTOTYPE_RELATIVE],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert prototype_status.stdout == ""


def test_stage02_archive_instrument_specimen_asset_pass01_html_review_contract():
    html_text = _html()

    assert (
        'data-vector-stage-product="2026-07-stage-02-archive-instrument-specimen-asset-pass-01"'
        in html_text
    )
    assert "<title>Archive Instrument Specimen Asset Pass 01</title>" in html_text
    assert "window.__ARCHIVE_SPECIMEN_ASSET_PASS_01__" in html_text
    assert "Specimen Asset Pass 01" in html_text
    assert EXPECTED_PAYLOAD["goal"] in html_text
    assert CURRENT_PROTOTYPE_HREF in html_text
    assert REFERENCE_LOCK_HREF in html_text
    assert "referenceCount" not in html_text


def test_stage02_archive_instrument_specimen_asset_pass01_threejs_specimen_contract():
    html_text = _html()

    assert html_text.count(THREE_IMPORT) == 1
    assert 'import * as THREE from "https://unpkg.com/three@0.165.0/build/three.module.js"' in html_text
    assert "new THREE.WebGLRenderer" in html_text
    assert "preserveDrawingBuffer: true" in html_text
    for function_name in [
        "createSpecimenCandidate",
        "createLeafBlade",
        "createFineRoots",
        "createMountingWires",
    ]:
        assert f"function {function_name}" in html_text
    assert "candidateId: SPECIMEN_PASS.candidate_id" in html_text
    assert "anatomyCount: SPECIMEN_PASS.required_anatomy_parts.length" in html_text
    assert "criteriaCount: SPECIMEN_PASS.visual_criteria.length" in html_text


def test_stage02_archive_instrument_specimen_asset_pass01_inline_data_matches_json():
    payload = _payload()
    html_text = _html()
    html_block = re.search(r"const SPECIMEN_PASS = (\{.*?\});", html_text, re.S)

    assert html_block, "inline specimen pass data missing"
    inline_payload = json.loads(html_block.group(1))
    assert inline_payload == payload
    assert inline_payload == EXPECTED_PAYLOAD

    required_visible_values = [
        *payload["required_anatomy_parts"],
        *payload["visual_criteria"],
        *payload["secondary_success_criteria"],
        *payload["not_read_as"],
        *payload["handoff_notes"],
    ]
    for value in required_visible_values:
        assert value in html_text
        assert value in html_block.group(1)
