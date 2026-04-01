import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from vulca._vlm import (
    _DEFAULT_MAX_TOKENS,
    _ESCALATED_MAX_TOKENS,
    _STATIC_SCORING_PREFIX,
    _SYSTEM_PROMPT,
    _build_dynamic_suffix,
    _extract_scoring,
    _parse_vlm_response,
    score_image,
)


class TestVLMPromptStructure:
    def test_prompt_has_observe_phase(self):
        assert "OBSERVE" in _STATIC_SCORING_PREFIX or "observe" in _STATIC_SCORING_PREFIX.lower()

    def test_prompt_has_evaluate_phase(self):
        assert "EVALUATE" in _STATIC_SCORING_PREFIX or "evaluate" in _STATIC_SCORING_PREFIX.lower()

    def test_prompt_requires_observations(self):
        assert "observations" in _STATIC_SCORING_PREFIX.lower()

    def test_prompt_requires_reference_technique(self):
        assert "reference_technique" in _STATIC_SCORING_PREFIX

    def test_prompt_has_static_dynamic_separation(self):
        """Static prefix contains L1/L5 but no {tradition} placeholders;
        _build_dynamic_suffix returns a non-empty string."""
        # Static prefix must describe L1 and L5
        assert "L1" in _STATIC_SCORING_PREFIX
        assert "L5" in _STATIC_SCORING_PREFIX
        # Static prefix must NOT have format placeholders for tradition
        assert "{tradition}" not in _STATIC_SCORING_PREFIX
        assert "{tradition_guidance}" not in _STATIC_SCORING_PREFIX
        # Dynamic suffix must be a non-empty string for a known tradition
        suffix = _build_dynamic_suffix("chinese_xieyi")
        assert isinstance(suffix, str)
        assert len(suffix) > 0
        # Backward-compat alias still points to the same text
        assert _SYSTEM_PROMPT is _STATIC_SCORING_PREFIX


class TestVLMResponseParsing:
    def test_parse_with_observations(self):
        raw = {
            "L1": 0.85, "L1_observations": "diagonal flow", "L1_rationale": "good",
            "L1_suggestion": "try X", "L1_reference_technique": "留白", "L1_deviation_type": "traditional",
            "L2": 0.7, "L2_observations": "ink grad", "L2_rationale": "ok",
            "L2_suggestion": "try Y", "L2_reference_technique": "泼墨", "L2_deviation_type": "traditional",
            "L3": 0.6, "L3_observations": "motifs", "L3_rationale": "fair",
            "L3_suggestion": "try Z", "L3_reference_technique": "气韵", "L3_deviation_type": "intentional_departure",
            "L4": 0.9, "L4_observations": "respectful", "L4_rationale": "great",
            "L4_suggestion": "push", "L4_reference_technique": "六法", "L4_deviation_type": "traditional",
            "L5": 0.75, "L5_observations": "depth", "L5_rationale": "solid",
            "L5_suggestion": "explore", "L5_reference_technique": "道", "L5_deviation_type": "traditional",
        }
        scores, rationales, suggestions, deviations, observations, ref_techniques = _parse_vlm_response(raw)
        assert scores == {"L1": 0.85, "L2": 0.7, "L3": 0.6, "L4": 0.9, "L5": 0.75}
        assert observations["L1"] == "diagonal flow"
        assert ref_techniques["L2"] == "泼墨"

    def test_parse_missing_observations_defaults_empty(self):
        raw = {
            "L1": 0.5, "L1_rationale": "ok", "L1_suggestion": "try",
            "L1_deviation_type": "traditional",
            "L2": 0.5, "L2_rationale": "ok", "L2_suggestion": "try",
            "L2_deviation_type": "traditional",
            "L3": 0.5, "L3_rationale": "ok", "L3_suggestion": "try",
            "L3_deviation_type": "traditional",
            "L4": 0.5, "L4_rationale": "ok", "L4_suggestion": "try",
            "L4_deviation_type": "traditional",
            "L5": 0.5, "L5_rationale": "ok", "L5_suggestion": "try",
            "L5_deviation_type": "traditional",
        }
        scores, rationales, suggestions, deviations, observations, ref_techniques = _parse_vlm_response(raw)
        assert observations == {"L1": "", "L2": "", "L3": "", "L4": "", "L5": ""}
        assert ref_techniques == {"L1": "", "L2": "", "L3": "", "L4": "", "L5": ""}


class TestExtractScoring:
    def test_extract_scoring_strips_observation(self):
        """VLM response with both tags: only the <scoring> content is returned."""
        response = (
            "<observation>\n"
            "The brushwork shows loose, expressive strokes typical of xieyi style.\n"
            "Color temperature is cool with ink wash gradients.\n"
            "</observation>\n"
            "<scoring>\n"
            '{\"L1\": 0.8, \"L2\": 0.7}\n'
            "</scoring>"
        )
        result = _extract_scoring(response)
        assert result == '{"L1": 0.8, "L2": 0.7}'
        assert "<observation>" not in result
        assert "<scoring>" not in result
        assert "brushwork" not in result

    def test_extract_scoring_fallback_no_tags(self):
        """Raw JSON without tags is returned as-is (backward compatibility)."""
        raw_json = '{"L1": 0.75, "L2": 0.65, "L3": 0.80}'
        result = _extract_scoring(raw_json)
        assert result == raw_json


# ---------------------------------------------------------------------------
# Minimal valid scoring JSON for mock responses
# ---------------------------------------------------------------------------
_VALID_SCORING_JSON = (
    '{"L1": 0.8, "L1_rationale": "good", "L1_suggestion": "try", '
    '"L1_deviation_type": "traditional", "L1_observations": "", "L1_reference_technique": "", '
    '"L2": 0.7, "L2_rationale": "ok", "L2_suggestion": "try", '
    '"L2_deviation_type": "traditional", "L2_observations": "", "L2_reference_technique": "", '
    '"L3": 0.6, "L3_rationale": "fair", "L3_suggestion": "try", '
    '"L3_deviation_type": "traditional", "L3_observations": "", "L3_reference_technique": "", '
    '"L4": 0.9, "L4_rationale": "great", "L4_suggestion": "push", '
    '"L4_deviation_type": "traditional", "L4_observations": "", "L4_reference_technique": "", '
    '"L5": 0.75, "L5_rationale": "solid", "L5_suggestion": "explore", '
    '"L5_deviation_type": "traditional", "L5_observations": "", "L5_reference_technique": ""}'
)


def _make_mock_response(finish_reason: str, content: str) -> MagicMock:
    """Build a fake litellm response object."""
    choice = MagicMock()
    choice.finish_reason = finish_reason
    choice.message.content = content
    resp = MagicMock()
    resp.choices = [choice]
    return resp


class TestScoreImageTokenEscalation:
    """Verify adaptive token budget: escalate from _DEFAULT to _ESCALATED on truncation."""

    def test_score_image_escalates_on_truncation(self):
        """First call returns finish_reason='length'; second call should use escalated tokens."""
        # Truncated response (finish_reason="length") — minimal parseable content
        truncated_resp = _make_mock_response("length", "<scoring>" + _VALID_SCORING_JSON + "</scoring>")
        # Full response on retry
        full_resp = _make_mock_response("stop", "<scoring>" + _VALID_SCORING_JSON + "</scoring>")

        mock_acompletion = AsyncMock(side_effect=[truncated_resp, full_resp])

        with patch("litellm.acompletion", mock_acompletion):
            result = asyncio.run(
                score_image(
                    img_b64="aGVsbG8=",  # base64("hello")
                    mime="image/png",
                    subject="test artwork",
                    tradition="chinese_xieyi",
                    api_key="test-key",
                )
            )

        # Two calls must have been made
        assert mock_acompletion.call_count == 2

        call_args_list = mock_acompletion.call_args_list
        first_max_tokens = call_args_list[0].kwargs["max_tokens"]
        second_max_tokens = call_args_list[1].kwargs["max_tokens"]

        assert first_max_tokens == _DEFAULT_MAX_TOKENS, (
            f"First attempt must use _DEFAULT_MAX_TOKENS={_DEFAULT_MAX_TOKENS}, got {first_max_tokens}"
        )
        assert second_max_tokens == _ESCALATED_MAX_TOKENS, (
            f"Escalated attempt must use _ESCALATED_MAX_TOKENS={_ESCALATED_MAX_TOKENS}, got {second_max_tokens}"
        )
        # Scores should still be parsed correctly from the full response
        assert result.get("L1") == pytest.approx(0.8)

    def test_score_image_no_escalation_on_stop(self):
        """When finish_reason='stop', only one call is made at _DEFAULT_MAX_TOKENS."""
        full_resp = _make_mock_response("stop", "<scoring>" + _VALID_SCORING_JSON + "</scoring>")
        mock_acompletion = AsyncMock(return_value=full_resp)

        with patch("litellm.acompletion", mock_acompletion):
            result = asyncio.run(
                score_image(
                    img_b64="aGVsbG8=",
                    mime="image/png",
                    subject="test artwork",
                    tradition="chinese_xieyi",
                    api_key="test-key",
                )
            )

        assert mock_acompletion.call_count == 1
        used_tokens = mock_acompletion.call_args_list[0].kwargs["max_tokens"]
        assert used_tokens == _DEFAULT_MAX_TOKENS
        assert result.get("L1") == pytest.approx(0.8)

    def test_score_image_no_double_escalation(self):
        """Even if both responses are truncated, at most 2 total calls (1 retry)."""
        truncated = _make_mock_response("length", "<scoring>" + _VALID_SCORING_JSON + "</scoring>")
        mock_acompletion = AsyncMock(return_value=truncated)

        with patch("litellm.acompletion", mock_acompletion):
            asyncio.run(
                score_image(
                    img_b64="aGVsbG8=",
                    mime="image/png",
                    subject="test artwork",
                    tradition="chinese_xieyi",
                    api_key="test-key",
                )
            )

        # _MAX_ESCALATION_ATTEMPTS=1 means at most 2 calls total
        assert mock_acompletion.call_count == 2
