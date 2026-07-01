from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DISCOVERY = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-reference-discovery.md"
)


def test_stage2_reference_discovery_exists_and_reframes_the_problem():
    text = DISCOVERY.read_text(encoding="utf-8")

    assert DISCOVERY.is_file()
    assert "Discovery for user review. Do not implement yet." in text
    assert "central visual element" in text
    assert "The main element is not text." in text
    assert "what is the subject?" in text
    assert "central_scroll_object" in text
    assert "3d-vector-aesthetic-stage-02-reference-board/index.html" in text
    assert "3d-vector-aesthetic-stage-02-reference-board.json" in text


def test_stage2_reference_discovery_includes_external_reference_shortlist():
    text = DISCOVERY.read_text(encoding="utf-8")

    for required in [
        "More Than a Portfolio: Building a Scroll-Driven 3D World with Something to Say",
        "https://tympanus.net/codrops/2026/04/28/more-than-a-portfolio-building-a-scroll-driven-3d-world-with-something-to-say/",
        "Weleda, The Open Garden",
        "https://www.awwwards.com/sites/weleda-the-open-garden",
        "iyO, Interactive WebGL Exploded View",
        "https://www.awwwards.com/inspiration/interactive-webgl-exploded-view-iyo",
        "https://www.awwwards.com/inspiration/scroll-navigation-with-animated-3d-models",
        "https://www.awwwards.com/inspiration/3d-environment-webgl-scroll-navigation",
    ]:
        assert required in text


def test_stage2_reference_discovery_includes_asset_and_runtime_stack():
    text = DISCOVERY.read_text(encoding="utf-8")

    for required in [
        "Spline AI 3D Generation",
        "https://docs.spline.design/spline-ai/ai-3d-generation",
        "Tripo API",
        "https://platform.tripo3d.ai/",
        "Meshy API",
        "https://www.meshy.ai/api",
        "Hunyuan3D",
        "https://github.com/Tencent-Hunyuan/Hunyuan3D-2",
        "TRELLIS",
        "https://github.com/microsoft/TRELLIS",
        "<model-viewer>",
        "React Three Fiber",
        "GSAP ScrollTrigger",
        "glTF Transform",
        "Blender glTF export",
    ]:
        assert required in text


def test_stage2_reference_discovery_recommends_micro_world_without_locking_build():
    text = DISCOVERY.read_text(encoding="utf-8")

    for required in [
        "D plus iyO mechanics",
        "Micro-world subject, exploded/scan state grammar.",
        "small evidence garden or data island",
        "Do this before any new Stage 02 implementation",
        "Only then choose the final Stage 02 direction.",
    ]:
        assert required in text

    assert "Depth Typography Poster" not in text
