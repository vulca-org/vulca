from __future__ import annotations

import json
import os
from pathlib import Path


def test_write_review_html_renders_required_views(tmp_path: Path):
    from vulca.vector_aesthetics.compiler import compile_database, export_review_json
    from vulca.vector_aesthetics.review_html import write_review_html
    from vulca.vector_aesthetics.seeds import write_seed_cases

    root = tmp_path / "vector-aesthetics"
    write_seed_cases(root)
    records = compile_database(root, root / "references.sqlite")
    review_json = export_review_json(records, tmp_path / "references.json")
    html_path = write_review_html(review_json, tmp_path / "index.html")
    html_text = html_path.read_text(encoding="utf-8")

    assert "3D Vector Aesthetics Learning Atlas" in html_text
    assert "Atlas View" in html_text
    assert "Anatomy View" in html_text
    assert "Compare View" in html_text
    assert "Coverage View" in html_text
    assert "Lesson Path View" in html_text
    assert "Makio MeshLine" in html_text
    assert '<script id="review-data" type="application/json">' in html_text


def test_write_review_html_redacts_secret_like_json(tmp_path: Path):
    from vulca.vector_aesthetics.review_html import write_review_html

    review_json = tmp_path / "references.json"
    review_json.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "summary": {"case_count": 1},
                "cases": [
                    {
                        "id": "secret-case",
                        "title": "Secret Case",
                        "summary": "contains sk-proj-secret",
                        "visual_families": [],
                        "coverage": {},
                        "quality_score_total": 0,
                        "review_status": "candidate",
                        "canonical_url": "https://example.com",
                        "modules": [],
                        "captures": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    html_path = write_review_html(review_json, tmp_path / "index.html")

    assert "sk-proj-secret" not in html_path.read_text(encoding="utf-8")
    assert "[redacted]" in html_path.read_text(encoding="utf-8")


def test_write_review_html_escapes_case_metadata(tmp_path: Path):
    from vulca.vector_aesthetics.review_html import write_review_html

    review_json = tmp_path / "references.json"
    review_json.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "summary": {"case_count": 1},
                "cases": [
                    {
                        "id": "xss-case",
                        "title": "<script>alert(1)</script>",
                        "summary": "<img src=x onerror=alert(1)>",
                        "visual_families": ["<svg onload=alert(1)>"],
                        "coverage": {"metadata": "complete"},
                        "quality_score_total": 0,
                        "review_status": "candidate",
                        "canonical_url": "https://example.com/?q=<bad>",
                        "modules": [],
                        "captures": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    html_text = write_review_html(review_json, tmp_path / "index.html").read_text(encoding="utf-8")

    visible_html = html_text.split('<script id="review-data"', 1)[0]
    assert "<script>alert(1)</script>" not in visible_html
    assert "<img src=x onerror=alert(1)>" not in visible_html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in visible_html


def test_write_review_html_resolves_local_capture_links(tmp_path: Path):
    from vulca.vector_aesthetics.review_html import write_review_html

    case_dir = tmp_path / "vector-aesthetics" / "cases" / "local-case"
    (case_dir / "screenshots").mkdir(parents=True)
    (case_dir / "screenshots" / "idle.png").write_text("capture placeholder", encoding="utf-8")
    output_dir = tmp_path / "output" / "review"
    review_json = tmp_path / "references.json"
    review_json.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "summary": {"case_count": 1},
                "cases": [
                    {
                        "id": "local-case",
                        "title": "Local Case",
                        "summary": "Local capture link test.",
                        "visual_families": [],
                        "coverage": {"screenshots": "complete"},
                        "quality_score_total": 0,
                        "review_status": "candidate",
                        "canonical_url": "https://example.com",
                        "case_rel": case_dir.as_posix(),
                        "modules": [],
                        "captures": [
                            {
                                "id": "desktop-idle",
                                "evidence_type": "screenshot",
                                "path_or_url": "screenshots/idle.png",
                                "rights_status": "local_capture",
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    html_text = write_review_html(review_json, output_dir / "index.html").read_text(encoding="utf-8")
    expected = os.path.relpath(case_dir / "screenshots" / "idle.png", output_dir).replace(os.sep, "/")

    assert f'href="{expected}"' in html_text
