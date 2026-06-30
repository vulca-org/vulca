from __future__ import annotations

import json
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_checked_in_gold_cases_are_multimodal_and_learning_ready(tmp_path: Path):
    from vulca.vector_aesthetics.compiler import compile_database, export_review_json_from_sqlite

    root = REPO_ROOT / "data" / "vector-aesthetics"
    sqlite_path = tmp_path / "references.sqlite"
    output_path = tmp_path / "references.json"

    compile_database(root, sqlite_path)
    export_review_json_from_sqlite(sqlite_path, output_path)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    cases = {case["id"]: case for case in payload["cases"]}
    makio = cases["makio-meshline"]
    text_destruction = cases["interactive-text-destruction-webgpu-tsl"]
    scanning_depth = cases["webgpu-scanning-depth-maps"]
    phantom_grid = cases["phantom-land-interactive-grid"]
    gommage = cases["webgpu-gommage-msdf-dissolve"]
    codrops_meshline = cases["codrops-threejs-meshline-family"]
    false_earth = cases["false-earth-webgpu-world"]
    matrix_sentinels = cases["matrix-sentinels-particle-trails-tsl"]
    spline_ui = cases["spline-contemporary-3d-web"]

    assert payload["summary"]["gold_case_count"] == 9
    assert payload["summary"]["multimodal_complete_count"] == 9
    for case in [
        makio,
        text_destruction,
        scanning_depth,
        phantom_grid,
        gommage,
        codrops_meshline,
        false_earth,
        matrix_sentinels,
        spline_ui,
    ]:
        assert case["coverage"]["screenshots"] == "complete"
        assert case["coverage"]["video"] == "complete"
        assert case["coverage"]["code_anatomy"] == "complete"
        assert case["coverage"]["lesson"] == "complete"
        assert case["coverage"]["vulca_translation"] == "complete"
        assert case["coverage"]["module_payloads"] == "complete"
        assert case["coverage"]["asset_manifest"] == "complete"
        assert case["data_quality_flags"] == []
        assert case["asset_manifest_status"] == "present_with_assets"
        assert any(
            capture["evidence_type"] == "screenshot" and capture["rights_status"] == "local_capture"
            for capture in case["captures"]
        )
        assert any(
            capture["evidence_type"] == "video" and capture["rights_status"] == "local_capture"
            for capture in case["captures"]
        )
        assert any(
            capture["evidence_type"] == "code_note" and capture["rights_status"] == "local_capture"
            for capture in case["captures"]
        )


def test_makio_meshline_gold_assets_are_bounded_and_self_contained():
    case_dir = REPO_ROOT / "data" / "vector-aesthetics" / "cases" / "makio-meshline"
    size_budgets = {
        "screenshots/minimal-rebuild-desktop.png": 200_000,
        "videos/minimal-rebuild-motion.gif": 2_000_000,
        "code/minimal-rebuild.html": 24_000,
    }

    for rel_path, max_bytes in size_budgets.items():
        asset_path = case_dir / rel_path
        assert asset_path.is_file()
        assert asset_path.stat().st_size <= max_bytes

    html_text = (case_dir / "code" / "minimal-rebuild.html").read_text(encoding="utf-8")
    lowered_html = html_text.lower()
    assert "<script" not in lowered_html
    assert "src=" not in lowered_html
    assert "href=" not in lowered_html
    assert "http://" not in html_text
    assert "https://" not in html_text
    assert 'role="img"' in html_text
    assert len(re.findall(r'<path class="route"', html_text)) == 3
    assert "animation: travel" in html_text


def test_interactive_text_destruction_gold_assets_are_bounded_and_self_contained():
    case_dir = REPO_ROOT / "data" / "vector-aesthetics" / "cases" / "interactive-text-destruction-webgpu-tsl"
    size_budgets = {
        "screenshots/minimal-rebuild-desktop.png": 240_000,
        "videos/minimal-rebuild-motion.gif": 2_400_000,
        "code/minimal-rebuild.html": 32_000,
    }

    for rel_path, max_bytes in size_budgets.items():
        asset_path = case_dir / rel_path
        assert asset_path.is_file()
        assert asset_path.stat().st_size <= max_bytes

    html_text = (case_dir / "code" / "minimal-rebuild.html").read_text(encoding="utf-8")
    lowered_html = html_text.lower()
    assert "<script" not in lowered_html
    assert "src=" not in lowered_html
    assert "href=" not in lowered_html
    assert "http://" not in html_text
    assert "https://" not in html_text
    assert 'role="img"' in html_text
    assert "data-word=\"VULCA\"" in html_text
    assert len(re.findall(r'class=\"fragment"', html_text)) >= 24
    assert "animation: drift" in html_text


def test_webgpu_scanning_depth_gold_assets_are_bounded_and_self_contained():
    case_dir = REPO_ROOT / "data" / "vector-aesthetics" / "cases" / "webgpu-scanning-depth-maps"
    size_budgets = {
        "screenshots/minimal-rebuild-desktop.png": 260_000,
        "videos/minimal-rebuild-motion.gif": 2_600_000,
        "code/minimal-rebuild.html": 34_000,
    }

    for rel_path, max_bytes in size_budgets.items():
        asset_path = case_dir / rel_path
        assert asset_path.is_file()
        assert asset_path.stat().st_size <= max_bytes

    html_text = (case_dir / "code" / "minimal-rebuild.html").read_text(encoding="utf-8")
    lowered_html = html_text.lower()
    assert "<script" not in lowered_html
    assert "src=" not in lowered_html
    assert "href=" not in lowered_html
    assert "http://" not in html_text
    assert "https://" not in html_text
    assert 'role="img"' in html_text
    assert len(re.findall(r'class=\"depth-dot', html_text)) >= 36
    assert "data-depth-map=\"generated\"" in html_text
    assert "animation: scan" in html_text


def test_phantom_land_grid_gold_assets_are_bounded_and_self_contained():
    case_dir = REPO_ROOT / "data" / "vector-aesthetics" / "cases" / "phantom-land-interactive-grid"
    size_budgets = {
        "screenshots/minimal-rebuild-desktop.png": 280_000,
        "videos/minimal-rebuild-motion.gif": 2_800_000,
        "code/minimal-rebuild.html": 38_000,
    }

    for rel_path, max_bytes in size_budgets.items():
        asset_path = case_dir / rel_path
        assert asset_path.is_file()
        assert asset_path.stat().st_size <= max_bytes

    html_text = (case_dir / "code" / "minimal-rebuild.html").read_text(encoding="utf-8")
    lowered_html = html_text.lower()
    assert "<script" not in lowered_html
    assert "src=" not in lowered_html
    assert "href=" not in lowered_html
    assert "http://" not in html_text
    assert "https://" not in html_text
    assert 'role="img"' in html_text
    assert 'data-grid-field="generated"' in html_text
    assert len(re.findall(r'class=\"grid-line', html_text)) >= 18
    assert len(re.findall(r'class=\"face-particle', html_text)) >= 36
    assert "animation: orbit" in html_text


def test_webgpu_gommage_gold_assets_are_bounded_and_self_contained():
    case_dir = REPO_ROOT / "data" / "vector-aesthetics" / "cases" / "webgpu-gommage-msdf-dissolve"
    size_budgets = {
        "screenshots/minimal-rebuild-desktop.png": 300_000,
        "videos/minimal-rebuild-motion.gif": 3_000_000,
        "code/minimal-rebuild.html": 42_000,
    }

    for rel_path, max_bytes in size_budgets.items():
        asset_path = case_dir / rel_path
        assert asset_path.is_file()
        assert asset_path.stat().st_size <= max_bytes

    html_text = (case_dir / "code" / "minimal-rebuild.html").read_text(encoding="utf-8")
    lowered_html = html_text.lower()
    assert "<script" not in lowered_html
    assert "src=" not in lowered_html
    assert "href=" not in lowered_html
    assert "http://" not in html_text
    assert "https://" not in html_text
    assert 'role="img"' in html_text
    assert 'data-msdf-text="generated"' in html_text
    assert len(re.findall(r'class=\"glyph-fragment', html_text)) >= 30
    assert len(re.findall(r'class=\"dust-particle', html_text)) >= 40
    assert len(re.findall(r'class=\"petal', html_text)) >= 16
    assert "animation: dissolve" in html_text


def test_codrops_threejs_meshline_family_gold_assets_are_bounded_and_self_contained():
    case_dir = REPO_ROOT / "data" / "vector-aesthetics" / "cases" / "codrops-threejs-meshline-family"
    size_budgets = {
        "screenshots/minimal-rebuild-desktop.png": 300_000,
        "videos/minimal-rebuild-motion.gif": 3_000_000,
        "code/minimal-rebuild.html": 44_000,
    }

    for rel_path, max_bytes in size_budgets.items():
        asset_path = case_dir / rel_path
        assert asset_path.is_file()
        assert asset_path.stat().st_size <= max_bytes

    html_text = (case_dir / "code" / "minimal-rebuild.html").read_text(encoding="utf-8")
    lowered_html = html_text.lower()
    assert "<script" not in lowered_html
    assert "src=" not in lowered_html
    assert "href=" not in lowered_html
    assert "http://" not in html_text
    assert "https://" not in html_text
    assert 'role="img"' in html_text
    assert 'data-meshline-field="generated"' in html_text
    assert len(re.findall(r'class=\"mesh-route', html_text)) >= 18
    assert len(re.findall(r'class=\"wire-cross', html_text)) >= 24
    assert len(re.findall(r'class=\"shader-ribbon', html_text)) >= 12
    assert "animation: sweep" in html_text


def test_false_earth_gold_assets_are_bounded_and_self_contained():
    case_dir = REPO_ROOT / "data" / "vector-aesthetics" / "cases" / "false-earth-webgpu-world"
    size_budgets = {
        "screenshots/minimal-rebuild-desktop.png": 320_000,
        "videos/minimal-rebuild-motion.gif": 3_200_000,
        "code/minimal-rebuild.html": 46_000,
    }

    for rel_path, max_bytes in size_budgets.items():
        asset_path = case_dir / rel_path
        assert asset_path.is_file()
        assert asset_path.stat().st_size <= max_bytes

    html_text = (case_dir / "code" / "minimal-rebuild.html").read_text(encoding="utf-8")
    lowered_html = html_text.lower()
    assert "<script" not in lowered_html
    assert "src=" not in lowered_html
    assert "href=" not in lowered_html
    assert "http://" not in html_text
    assert "https://" not in html_text
    assert 'role="img"' in html_text
    assert 'data-world-field="generated"' in html_text
    assert len(re.findall(r'class=\"grass-blade', html_text)) >= 48
    assert len(re.findall(r'class=\"cosmic-beam', html_text)) >= 8
    assert len(re.findall(r'class=\"wave-ring', html_text)) >= 5
    assert len(re.findall(r'class=\"flower-bloom', html_text)) >= 12
    assert "animation: drift" in html_text


def test_matrix_sentinels_gold_assets_are_bounded_and_self_contained():
    case_dir = REPO_ROOT / "data" / "vector-aesthetics" / "cases" / "matrix-sentinels-particle-trails-tsl"
    size_budgets = {
        "screenshots/minimal-rebuild-desktop.png": 320_000,
        "videos/minimal-rebuild-motion.gif": 3_200_000,
        "code/minimal-rebuild.html": 48_000,
    }

    for rel_path, max_bytes in size_budgets.items():
        asset_path = case_dir / rel_path
        assert asset_path.is_file()
        assert asset_path.stat().st_size <= max_bytes

    html_text = (case_dir / "code" / "minimal-rebuild.html").read_text(encoding="utf-8")
    lowered_html = html_text.lower()
    assert "<script" not in lowered_html
    assert "src=" not in lowered_html
    assert "href=" not in lowered_html
    assert "http://" not in html_text
    assert "https://" not in html_text
    assert 'role="img"' in html_text
    assert 'data-trail-field="generated"' in html_text
    assert len(re.findall(r'class=\"trail-route', html_text)) >= 8
    assert len(re.findall(r'class=\"history-slice', html_text)) >= 32
    assert len(re.findall(r'class=\"sentinel-head', html_text)) >= 8
    assert len(re.findall(r'class=\"flow-vector', html_text)) >= 20
    assert "animation: trace" in html_text


def test_spline_contemporary_3d_web_gold_assets_are_bounded_and_self_contained():
    case_dir = REPO_ROOT / "data" / "vector-aesthetics" / "cases" / "spline-contemporary-3d-web"
    size_budgets = {
        "screenshots/minimal-rebuild-desktop.png": 300_000,
        "videos/minimal-rebuild-motion.gif": 3_000_000,
        "code/minimal-rebuild.html": 44_000,
    }

    for rel_path, max_bytes in size_budgets.items():
        asset_path = case_dir / rel_path
        assert asset_path.is_file()
        assert asset_path.stat().st_size <= max_bytes

    html_text = (case_dir / "code" / "minimal-rebuild.html").read_text(encoding="utf-8")
    lowered_html = html_text.lower()
    assert "<script" not in lowered_html
    assert "src=" not in lowered_html
    assert "href=" not in lowered_html
    assert "http://" not in html_text
    assert "https://" not in html_text
    assert 'role="img"' in html_text
    assert 'data-spline-ui="generated"' in html_text
    assert len(re.findall(r'class=\"ui-panel', html_text)) >= 5
    assert len(re.findall(r'class=\"spatial-node', html_text)) >= 12
    assert len(re.findall(r'class=\"state-track', html_text)) >= 4
    assert len(re.findall(r'class=\"hotspot', html_text)) >= 6
    assert "animation: morph" in html_text
