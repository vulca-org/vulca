from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HANDOFF = REPO_ROOT / "docs" / "product" / "experiments" / "3d-vector-aesthetic-stage-02-directions.md"


def test_stage2_direction_handoff_exists_with_three_directions():
    text = HANDOFF.read_text(encoding="utf-8")

    assert HANDOFF.is_file()
    assert text.count("## Direction ") == 3
    assert "Depth Typography Poster" in text
    assert "Mineral Line Sculpture" in text
    assert "Quiet Interface Still Life" in text
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


def test_stage2_direction_handoff_preserves_visual_first_constraints():
    text = HANDOFF.read_text(encoding="utf-8")

    for required in [
        "horizontal",
        "visual-first",
        "dynamic visual poster",
        "first frame",
        "still frame",
        "one cold accent",
        "one warm accent",
        "zh-CN-XiaoxiaoNeural",
        "Subtitle segments and spoken audio must come from the same source text.",
        "output/video/",
        "effect",
        "future planning",
    ]:
        assert required in text

    for banned in [
        "capture=1",
        "scripts/record_vector_stage_live.py",
        "Pointer down",
        "Pointer release",
        "cursorTrail",
        "mouse demo",
        "—",
        "–",
    ]:
        assert banned not in text
