from __future__ import annotations

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
PREVIEW = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-suspended-root-lens-preview"
    / "index.html"
)


def test_suspended_root_lens_preview_is_threejs_visual_stage():
    html_text = PREVIEW.read_text(encoding="utf-8")

    assert PREVIEW.is_file()
    assert 'data-vector-stage-product="2026-06-stage-02-suspended-root-lens-preview"' in html_text
    assert '<canvas id="webglStage"' in html_text
    assert 'import * as THREE from "https://unpkg.com/three@0.165.0/build/three.module.js"' in html_text
    assert "new THREE.WebGLRenderer" in html_text
    assert "window.__SUSPENDED_ROOT_LENS_PREVIEW__" in html_text
    assert "threejs-procedural-preview" in html_text


def test_suspended_root_lens_preview_keeps_object_as_primary_surface():
    html_text = PREVIEW.read_text(encoding="utf-8")
    lowered = html_text.lower()

    assert ".stage" in html_text
    assert "position: fixed;" in html_text
    assert "inset: 0;" in html_text
    assert "Suspended Root Lens" in html_text
    assert "Procedural Three.js preview" in html_text
    assert "<model-viewer" not in lowered
    assert "<button" not in lowered
    assert "dashboard" not in lowered
    assert "poster" not in lowered
    assert "font-size: clamp(20px, 2.2vw, 30px);" in html_text
    assert "@media (max-width: 820px)" in html_text
    assert ".state-rail {\n        display: none;\n      }" in html_text


def test_suspended_root_lens_preview_models_selected_variant_parts():
    html_text = PREVIEW.read_text(encoding="utf-8")

    for fn_name in [
        "createLensShell",
        "createMineralCore",
        "createRootSystem",
        "createBuds",
        "createScanPlane",
        "createArchiveParticles",
        "readScrollProgress",
        "updateStateVisuals",
    ]:
        assert f"function {fn_name}" in html_text

    for term in [
        "variantId: \"suspended-root-lens\"",
        "selectedModelCandidateId: \"glass-root-specimen\"",
        "glass containment",
        "root logic",
    ]:
        assert term in html_text


def test_suspended_root_lens_preview_guards_against_root_piercing_and_blank_canvas():
    html_text = PREVIEW.read_text(encoding="utf-8")

    assert "preserveDrawingBuffer: true" in html_text
    assert "root.scale.setScalar(width < 700 ? 0.32 : 1);" in html_text
    assert "[-0.78, 0.28, -0.12]" in html_text
    assert "[0.96, 0.24, -0.1]" in html_text
    assert "0.98" not in html_text
    assert "0.92" not in html_text


def test_suspended_root_lens_preview_has_four_scroll_states():
    html_text = PREVIEW.read_text(encoding="utf-8")
    state_ids = re.findall(r'id: "(dormant_specimen|root_scan|data_bloom|archive_constellation)"', html_text)

    assert state_ids == [
        "dormant_specimen",
        "root_scan",
        "data_bloom",
        "archive_constellation",
    ]
    for title in ["Dormant Specimen", "Root Scan", "Data Bloom", "Archive Constellation"]:
        assert title in html_text
    assert "min-height: 420vh;" in html_text
    assert "window.scrollY" in html_text
