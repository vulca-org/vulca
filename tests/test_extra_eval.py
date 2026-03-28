from vulca.types import EvalResult
from vulca._vlm import _build_extra_dimensions_prompt, _parse_vlm_response


class TestExtraEvalFields:
    def test_eval_result_extra_scores_default_empty(self):
        r = EvalResult(
            score=0.8, tradition="test", dimensions={}, rationales={},
            summary="", risk_level="low", risk_flags=[], recommendations=[],
        )
        assert r.extra_scores == {}

    def test_eval_result_extra_rationales_default_empty(self):
        r = EvalResult(
            score=0.8, tradition="test", dimensions={}, rationales={},
            summary="", risk_level="low", risk_flags=[], recommendations=[],
        )
        assert r.extra_rationales == {}

    def test_eval_result_extra_suggestions_default_empty(self):
        r = EvalResult(
            score=0.8, tradition="test", dimensions={}, rationales={},
            summary="", risk_level="low", risk_flags=[], recommendations=[],
        )
        assert r.extra_suggestions == {}

    def test_eval_result_extra_observations_default_empty(self):
        r = EvalResult(
            score=0.8, tradition="test", dimensions={}, rationales={},
            summary="", risk_level="low", risk_flags=[], recommendations=[],
        )
        assert r.extra_observations == {}


class TestExtraDimensionsPrompt:
    def test_builds_prompt_with_extras(self):
        extras = [
            {"key": "E1", "name": "Brand Consistency", "description": "Adherence to brand guidelines..."},
            {"key": "E2", "name": "Target Audience Fit", "description": "Alignment with target audience..."},
        ]
        prompt = _build_extra_dimensions_prompt(extras)
        assert "E1" in prompt
        assert "Brand Consistency" in prompt
        assert "E2" in prompt

    def test_returns_empty_for_no_extras(self):
        prompt = _build_extra_dimensions_prompt([])
        assert prompt == ""

    def test_max_three_extras(self):
        extras = [{"key": f"E{i}", "name": f"Dim{i}", "description": f"Desc{i}"} for i in range(1, 6)]
        prompt = _build_extra_dimensions_prompt(extras)
        assert "E1" in prompt
        assert "E3" in prompt
        assert "E4" not in prompt  # Truncated


class TestParseExtraDimensions:
    def test_parse_includes_extras(self):
        raw = {}
        for i in range(1, 6):
            raw[f"L{i}"] = 0.5
            raw[f"L{i}_rationale"] = "ok"
            raw[f"L{i}_suggestion"] = "try"
            raw[f"L{i}_deviation_type"] = "traditional"
            raw[f"L{i}_observations"] = "obs"
            raw[f"L{i}_reference_technique"] = "tech"
        raw["E1"] = 0.82
        raw["E1_rationale"] = "strong brand"
        raw["E1_suggestion"] = "use more tokens"
        raw["E1_observations"] = "consistent palette"

        extra_keys = ["E1"]
        scores, rationales, suggestions, deviations, observations, ref_techniques = _parse_vlm_response(raw, extra_keys=extra_keys)
        assert "E1" in scores
        assert scores["E1"] == 0.82
