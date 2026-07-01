from __future__ import annotations

import json
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_HTML = (
    REPO_ROOT
    / "docs"
    / "product"
    / "experiments"
    / "3d-vector-aesthetic-stage-02-candidates"
    / "index.html"
)


def _candidate_data() -> list[dict[str, object]]:
    text = CANDIDATE_HTML.read_text(encoding="utf-8")
    match = re.search(r"const CANDIDATES = (\[.*?\]);", text, re.S)
    assert match, "candidate data block missing"
    return json.loads(match.group(1))


def test_stage2_candidate_spike_exists_as_self_contained_review_page():
    html_text = CANDIDATE_HTML.read_text(encoding="utf-8")
    lowered = html_text.lower()

    assert CANDIDATE_HTML.is_file()
    assert CANDIDATE_HTML.stat().st_size < 70_000
    assert 'data-vector-stage-product="2026-06-stage-02-central-object-spike"' in html_text
    assert '<canvas id="stageCanvas"' in html_text
    assert "Choose the subject." in html_text
    assert "central-object candidates" in html_text
    assert "__VULCA_STAGE02_CANDIDATES__" in html_text

    for banned in ["<iframe", "https://", "http://", "src=", 'href="http']:
        assert banned not in lowered


def test_stage2_candidate_spike_has_six_non_text_central_subjects():
    candidates = _candidate_data()

    assert len(candidates) == 6
    assert {candidate["id"] for candidate in candidates} == {
        "evidence-garden",
        "glass-root-archive",
        "evidence-instrument",
        "mineral-scanner-seed",
        "route-core-sculpture",
        "archive-constellation",
    }
    for candidate in candidates:
        prompt = str(candidate["modelPrompt"]).lower()
        assert "single centered 3d" in prompt
        assert "no text" in prompt
        assert "export as glb" in prompt
        assert "logo" in prompt
        assert len(candidate["states"]) == 4


def test_stage2_candidate_spike_supports_scroll_state_grammar_and_scoring():
    candidates = _candidate_data()
    families = {candidate["family"] for candidate in candidates}
    html_text = CANDIDATE_HTML.read_text(encoding="utf-8")

    assert {"micro_world", "living_system", "product_exploded_view", "technical_device", "spatial_sculpture"} <= families
    assert "Page state:" in html_text
    assert "scan, bloom, explode, archive" in html_text
    assert "drawEvidenceGarden" in html_text
    assert "drawEvidenceInstrument" in html_text
    assert "drawArchiveConstellation" in html_text

    for candidate in candidates:
        score = candidate["score"]
        assert set(score) == {"firstFrame", "silhouette", "statePotential", "assetRisk"}
        assert all(isinstance(value, int) and 0 <= value <= 3 for value in score.values())


def test_stage2_candidate_spike_does_not_revive_rejected_typography_poster():
    html_text = CANDIDATE_HTML.read_text(encoding="utf-8")

    for rejected in [
        "Depth Typography Poster",
        "drawDepthTypography",
        "drawGhostType",
        "VECTOR",
        "large readable typography",
    ]:
        assert rejected not in html_text
