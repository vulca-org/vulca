"""Integration tests — VULCA SDK public API with real Gemini calls.

Run with:  pytest tests/integration/test_sdk_real.py -m integration -v
Requires:  GEMINI_API_KEY in environment or .env file.

Test coverage:
  1. vulca.evaluate()         — real VLM scoring via Gemini
  2. vulca.create() mock      — local pipeline, no API call  (no marker)
  3. vulca.create() HITL      — pipeline pauses at decide    (no marker)
  4. vulca.create() weights   — custom L1-L5 weights         (no marker)
  5. vulca.traditions()       — returns all 9 names          (no marker)
  6. vulca._vlm.score_image() — direct async VLM call        (integration)
"""

from __future__ import annotations

import asyncio
import base64
import sys
import time
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# sys.path: make the vulca SDK importable from within the backend test runner
# ---------------------------------------------------------------------------
_VULCA_SRC = Path(__file__).resolve().parents[4] / "vulca" / "src"
if str(_VULCA_SRC) not in sys.path:
    sys.path.insert(0, str(_VULCA_SRC))

import vulca  # noqa: E402  (after sys.path manipulation)

_FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
_ARTWORK_PNG = _FIXTURES_DIR / "test_artwork.png"

# ---------------------------------------------------------------------------
# Throttle evolution to avoid 8+ second CulturalClusterer on 1700+ sessions.
#
# ContextEvolver().evolve() clusters all sessions — O(n²) on the full
# JSONL store (~1700 sessions).  We set _last_evolution_time to "just ran"
# so the 5-minute throttle skips evolution during rapid test iterations.
# This is the SAME mechanism production uses — not a mock bypass.
# ---------------------------------------------------------------------------

def _throttle_evolution() -> None:
    try:
        import vulca.pipeline.hooks as _hooks
        import time
        _hooks._last_evolution_time = time.monotonic()
    except Exception:
        pass


_throttle_evolution()

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def artwork_path() -> Path:
    assert _ARTWORK_PNG.exists(), f"Missing fixture: {_ARTWORK_PNG}"
    return _ARTWORK_PNG


@pytest.fixture(scope="module")
def artwork_b64() -> str:
    assert _ARTWORK_PNG.exists(), f"Missing fixture: {_ARTWORK_PNG}"
    return base64.b64encode(_ARTWORK_PNG.read_bytes()).decode()


# ---------------------------------------------------------------------------
# 1. vulca.evaluate() — real Gemini VLM
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestVulcaEvaluate:
    """vulca.evaluate(image_path, tradition=...) with real Gemini API."""

    def test_returns_eval_result(self, artwork_path, gemini_api_key):
        result = vulca.evaluate(
            artwork_path,
            tradition="chinese_xieyi",
            api_key=gemini_api_key,
        )
        assert result is not None
        assert isinstance(result, vulca.EvalResult)

    def test_score_in_range(self, artwork_path, gemini_api_key):
        result = vulca.evaluate(
            artwork_path,
            tradition="chinese_xieyi",
            api_key=gemini_api_key,
        )
        assert 0.0 <= result.score <= 1.0, f"score={result.score} out of [0, 1]"

    def test_all_l1_to_l5_dimensions_present(self, artwork_path, gemini_api_key):
        result = vulca.evaluate(
            artwork_path,
            tradition="chinese_xieyi",
            api_key=gemini_api_key,
        )
        for level in ("L1", "L2", "L3", "L4", "L5"):
            assert level in result.dimensions, f"Missing dimension {level}"
            val = result.dimensions[level]
            assert isinstance(val, float), f"{level} is {type(val)}"
            assert 0.0 <= val <= 1.0, f"{level}={val} out of [0, 1]"

    def test_dimension_properties(self, artwork_path, gemini_api_key):
        """EvalResult.L1 ... L5 properties must mirror dimensions dict."""
        result = vulca.evaluate(
            artwork_path,
            tradition="chinese_xieyi",
            api_key=gemini_api_key,
        )
        assert result.L1 == result.dimensions["L1"]
        assert result.L2 == result.dimensions["L2"]
        assert result.L3 == result.dimensions["L3"]
        assert result.L4 == result.dimensions["L4"]
        assert result.L5 == result.dimensions["L5"]

    def test_rationales_present(self, artwork_path, gemini_api_key):
        result = vulca.evaluate(
            artwork_path,
            tradition="chinese_xieyi",
            subject="ink wash landscape",
            api_key=gemini_api_key,
        )
        # At least 3 of 5 rationales should be non-empty strings
        non_empty = sum(
            1 for k in ("L1", "L2", "L3", "L4", "L5")
            if result.rationales.get(k, "")
        )
        assert non_empty >= 3, (
            f"Only {non_empty}/5 rationales non-empty: {result.rationales}"
        )

    def test_tradition_recorded(self, artwork_path, gemini_api_key):
        result = vulca.evaluate(
            artwork_path,
            tradition="chinese_xieyi",
            api_key=gemini_api_key,
        )
        assert result.tradition == "chinese_xieyi"

    def test_latency_reasonable(self, artwork_path, gemini_api_key):
        """Real VLM call should complete within 60 seconds."""
        t0 = time.monotonic()
        vulca.evaluate(
            artwork_path,
            tradition="default",
            api_key=gemini_api_key,
        )
        elapsed = time.monotonic() - t0
        assert elapsed < 60, f"evaluate() took {elapsed:.1f}s (>60s limit)"

    @pytest.mark.parametrize("tradition", [
        "chinese_xieyi",
        "western_academic",
        "islamic_geometric",
    ])
    def test_three_traditions(self, artwork_path, gemini_api_key, tradition):
        """Spot-check 3 diverse traditions — verify valid response, not score value.

        The fixture is a synthetic gradient; low scores (even 0.0) are acceptable.
        """
        result = vulca.evaluate(
            artwork_path,
            tradition=tradition,
            subject=f"test {tradition}",
            api_key=gemini_api_key,
        )
        assert result.tradition == tradition
        assert 0.0 <= result.score <= 1.0
        for level in ("L1", "L2", "L3", "L4", "L5"):
            assert level in result.dimensions


# ---------------------------------------------------------------------------
# 2. vulca.create() with mock provider — no real API call (no integration mark)
# ---------------------------------------------------------------------------

class TestVulcaCreateMock:
    """vulca.create() with provider='mock', mode='local' — no Gemini needed."""

    def test_returns_create_result(self):
        result = vulca.create("ink wash mountains", provider="mock", mode="local")
        assert result is not None
        assert isinstance(result, vulca.CreateResult)

    def test_has_session_id(self):
        result = vulca.create("ink wash mountains", provider="mock", mode="local")
        assert result.session_id, "session_id should be a non-empty string"

    def test_status_is_completed(self):
        result = vulca.create("ink wash mountains", provider="mock", mode="local")
        assert result.status == "completed", f"Expected 'completed', got {result.status!r}"

    def test_scores_dict_present(self):
        result = vulca.create("ink wash mountains", provider="mock", mode="local")
        # Mock pipeline should populate scores after evaluate node
        assert isinstance(result.scores, dict)

    def test_weighted_total_in_range(self):
        result = vulca.create("ink wash mountains", provider="mock", mode="local")
        assert 0.0 <= result.weighted_total <= 1.0, (
            f"weighted_total={result.weighted_total} out of [0, 1]"
        )

    def test_total_rounds_positive(self):
        result = vulca.create("ink wash mountains", provider="mock", mode="local")
        assert result.total_rounds >= 1

    def test_rounds_list_matches_count(self):
        result = vulca.create("ink wash mountains", provider="mock", mode="local")
        assert len(result.rounds) == result.total_rounds

    def test_summary_non_empty(self):
        result = vulca.create("ink wash mountains", provider="mock", mode="local")
        assert result.summary, "summary should be a non-empty string"

    def test_no_interrupted_at_when_not_hitl(self):
        result = vulca.create("ink wash mountains", provider="mock", mode="local")
        assert result.interrupted_at == ""


# ---------------------------------------------------------------------------
# 3. vulca.create() with HITL — no real API call (no integration mark)
# ---------------------------------------------------------------------------

class TestVulcaCreateHITL:
    """vulca.create() with hitl=True — pipeline should pause before 'decide'."""

    def test_status_is_waiting_human(self):
        result = vulca.create("mountains", provider="mock", hitl=True)
        assert result.status == "waiting_human", (
            f"Expected 'waiting_human', got {result.status!r}"
        )

    def test_interrupted_at_is_decide(self):
        result = vulca.create("mountains", provider="mock", hitl=True)
        assert result.interrupted_at == "decide", (
            f"Expected interrupted_at='decide', got {result.interrupted_at!r}"
        )

    def test_session_id_present(self):
        result = vulca.create("mountains", provider="mock", hitl=True)
        assert result.session_id, "session_id should be non-empty on HITL pause"

    def test_tradition_recorded(self):
        result = vulca.create("mountains", provider="mock", hitl=True, tradition="chinese_xieyi")
        assert result.tradition == "chinese_xieyi"


# ---------------------------------------------------------------------------
# 4. vulca.create() with custom weights — no real API call (no integration mark)
# ---------------------------------------------------------------------------

class TestVulcaCreateCustomWeights:
    """vulca.create() with weights={...} — weighted_total should reflect custom weights."""

    _CUSTOM_WEIGHTS = {"L1": 0.5, "L2": 0.1, "L3": 0.2, "L4": 0.1, "L5": 0.1}

    def test_completes_successfully(self):
        result = vulca.create(
            "mountains",
            provider="mock",
            weights=self._CUSTOM_WEIGHTS,
        )
        assert result.status == "completed"

    def test_weighted_total_in_range(self):
        result = vulca.create(
            "mountains",
            provider="mock",
            weights=self._CUSTOM_WEIGHTS,
        )
        assert 0.0 <= result.weighted_total <= 1.0

    def test_weighted_total_differs_from_default(self):
        """Custom L1=0.5 vs default L1=0.15 should produce a different total.

        We compare against equal-weight baseline to verify custom weights apply.
        """
        result_custom = vulca.create(
            "mountains",
            provider="mock",
            weights=self._CUSTOM_WEIGHTS,
        )
        result_default = vulca.create(
            "mountains",
            provider="mock",
        )
        # They use the same mock scores — only the weighting differs.
        # If custom weights are applied, totals must differ.
        assert result_custom.weighted_total != result_default.weighted_total, (
            f"Custom and default weights produced identical totals: "
            f"{result_custom.weighted_total} — custom weights may not be applied."
        )

    def test_custom_weights_sum_to_one(self):
        """Sanity check: the test fixture's weights must sum to 1.0."""
        total = sum(self._CUSTOM_WEIGHTS.values())
        assert abs(total - 1.0) < 1e-9, f"Test weights sum={total}, expected 1.0"


# ---------------------------------------------------------------------------
# 5. vulca.traditions() — no real API call (no integration mark)
# ---------------------------------------------------------------------------

class TestVulcaTraditions:
    """vulca.traditions() returns all 9 known tradition names."""

    _EXPECTED = {
        "default",
        "chinese_xieyi",
        "chinese_gongbi",
        "western_academic",
        "islamic_geometric",
        "japanese_traditional",
        "watercolor",
        "african_traditional",
        "south_asian",
    }

    def test_returns_list(self):
        result = vulca.traditions()
        assert isinstance(result, list)

    def test_returns_9_traditions(self):
        result = vulca.traditions()
        assert len(result) == 9, f"Expected 9 traditions, got {len(result)}: {result}"

    def test_all_expected_names_present(self):
        result = set(vulca.traditions())
        missing = self._EXPECTED - result
        assert not missing, f"Missing traditions: {missing}"

    def test_all_strings(self):
        for t in vulca.traditions():
            assert isinstance(t, str), f"Tradition {t!r} is not a string"

    def test_no_duplicates(self):
        result = vulca.traditions()
        assert len(result) == len(set(result)), "Duplicate tradition names found"


# ---------------------------------------------------------------------------
# 6. Direct score_image() — real Gemini async VLM call
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestScoreImageDirect:
    """vulca._vlm.score_image() — direct async call to Gemini Vision."""

    def test_returns_l1_to_l5_scores(self, artwork_b64, gemini_api_key):
        from vulca._vlm import score_image

        result = asyncio.run(
            score_image(
                img_b64=artwork_b64,
                mime="image/png",
                subject="abstract gradient composition",
                tradition="default",
                api_key=gemini_api_key,
            )
        )

        for level in ("L1", "L2", "L3", "L4", "L5"):
            assert level in result, f"Missing key {level!r}"
            val = result[level]
            assert isinstance(val, float), f"{level} is {type(val)}"
            assert 0.0 <= val <= 1.0, f"{level}={val} out of [0, 1]"

    def test_returns_rationales(self, artwork_b64, gemini_api_key):
        from vulca._vlm import score_image

        result = asyncio.run(
            score_image(
                img_b64=artwork_b64,
                mime="image/png",
                subject="abstract gradient for rationale test",
                tradition="chinese_xieyi",
                api_key=gemini_api_key,
            )
        )

        non_empty = sum(
            1 for level in ("L1", "L2", "L3", "L4", "L5")
            if result.get(f"{level}_rationale", "")
        )
        assert non_empty >= 3, (
            f"Only {non_empty}/5 rationales non-empty.\nResult: {result}"
        )

    def test_no_error_key_on_success(self, artwork_b64, gemini_api_key):
        from vulca._vlm import score_image

        result = asyncio.run(
            score_image(
                img_b64=artwork_b64,
                mime="image/png",
                subject="success path test",
                tradition="default",
                api_key=gemini_api_key,
            )
        )
        assert "error" not in result, (
            f"score_image returned an error: {result.get('error')}"
        )

    def test_scores_clamped_to_unit_interval(self, artwork_b64, gemini_api_key):
        """Even if the model returns an out-of-range value, it must be clamped."""
        from vulca._vlm import score_image

        result = asyncio.run(
            score_image(
                img_b64=artwork_b64,
                mime="image/png",
                subject="clamping boundary check",
                tradition="western_academic",
                api_key=gemini_api_key,
            )
        )
        for level in ("L1", "L2", "L3", "L4", "L5"):
            val = result[level]
            assert 0.0 <= val <= 1.0, f"{level}={val} violates [0, 1] after clamping"

    def test_tradition_guidance_injected(self, artwork_b64, gemini_api_key):
        """Calling with chinese_xieyi tradition should not raise — confirms
        _build_tradition_guidance() is called without error."""
        from vulca._vlm import score_image

        result = asyncio.run(
            score_image(
                img_b64=artwork_b64,
                mime="image/png",
                subject="tradition guidance injection test",
                tradition="chinese_xieyi",
                api_key=gemini_api_key,
            )
        )
        # Just check the call succeeded and returned valid structure
        assert "L1" in result
        assert "L5" in result
