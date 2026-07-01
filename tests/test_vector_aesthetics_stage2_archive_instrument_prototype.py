from __future__ import annotations

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOTYPE = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-archive-instrument-prototype"
    / "index.html"
)


def test_archive_instrument_prototype_is_reference_driven_threejs_stage():
    html_text = PROTOTYPE.read_text(encoding="utf-8")

    assert PROTOTYPE.is_file()
    assert 'data-vector-stage-product="2026-07-stage-02-archive-instrument-prototype"' in html_text
    assert '<canvas id="instrumentCanvas"' in html_text
    assert 'import * as THREE from "https://unpkg.com/three@0.165.0/build/three.module.js"' in html_text
    assert "new THREE.WebGLRenderer" in html_text
    assert "preserveDrawingBuffer: true" in html_text
    assert "window.__ARCHIVE_INSTRUMENT_PROTOTYPE__" in html_text
    assert "threejs-reference-driven-prototype" in html_text
    assert "stage-02-central-scroll-object-reference-board" in html_text


def test_archive_instrument_prototype_locks_reference_sources_and_layers():
    html_text = PROTOTYPE.read_text(encoding="utf-8")

    for reference_id in [
        "iyo-webgl-exploded-view",
        "webgpu-scanning-depth-maps",
        "spline-ai-single-object-rule",
    ]:
        assert reference_id in html_text

    for layer in ["frame", "shell", "membrane", "core", "roots", "signals", "scan", "trace-particles"]:
        assert f'"{layer}"' in html_text

    for fn_name in [
        "createArchiveFrameLayer",
        "createCapsuleLayer",
        "createMembraneLayer",
        "createCoreLayer",
        "createRootRouteLayer",
        "createSignalLayer",
        "createScanLayer",
        "createTraceParticles",
        "applyLayerSeparation",
        "updateTraceParticles",
    ]:
        assert f"function {fn_name}" in html_text


def test_archive_instrument_prototype_has_four_state_hierarchy_not_random_demo():
    html_text = PROTOTYPE.read_text(encoding="utf-8")
    state_ids = re.findall(r'id: "(sealed_archive|membrane_scan|layer_separation|trace_constellation)"', html_text)

    assert state_ids == [
        "sealed_archive",
        "membrane_scan",
        "layer_separation",
        "trace_constellation",
    ]
    for title in ["Preserve", "Scan", "Section", "Annotate"]:
        assert title in html_text
    for logic in [
        "sealed specimen at rest",
        "surface scan reveals leaf orientation and condensation",
        "section view separates the physical layers",
        "evidence pins attach to inspected features",
    ]:
        assert logic in html_text
    for motion_param in ["specimenTurn", "leafOpen", "leaf-cluster", "baseRotation", "openBias"]:
        assert motion_param in html_text
    for specimen_detail in [
        "museum-rear-backdrop",
        "specimen-contact-shadow",
        "preserving-fluid-depth",
        "specimen-mount-wire",
    ]:
        assert specimen_detail in html_text
    assert "random tubes" not in html_text.lower()
    assert "poster" not in html_text.lower()
    assert "<button" not in html_text.lower()


def test_archive_instrument_prototype_has_mobile_and_canvas_guards():
    html_text = PROTOTYPE.read_text(encoding="utf-8")

    assert "root.scale.setScalar(width < 700 ? 0.74 : 0.98);" in html_text
    assert "@media (max-width: 820px)" in html_text
    assert ".state-rail,\n      .quality-tag {\n        display: none;\n      }" in html_text
    assert "min-height: 430vh;" in html_text
    assert "window.scrollY" in html_text
