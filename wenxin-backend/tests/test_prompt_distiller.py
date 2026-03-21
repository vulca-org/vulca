"""Test PromptDistiller."""
from __future__ import annotations
import json
import sys
from unittest.mock import MagicMock, patch
import pytest
from app.prototype.digestion.prompt_distiller import PromptDistiller, PromptArchetype


def _mock_litellm_module():
    """Create a mock litellm module for injection into sys.modules."""
    m = MagicMock()
    m.__name__ = "litellm"
    return m


class TestPromptDistiller:
    def test_empty_sessions(self):
        d = PromptDistiller()
        assert d.distill([]) == []

    def test_low_scoring_ignored(self):
        sessions = [
            {"intent": "test art", "final_weighted_total": 0.3, "tradition": "default"}
        ]
        assert PromptDistiller().distill(sessions) == []

    def test_high_scoring_extracted(self):
        sessions = [
            {"intent": "landscape mountain painting", "final_weighted_total": 0.85, "tradition": "chinese_xieyi"},
            {"intent": "mountain landscape scene", "final_weighted_total": 0.80, "tradition": "chinese_xieyi"},
            {"intent": "abstract modern art", "final_weighted_total": 0.75, "tradition": "default"},
        ]
        archetypes = PromptDistiller().distill(sessions)
        assert len(archetypes) >= 1, "High-scoring sessions should produce archetypes"
        # Patterns should relate to the input intents (keyword or LLM-generated)
        all_patterns = " ".join(a.pattern.lower() for a in archetypes)
        assert "mountain" in all_patterns or "landscape" in all_patterns, (
            f"Expected mountain/landscape in patterns, got: {[a.pattern for a in archetypes]}"
        )

    def test_chinese_intent_keywords(self):
        """Chinese bigrams/trigrams should be extracted from intent text."""
        sessions = [
            {"intent": "水墨 landscape", "final_weighted_total": 0.85, "tradition": "chinese_xieyi"},
            {"intent": "水墨 painting style", "final_weighted_total": 0.80, "tradition": "chinese_xieyi"},
            {"intent": "水墨 art", "final_weighted_total": 0.78, "tradition": "chinese_xieyi"},
        ]
        archetypes = PromptDistiller().distill(sessions)
        assert len(archetypes) >= 1, "Should produce archetypes from Chinese intents"
        # Pattern should relate to 水墨/ink wash (keyword or LLM-generated)
        all_patterns = " ".join(a.pattern for a in archetypes)
        assert "水墨" in all_patterns or "ink" in all_patterns.lower() or "wash" in all_patterns.lower(), (
            f"Expected ink wash related pattern, got: {[a.pattern for a in archetypes]}"
        )

    def test_extract_keywords_mixed(self):
        """Mixed English+Chinese text should extract both."""
        keywords = PromptDistiller._extract_keywords("watercolor 水墨山水 landscape 传统意境")
        en_kw = [w for w in keywords if w.isascii()]
        zh_kw = [w for w in keywords if any(c >= '\u4e00' and c <= '\u9fff' for c in w)]
        assert len(en_kw) > 0, "Should extract English keywords"
        assert len(zh_kw) > 0, "Should extract Chinese keywords"

    def test_archetype_to_dict(self):
        a = PromptArchetype(pattern="test", avg_score=0.8, count=3)
        d = a.to_dict()
        assert d["pattern"] == "test"
        assert d["avg_score"] == 0.8

    def test_archetype_to_dict_with_llm_fields(self):
        """LLM-enriched archetypes include insights, guidance, anti_patterns."""
        a = PromptArchetype(
            pattern="ink wash landscape",
            avg_score=0.85,
            count=5,
            traditions=["chinese_xieyi"],
            example_prompts=["mountain ink wash"],
            insights="Ink wash landscapes succeed through mastery of negative space.",
            evaluation_guidance={
                "L1": "Look for balanced composition with generous negative space",
                "L3": "Assess connection to literati painting tradition",
            },
            anti_patterns=["Overloading composition with too many elements"],
        )
        d = a.to_dict()
        assert d["insights"] == "Ink wash landscapes succeed through mastery of negative space."
        assert "L1" in d["evaluation_guidance"]
        assert "L3" in d["evaluation_guidance"]
        assert len(d["anti_patterns"]) == 1

    def test_archetype_to_dict_omits_empty_llm_fields(self):
        """Keyword-only archetypes omit LLM fields from dict."""
        a = PromptArchetype(pattern="mountain", avg_score=0.8, count=3)
        d = a.to_dict()
        assert "insights" not in d
        assert "evaluation_guidance" not in d
        assert "anti_patterns" not in d

    def test_keyword_fallback_when_no_api_key(self):
        """Without API key, distill uses keyword fallback."""
        sessions = [
            {"intent": "landscape mountain painting", "final_weighted_total": 0.85, "tradition": "chinese_xieyi"},
            {"intent": "mountain landscape scene", "final_weighted_total": 0.80, "tradition": "chinese_xieyi"},
        ]
        with patch.object(PromptDistiller, "_has_api_key", return_value=False):
            archetypes = PromptDistiller().distill(sessions)
        patterns = [a.pattern for a in archetypes]
        assert "mountain" in patterns or "landscape" in patterns
        # Keyword fallback produces no insights
        for a in archetypes:
            assert a.insights == ""

    def test_llm_mode_with_mock_response(self):
        """LLM mode parses structured JSON response into enriched archetypes."""
        sessions = [
            {"intent": "mountain landscape ink wash", "final_weighted_total": 0.85, "tradition": "chinese_xieyi",
             "final_scores": {"L1": 0.8, "L3": 0.9}},
            {"intent": "bamboo in wind ink wash", "final_weighted_total": 0.80, "tradition": "chinese_xieyi",
             "final_scores": {"L1": 0.75, "L3": 0.85}},
        ]

        llm_response = json.dumps([
            {
                "pattern": "ink wash naturalism",
                "insights": "Traditional ink wash captures nature's essence through minimal strokes.",
                "evaluation_guidance": {
                    "L1": "Assess negative space balance",
                    "L2": "Check ink consistency and brush control",
                    "L3": "Verify literati tradition connection",
                    "L4": "Evaluate spiritual depth of expression",
                    "L5": "Consider Daoist philosophical undertones",
                },
                "anti_patterns": [
                    "Over-rendering that loses spontaneity",
                    "Ignoring the poem-painting unity tradition",
                ],
            }
        ])

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = llm_response

        mock_litellm = _mock_litellm_module()
        mock_litellm.completion.return_value = mock_response

        with patch.object(PromptDistiller, "_has_api_key", return_value=True), \
             patch.dict(sys.modules, {"litellm": mock_litellm}):
            archetypes = PromptDistiller().distill(sessions)

        assert len(archetypes) == 1
        a = archetypes[0]
        assert a.pattern == "ink wash naturalism"
        assert "minimal strokes" in a.insights
        assert "L1" in a.evaluation_guidance
        assert "L5" in a.evaluation_guidance
        assert len(a.anti_patterns) == 2
        assert a.traditions == ["chinese_xieyi"]

    def test_llm_failure_falls_back_to_keywords(self):
        """When LLM call raises, gracefully falls back to keyword mode."""
        sessions = [
            {"intent": "landscape mountain painting", "final_weighted_total": 0.85, "tradition": "chinese_xieyi"},
            {"intent": "mountain landscape scene", "final_weighted_total": 0.80, "tradition": "chinese_xieyi"},
        ]

        mock_litellm = _mock_litellm_module()
        mock_litellm.completion.side_effect = ConnectionError("API unavailable")

        with patch.object(PromptDistiller, "_has_api_key", return_value=True), \
             patch.dict(sys.modules, {"litellm": mock_litellm}):
            archetypes = PromptDistiller().distill(sessions)

        # Should have keyword-based results
        patterns = [a.pattern for a in archetypes]
        assert "mountain" in patterns or "landscape" in patterns

    def test_parse_llm_response_with_markdown_fences(self):
        """LLM response wrapped in ```json fences should be parsed correctly."""
        d = PromptDistiller()
        content = '```json\n[{"pattern": "zen garden", "insights": "test", "evaluation_guidance": {}, "anti_patterns": []}]\n```'
        archetypes = d._parse_llm_response(content, "japanese_wabi_sabi", [
            {"intent": "zen garden", "final_weighted_total": 0.8},
        ])
        assert len(archetypes) == 1
        assert archetypes[0].pattern == "zen garden"

    def test_parse_llm_response_invalid_json(self):
        """Invalid JSON from LLM returns empty list."""
        d = PromptDistiller()
        archetypes = d._parse_llm_response("not json at all", "default", [])
        assert archetypes == []
