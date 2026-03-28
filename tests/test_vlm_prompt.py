from vulca._vlm import _SYSTEM_PROMPT, _parse_vlm_response


class TestVLMPromptStructure:
    def test_prompt_has_observe_phase(self):
        assert "OBSERVE" in _SYSTEM_PROMPT or "observe" in _SYSTEM_PROMPT.lower()

    def test_prompt_has_evaluate_phase(self):
        assert "EVALUATE" in _SYSTEM_PROMPT or "evaluate" in _SYSTEM_PROMPT.lower()

    def test_prompt_requires_observations(self):
        assert "observations" in _SYSTEM_PROMPT.lower()

    def test_prompt_requires_reference_technique(self):
        assert "reference_technique" in _SYSTEM_PROMPT


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
