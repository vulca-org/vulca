from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PRODUCT_HTML = REPO_ROOT / "docs" / "product" / "experiments" / "3d-vector-aesthetic-stage" / "index.html"
VIDEO_SCRIPT = REPO_ROOT / "scripts" / "build_vector_stage_video.py"


def test_stage_product_is_single_file_recording_surface():
    html_text = PRODUCT_HTML.read_text(encoding="utf-8")
    lowered = html_text.lower()

    assert PRODUCT_HTML.is_file()
    assert PRODUCT_HTML.stat().st_size < 90_000
    assert 'data-vector-stage-product="2026-06"' in html_text
    assert "<canvas" in html_text
    assert "requestAnimationFrame" in html_text
    assert "projectPoint" in html_text
    assert "drawVectorTunnel" in html_text
    assert "drawTextParticleField" in html_text
    assert "drawMaterialRibbons" in html_text
    assert "drawUISculpture" in html_text
    assert "recordMode" in html_text
    assert "__VULCA_RENDER_FRAME__" in html_text
    assert "pointermove" in html_text

    assert "<iframe" not in lowered
    assert "http://" not in lowered
    assert "https://" not in lowered
    assert "src=" not in lowered
    assert "href=" not in lowered


def test_stage_product_embeds_atlas_learning_primitives():
    html_text = PRODUCT_HTML.read_text(encoding="utf-8")

    for primitive in [
        "meshline",
        "shader_material",
        "typography_3d",
        "particle_vector",
        "data_tunnel",
        "ui_sculpture",
        "wire_grid",
        "scan_depth",
    ]:
        assert primitive in html_text

    for case_id in [
        "countertype",
        "false-earth",
        "matrix-sentinels",
        "tsl-guide",
        "threejs-docs",
        "gommage",
        "scan-depth",
    ]:
        assert case_id in html_text


def test_stage_video_builder_targets_xhs_mp4():
    script_text = VIDEO_SCRIPT.read_text(encoding="utf-8")

    assert VIDEO_SCRIPT.is_file()
    assert "vector-stage-xhs-20260630.mp4" in script_text
    assert "540" in script_text
    assert "960" in script_text
    assert "Tingting" in script_text
    assert "VOICEOVER_TEXT" in script_text
    assert "SUBTITLE_CUES" in script_text
    assert "burn_subtitles_on_frames" in script_text
    assert "ImageDraw" in script_text
    assert "libx264" in script_text
    assert "aac" in script_text
    assert "__VULCA_RENDER_FRAME__" in script_text
