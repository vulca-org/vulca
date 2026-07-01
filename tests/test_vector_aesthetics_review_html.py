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
    assert "Compare Matrix" in html_text
    assert "Screenshot / Video" in html_text
    assert "Coverage View" in html_text
    assert "Lesson Path View" in html_text
    assert "Makio MeshLine" in html_text
    assert "Primitive:" in html_text
    assert "Technique:" in html_text
    assert "minimal_rebuild_exercise" in html_text
    assert "VULCA Translation" in html_text
    assert "learning_primitive" in html_text
    assert "meshline learning primitive" in html_text
    assert "Manifest present, no archived assets" in html_text
    assert "Data Quality Gate" in html_text
    assert "Seed/stub cases" in html_text
    assert "Gold cases" in html_text
    assert "metadata_only_modules" in html_text
    assert '<script id="review-data" type="application/json">' in html_text


def test_write_review_html_renders_release_ready_state_for_complete_payload(tmp_path: Path):
    from vulca.vector_aesthetics.review_html import write_review_html

    review_json = tmp_path / "references.json"
    review_json.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "summary": {
                    "case_count": 1,
                    "gold_case_count": 1,
                    "seed_stub_case_count": 0,
                    "multimodal_complete_count": 1,
                    "shortlist_count": 1,
                    "candidate_count": 0,
                },
                "cases": [
                    {
                        "id": "complete-case",
                        "title": "Complete Case",
                        "summary": "Complete learning case.",
                        "visual_families": ["shader_material"],
                        "coverage": {
                            "screenshots": "complete",
                            "video": "complete",
                            "code_anatomy": "complete",
                            "lesson": "complete",
                            "vulca_translation": "complete",
                        },
                        "quality_score_total": 17,
                        "review_status": "shortlist",
                        "canonical_url": "https://example.com",
                        "asset_manifest_status": "present_with_assets",
                        "data_quality_flags": [],
                        "modules": [
                            {
                                "module_type": "shader_material",
                                "review_status": "complete",
                                "confidence": "high",
                                "payload": {"learning_primitive": "complete primitive"},
                            }
                        ],
                        "captures": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    html_text = write_review_html(review_json, tmp_path / "index.html").read_text(encoding="utf-8")

    assert "Release-ready atlas" in html_text
    assert "No active seed gaps" in html_text
    assert "Completion Checklist" in html_text
    assert "All tracked cases are gold-ready and multimodal complete." in html_text
    assert '<label for="filter-seed">' not in html_text


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


def test_write_review_html_redacts_secret_like_href_values(tmp_path: Path):
    from vulca.vector_aesthetics.review_html import write_review_html

    review_json = tmp_path / "references.json"
    review_json.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "summary": {"case_count": 1},
                "cases": [
                    {
                        "id": "secret-href-case",
                        "title": "Secret Href Case",
                        "summary": "href redaction test",
                        "visual_families": [],
                        "coverage": {},
                        "quality_score_total": 0,
                        "review_status": "candidate",
                        "canonical_url": "https://example.com/?api_key=abcdef1234567890",
                        "modules": [],
                        "captures": [
                            {
                                "id": "capture-secret-href",
                                "evidence_type": "screenshot",
                                "path_or_url": "https://cdn.example.com/capture.png?token=abcdef1234567890",
                                "rights_status": "source_link_only",
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    html_text = write_review_html(review_json, tmp_path / "index.html").read_text(encoding="utf-8")

    assert "api_key=abcdef1234567890" not in html_text
    assert "token=abcdef1234567890" not in html_text
    assert "[redacted]" in html_text


def test_write_review_html_renders_capture_status_details(tmp_path: Path):
    from vulca.vector_aesthetics.review_html import write_review_html

    review_json = tmp_path / "references.json"
    review_json.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "summary": {"case_count": 1},
                "cases": [
                    {
                        "id": "capture-case",
                        "title": "Capture Case",
                        "summary": "Capture detail test.",
                        "visual_families": [],
                        "coverage": {"screenshots": "partial"},
                        "quality_score_total": 0,
                        "review_status": "candidate",
                        "canonical_url": "https://example.com",
                        "modules": [],
                        "captures": [
                            {
                                "id": "capture-1",
                                "evidence_type": "screenshot",
                                "path_or_url": "captures/shot.png",
                                "capture_method": "manual_browser",
                                "viewport": "desktop",
                                "interaction": "capture_failed",
                                "captured_at": "2026-06-29",
                                "source_url": "https://example.com/source",
                                "confidence": "medium",
                                "rights_status": "source_link_only",
                                "notes": "No local screenshot archived yet.",
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    html_text = write_review_html(review_json, tmp_path / "index.html").read_text(encoding="utf-8")

    for expected in [
        "capture_failed",
        "source_link_only",
        "manual_browser",
        "medium",
        "No local screenshot archived yet.",
        "source_url",
        "evidence_type",
        "capture_method",
    ]:
        assert expected in html_text


def test_write_review_html_blocks_unsafe_href_and_hardens_script_json(tmp_path: Path):
    from vulca.vector_aesthetics.review_html import write_review_html

    review_json = tmp_path / "references.json"
    review_json.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "summary": {"case_count": 1},
                "cases": [
                    {
                        "id": "unsafe-case",
                        "title": "</script><script>alert(1)</script>",
                        "summary": "unsafe href test",
                        "visual_families": [],
                        "coverage": {},
                        "quality_score_total": 0,
                        "review_status": "candidate",
                        "canonical_url": "javascript:alert(1)",
                        "modules": [],
                        "captures": [
                            {
                                "id": "capture-unsafe",
                                "evidence_type": "screenshot",
                                "path_or_url": "javascript:alert(1)",
                                "capture_method": "manual_browser",
                                "viewport": "desktop",
                                "interaction": "capture_failed",
                                "captured_at": "2026-06-29",
                                "source_url": "javascript:alert(1)",
                                "confidence": "medium",
                                "rights_status": "source_link_only",
                                "notes": "unsafe capture link",
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    html_text = write_review_html(review_json, tmp_path / "index.html").read_text(encoding="utf-8")
    script_body = html_text.split('<script id="review-data" type="application/json">', 1)[1].split("</script>", 1)[0]

    assert 'href="javascript:' not in html_text
    assert "</script>" not in script_body

    parsed = json.loads(script_body.replace("<\\/", "</"))
    assert parsed["cases"][0]["title"] == "</script><script>alert(1)</script>"


def test_write_review_html_renders_media_previews_filters_family_matrix_and_gap_queue(tmp_path: Path):
    from vulca.vector_aesthetics.review_html import write_review_html

    case_dir = tmp_path / "vector-aesthetics" / "cases" / "gold-case"
    (case_dir / "screenshots").mkdir(parents=True)
    (case_dir / "videos").mkdir(parents=True)
    (case_dir / "screenshots" / "still.png").write_text("png fixture", encoding="utf-8")
    (case_dir / "videos" / "motion.gif").write_text("gif fixture", encoding="utf-8")
    output_dir = tmp_path / "output" / "review"
    review_json = tmp_path / "references.json"
    review_json.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "summary": {
                    "case_count": 2,
                    "gold_case_count": 1,
                    "multimodal_complete_count": 1,
                    "seed_stub_case_count": 1,
                },
                "cases": [
                    {
                        "id": "gold-case",
                        "title": "Gold Case",
                        "summary": "Gold preview test.",
                        "visual_families": ["meshline", "scan_depth"],
                        "coverage": {"screenshots": "complete", "video": "complete"},
                        "quality_score_total": 17,
                        "review_status": "shortlist",
                        "canonical_url": "https://example.com/gold",
                        "asset_manifest_status": "present_with_assets",
                        "data_quality_flags": [],
                        "case_rel": case_dir.as_posix(),
                        "modules": [{"module_type": "meshline", "payload": {}, "review_status": "complete", "confidence": "high"}],
                        "captures": [
                            {
                                "id": "still",
                                "evidence_type": "screenshot",
                                "path_or_url": "screenshots/still.png",
                                "capture_method": "user_supplied",
                                "viewport": "960x540",
                                "interaction": "idle",
                                "captured_at": "2026-06-30",
                                "source_url": "https://example.com/gold",
                                "confidence": "high",
                                "rights_status": "local_capture",
                                "notes": "Local still.",
                            },
                            {
                                "id": "motion",
                                "evidence_type": "video",
                                "path_or_url": "videos/motion.gif",
                                "capture_method": "user_supplied",
                                "viewport": "960x540",
                                "interaction": "motion",
                                "captured_at": "2026-06-30",
                                "source_url": "https://example.com/gold",
                                "confidence": "high",
                                "rights_status": "local_capture",
                                "notes": "Local motion.",
                            },
                        ],
                    },
                    {
                        "id": "seed-case",
                        "title": "Seed Case",
                        "summary": "Seed gap test.",
                        "visual_families": ["scan_depth"],
                        "coverage": {"screenshots": "partial", "video": "partial"},
                        "quality_score_total": 10,
                        "review_status": "candidate",
                        "canonical_url": "https://example.com/seed",
                        "asset_manifest_status": "present_empty",
                        "data_quality_flags": ["missing_local_screenshot", "metadata_only_modules"],
                        "case_rel": "cases/seed-case",
                        "modules": [{"module_type": "scan_depth", "payload": {}, "review_status": "partial", "confidence": "low"}],
                        "captures": [],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    html_text = write_review_html(review_json, output_dir / "index.html").read_text(encoding="utf-8")
    still_href = os.path.relpath(case_dir / "screenshots" / "still.png", output_dir).replace(os.sep, "/")
    motion_href = os.path.relpath(case_dir / "videos" / "motion.gif", output_dir).replace(os.sep, "/")

    assert "Review Filters" in html_text
    assert 'class="view-pill active-view"' in html_text
    assert 'id="filter-gold"' in html_text
    assert 'id="filter-seed"' in html_text
    assert 'class="case-card case-gold"' in html_text
    assert 'class="case-card case-seed"' in html_text
    assert "Family Coverage Matrix" in html_text
    assert "meshline" in html_text
    assert "scan_depth" in html_text
    assert "1 / 1 gold" in html_text
    assert "1 / 2 gold" in html_text
    assert "Gap Queue" in html_text
    assert 'class="gap-flags"' in html_text
    assert '<span>missing_local_screenshot</span>' in html_text
    assert '<span>metadata_only_modules</span>' in html_text
    assert "missing_local_screenshot" in html_text
    assert f'src="{still_href}"' in html_text
    assert f'src="{motion_href}"' in html_text
    assert 'alt="Gold Case screenshot preview"' in html_text
    assert 'alt="Gold Case video preview"' in html_text
