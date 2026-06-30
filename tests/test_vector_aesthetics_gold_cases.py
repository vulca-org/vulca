from __future__ import annotations

import json
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_checked_in_makio_meshline_is_first_gold_case(tmp_path: Path):
    from vulca.vector_aesthetics.compiler import compile_database, export_review_json_from_sqlite

    root = REPO_ROOT / "data" / "vector-aesthetics"
    sqlite_path = tmp_path / "references.sqlite"
    output_path = tmp_path / "references.json"

    compile_database(root, sqlite_path)
    export_review_json_from_sqlite(sqlite_path, output_path)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    cases = {case["id"]: case for case in payload["cases"]}
    makio = cases["makio-meshline"]

    assert payload["summary"]["gold_case_count"] == 1
    assert payload["summary"]["multimodal_complete_count"] == 1
    assert makio["coverage"]["screenshots"] == "complete"
    assert makio["coverage"]["video"] == "complete"
    assert makio["coverage"]["code_anatomy"] == "complete"
    assert makio["coverage"]["lesson"] == "complete"
    assert makio["coverage"]["vulca_translation"] == "complete"
    assert makio["coverage"]["module_payloads"] == "complete"
    assert makio["coverage"]["asset_manifest"] == "complete"
    assert makio["data_quality_flags"] == []
    assert makio["asset_manifest_status"] == "present_with_assets"
    assert any(
        capture["evidence_type"] == "screenshot" and capture["rights_status"] == "local_capture"
        for capture in makio["captures"]
    )
    assert any(
        capture["evidence_type"] == "video" and capture["rights_status"] == "local_capture"
        for capture in makio["captures"]
    )
    assert any(
        capture["evidence_type"] == "code_note" and capture["rights_status"] == "local_capture"
        for capture in makio["captures"]
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
    assert "<script" not in html_text.lower()
    assert "http://" not in html_text
    assert "https://" not in html_text
    assert 'role="img"' in html_text
    assert len(re.findall(r'<path class="route"', html_text)) == 3
    assert "animation: travel" in html_text
