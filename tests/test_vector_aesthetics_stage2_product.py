from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
STAGE2_HTML = REPO_ROOT / "docs" / "product" / "experiments" / "3d-vector-aesthetic-stage-02" / "index.html"


def test_stage2_product_is_visual_first_single_file_canvas():
    html_text = STAGE2_HTML.read_text(encoding="utf-8")
    lowered = html_text.lower()

    assert STAGE2_HTML.is_file()
    assert STAGE2_HTML.stat().st_size < 95_000
    assert 'data-vector-stage-product="2026-06-stage-02"' in html_text
    assert "<canvas" in html_text
    assert "Depth typography poster" in html_text
    assert "dynamic visual poster" in html_text
    assert "drawDepthTypography" in html_text
    assert "drawGhostType" in html_text
    assert "drawScanVeil" in html_text
    assert "drawComposedRibbons" in html_text
    assert "drawPosterFrame" in html_text
    assert "requestAnimationFrame" in html_text
    assert "recordMode" in html_text
    assert "__VULCA_RENDER_FRAME__" in html_text

    assert "<iframe" not in lowered
    assert "http://" not in lowered
    assert "https://" not in lowered
    assert "src=" not in lowered
    assert "href=" not in lowered


def test_stage2_product_removes_mouse_demo_language():
    html_text = STAGE2_HTML.read_text(encoding="utf-8")

    for banned in [
        "pointermove",
        "pointerdown",
        "pointerup",
        "pointerleave",
        "captureMode",
        "drawRecordCursor",
        "cursorTrail",
        "getRecordCursor",
        "page.mouse",
    ]:
        assert banned not in html_text


def test_stage2_product_uses_restrained_visual_palette():
    html_text = STAGE2_HTML.read_text(encoding="utf-8")

    for required in [
        "#060909",
        "#0c1715",
        "#efe6d0",
        "#6dd9cf",
        "#d8955d",
    ]:
        assert required in html_text

    for removed_stage1_color in [
        "#b7ff62",
        "#ff4f91",
        "#78a7ff",
        "#ff7b62",
    ]:
        assert removed_stage1_color not in html_text
