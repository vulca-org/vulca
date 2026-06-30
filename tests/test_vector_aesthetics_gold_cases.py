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

    assert payload["summary"]["gold_case_count"] == 2
    assert payload["summary"]["multimodal_complete_count"] == 2
    for case in [makio, text_destruction]:
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
