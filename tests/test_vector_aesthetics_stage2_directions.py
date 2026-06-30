from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HANDOFF = REPO_ROOT / "docs" / "product" / "experiments" / "3d-vector-aesthetic-stage-02-directions.md"


def test_stage2_direction_handoff_exists_with_three_directions():
    text = HANDOFF.read_text(encoding="utf-8")

    assert HANDOFF.is_file()
    assert text.count("## Direction ") == 3
    assert "Scan Typography Field" in text
    assert "Particle Reasoning Tunnel" in text
    assert "Spatial Type Interface" in text
    assert "Recommended for Stage 02." in text


def test_stage2_direction_handoff_maps_to_shortlist_sources():
    text = HANDOFF.read_text(encoding="utf-8")

    for case_id in [
        "webgpu-scanning-depth-maps",
        "webgpu-gommage-msdf-dissolve",
        "interactive-text-destruction-webgpu-tsl",
        "countertype-three-text",
        "matrix-sentinels-particle-trails-tsl",
        "makio-meshline",
        "codrops-threejs-meshline-family",
        "maxime-heckel-tsl-webgpu-guide",
        "spline-contemporary-3d-web",
        "phantom-land-interactive-grid",
        "false-earth-webgpu-world",
    ]:
        assert case_id in text


def test_stage2_direction_handoff_preserves_video_and_copy_constraints():
    text = HANDOFF.read_text(encoding="utf-8")

    for required in [
        "horizontal",
        "capture=1",
        "scripts/record_vector_stage_live.py",
        "zh-CN-XiaoxiaoNeural",
        "Subtitle segments and spoken audio must come from the same source text.",
        "output/video/",
        "effect",
        "continuation step",
        "future planning",
    ]:
        assert required in text

    for banned in ["不是", "而是", "AI 式", "反转句", "—", "–"]:
        assert banned not in text.replace(f"`{banned}`", "")
