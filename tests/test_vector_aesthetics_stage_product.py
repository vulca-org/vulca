from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PRODUCT_HTML = REPO_ROOT / "docs" / "product" / "experiments" / "3d-vector-aesthetic-stage" / "index.html"
VIDEO_SCRIPT = REPO_ROOT / "scripts" / "build_vector_stage_video.py"
VOICE_AUDITION_SCRIPT = REPO_ROOT / "scripts" / "build_vector_voice_auditions.py"


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
    assert "drawRecordCursor" in html_text
    assert "getRecordCursor" in html_text
    assert "cursor: { ...recordCursor }" in html_text
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
    assert "vector-stage-xhs-horizontal-20260630.mp4" in script_text
    assert "1920" in script_text
    assert "1080" in script_text
    assert "zh-CN-XiaoxiaoNeural" in script_text
    assert "is_edge_voice" in script_text
    assert "VOICEOVER_SEGMENTS" in script_text
    assert "synthesize_voiceover" in script_text
    assert "subtitle_cues" in script_text
    assert "burn_subtitles_on_frames" in script_text
    assert "ImageDraw" in script_text
    assert "page.mouse.move" in script_text
    assert "page.mouse.down" in script_text
    assert "h264_videotoolbox" in script_text
    assert "12M" in script_text
    assert "aac" in script_text
    assert "__VULCA_RENDER_FRAME__" in script_text
    assert "不是" not in script_text
    assert "而是" not in script_text
    assert "AI 式" not in script_text
    assert "反转句" not in script_text


def test_stage_voice_audition_builder_compares_neural_cn_voices():
    script_text = VOICE_AUDITION_SCRIPT.read_text(encoding="utf-8")

    assert VOICE_AUDITION_SCRIPT.is_file()
    assert "SCRIPT_VARIANTS" in script_text
    assert "01_effect_plan" in script_text
    assert "02_short_direct" in script_text
    assert "03_product_roadmap" in script_text
    assert "zh-CN-XiaoxiaoNeural" in script_text
    assert "edge_tts" in script_text
    assert "loudnorm=I=-18" in script_text
    assert "Voice Auditions" in script_text
    assert "<audio controls" in script_text
    assert "不是" not in script_text
    assert "而是" not in script_text
    assert "AI 式" not in script_text
    assert "反转句" not in script_text
