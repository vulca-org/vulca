"""Test SessionDigest cultural features — Tier-1 (rule-based) and Tier-2 (LLM async).

Covers:
- Tier-1 extraction: synchronous, no LLM
- Tier-2 async extraction with mocked litellm
- Tier-2 failure graceful degradation
- Background enrichment integration
- SessionDigest field compatibility
"""
from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.prototype.session.types import RoundSnapshot, SessionDigest


# ─── Tier-1 (rule-based) tests ───


class TestSessionDigestExtensions:
    def test_new_fields_defaults(self):
        digest = SessionDigest()
        assert digest.cultural_features == {}
        assert digest.critic_insights == []
        assert digest.candidate_choice_index == -1
        assert digest.time_to_select_ms == 0
        assert digest.downloaded is False

    def test_new_fields_in_to_dict(self):
        digest = SessionDigest(
            cultural_features={"l5_emphasis": 0.85},
            critic_insights=["strong L5"],
            candidate_choice_index=2,
            time_to_select_ms=3500,
            downloaded=True,
        )
        d = digest.to_dict()
        assert d["cultural_features"] == {"l5_emphasis": 0.85}
        assert d["critic_insights"] == ["strong L5"]
        assert d["candidate_choice_index"] == 2
        assert d["time_to_select_ms"] == 3500
        assert d["downloaded"] is True

    def test_backward_compat_no_new_fields(self):
        """Existing code that doesn't pass new fields should still work."""
        digest = SessionDigest(
            session_id="test-123",
            mode="create",
            tradition="chinese_xieyi",
        )
        d = digest.to_dict()
        assert d["session_id"] == "test-123"
        assert d["cultural_features"] == {}

    def test_mixed_tier1_and_tier2_features(self):
        """cultural_features dict can hold both numeric (Tier-1) and list (Tier-2) values."""
        digest = SessionDigest(
            cultural_features={
                "tradition_specificity": 0.8,
                "l5_emphasis": 0.9,
                "style_elements": ["water ink", "negative space"],
                "emotional_tone": ["serene"],
            }
        )
        d = digest.to_dict()
        assert d["cultural_features"]["tradition_specificity"] == 0.8
        assert d["cultural_features"]["style_elements"] == ["water ink", "negative space"]


class TestExtractCulturalFeaturesTier1:
    def test_basic_extraction(self):
        from app.prototype.digestion.feature_extractor import extract_cultural_features as _extract_cultural_features
        features = _extract_cultural_features(
            tradition="chinese_xieyi",
            final_scores={"L1": 0.8, "L2": 0.7, "L3": 0.9, "L4": 0.6, "L5": 0.85},
            risk_flags=[],
        )
        assert features["tradition_specificity"] == 0.8
        assert "l5_emphasis" in features
        assert "avg_score" in features
        assert features["risk_level"] == 0.0

    def test_default_tradition_lower_specificity(self):
        from app.prototype.digestion.feature_extractor import extract_cultural_features as _extract_cultural_features
        features = _extract_cultural_features("default", {"L1": 0.5}, [])
        assert features["tradition_specificity"] == 0.3

    def test_empty_scores(self):
        from app.prototype.digestion.feature_extractor import extract_cultural_features as _extract_cultural_features
        features = _extract_cultural_features("default", {}, [])
        assert features == {}

    def test_risk_flags_increase_risk_level(self):
        from app.prototype.digestion.feature_extractor import extract_cultural_features as _extract_cultural_features
        features = _extract_cultural_features(
            "chinese_xieyi",
            {"L1": 0.5},
            ["[critical] taboo", "[high] sensitive"],
        )
        assert features["risk_level"] == 0.5

    def test_l5_emphasis_calculation(self):
        from app.prototype.digestion.feature_extractor import extract_cultural_features as _extract_cultural_features
        features = _extract_cultural_features(
            "japanese_ukiyoe",
            {"L1": 1.0, "L5": 0.5},
            [],
        )
        assert features["l5_emphasis"] == 0.5

    def test_cultural_depth_from_l3(self):
        from app.prototype.digestion.feature_extractor import extract_cultural_features as _extract_cultural_features
        features = _extract_cultural_features(
            "chinese_xieyi",
            {"L1": 0.5, "L3": 0.75},
            [],
        )
        assert features["cultural_depth"] == 0.75

    def test_returns_dict_type(self):
        """Tier-1 returns a plain dict (not dict[str, float] exclusively)."""
        from app.prototype.digestion.feature_extractor import extract_cultural_features as _extract_cultural_features
        features = _extract_cultural_features("default", {"L1": 0.5}, [])
        assert isinstance(features, dict)


# ─── Tier-2 (LLM async) tests ───


class TestExtractCulturalFeaturesAsyncTier2:
    """Test _extract_cultural_features_async with mocked litellm."""

    @pytest.mark.asyncio
    async def test_successful_llm_extraction(self):
        """LLM returns valid JSON with 4 expected keys."""
        from app.prototype.api.create_routes import _extract_cultural_features_async

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "style_elements": ["water ink", "negative space"],
            "emotional_tone": ["serene", "contemplative"],
            "technique_markers": ["wet-on-wet"],
            "cultural_references": ["Song dynasty landscape"],
        })

        mock_litellm = MagicMock()
        mock_litellm.acompletion = AsyncMock(return_value=mock_response)

        with patch.dict("sys.modules", {"litellm": mock_litellm}):
            result = await _extract_cultural_features_async(
                intent="Paint a serene mountain landscape in Song dynasty style",
                tradition="chinese_shanshui",
            )

        assert "style_elements" in result
        assert "emotional_tone" in result
        assert "technique_markers" in result
        assert "cultural_references" in result
        assert result["style_elements"] == ["water ink", "negative space"]
        assert result["emotional_tone"] == ["serene", "contemplative"]

    @pytest.mark.asyncio
    async def test_llm_returns_markdown_fenced_json(self):
        """LLM wraps JSON in markdown code fences — should still parse."""
        from app.prototype.api.create_routes import _extract_cultural_features_async

        fenced_json = '```json\n{"style_elements": ["impasto"], "emotional_tone": ["dramatic"], "technique_markers": [], "cultural_references": ["Baroque"]}\n```'
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = fenced_json

        mock_litellm = MagicMock()
        mock_litellm.acompletion = AsyncMock(return_value=mock_response)

        with patch.dict("sys.modules", {"litellm": mock_litellm}):
            result = await _extract_cultural_features_async(
                intent="Create a dramatic oil painting",
                tradition="western_baroque",
            )

        assert result["style_elements"] == ["impasto"]
        assert result["cultural_references"] == ["Baroque"]

    @pytest.mark.asyncio
    async def test_empty_intent_returns_empty(self):
        """Empty intent string should return empty dict without calling LLM."""
        from app.prototype.api.create_routes import _extract_cultural_features_async

        result = await _extract_cultural_features_async(intent="", tradition="default")
        assert result == {}

    @pytest.mark.asyncio
    async def test_whitespace_only_intent_returns_empty(self):
        """Whitespace-only intent should return empty dict."""
        from app.prototype.api.create_routes import _extract_cultural_features_async

        result = await _extract_cultural_features_async(intent="   ", tradition="default")
        assert result == {}

    @pytest.mark.asyncio
    async def test_llm_failure_graceful_degradation(self):
        """If litellm raises an exception, return empty dict (no crash)."""
        from app.prototype.api.create_routes import _extract_cultural_features_async

        mock_litellm = MagicMock()
        mock_litellm.acompletion = AsyncMock(side_effect=Exception("API quota exceeded"))

        with patch.dict("sys.modules", {"litellm": mock_litellm}):
            result = await _extract_cultural_features_async(
                intent="Paint something beautiful",
                tradition="default",
            )

        assert result == {}

    @pytest.mark.asyncio
    async def test_llm_returns_invalid_json(self):
        """If LLM returns non-JSON, gracefully degrade."""
        from app.prototype.api.create_routes import _extract_cultural_features_async

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Sorry, I cannot process this request."

        mock_litellm = MagicMock()
        mock_litellm.acompletion = AsyncMock(return_value=mock_response)

        with patch.dict("sys.modules", {"litellm": mock_litellm}):
            result = await _extract_cultural_features_async(
                intent="Something abstract",
                tradition="default",
            )

        assert result == {}

    @pytest.mark.asyncio
    async def test_llm_returns_partial_keys(self):
        """LLM returns some but not all keys — missing ones get empty lists."""
        from app.prototype.api.create_routes import _extract_cultural_features_async

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "style_elements": ["minimalist"],
            # Missing: emotional_tone, technique_markers, cultural_references
        })

        mock_litellm = MagicMock()
        mock_litellm.acompletion = AsyncMock(return_value=mock_response)

        with patch.dict("sys.modules", {"litellm": mock_litellm}):
            result = await _extract_cultural_features_async(
                intent="Minimalist composition",
                tradition="default",
            )

        assert result["style_elements"] == ["minimalist"]
        assert result["emotional_tone"] == []
        assert result["technique_markers"] == []
        assert result["cultural_references"] == []

    @pytest.mark.asyncio
    async def test_litellm_import_failure(self):
        """If litellm is not installed, gracefully degrade."""
        from app.prototype.api.create_routes import _extract_cultural_features_async

        with patch.dict("sys.modules", {"litellm": None}):
            result = await _extract_cultural_features_async(
                intent="Some intent",
                tradition="default",
            )

        assert result == {}


# ─── Background enrichment tests ───


class TestEnrichCulturalFeaturesBackground:
    """Test _enrich_cultural_features_background merging."""

    @pytest.mark.asyncio
    async def test_background_enrichment_merges_features(self):
        """Tier-2 features should be merged into existing Tier-1 features."""
        from app.prototype.api.create_routes import _enrich_cultural_features_background

        digest = SessionDigest(
            session_id="test-enrich",
            cultural_features={"tradition_specificity": 0.8, "avg_score": 0.75},
        )

        tier2_result = {
            "style_elements": ["calligraphic strokes"],
            "emotional_tone": ["meditative"],
            "technique_markers": ["dry brush"],
            "cultural_references": ["Zen Buddhism"],
        }

        with patch(
            "app.prototype.api.create_routes._extract_cultural_features_async",
            new_callable=AsyncMock,
            return_value=tier2_result,
        ):
            await _enrich_cultural_features_background(
                digest, intent="Zen calligraphy", tradition="japanese_zen",
            )

        # Tier-1 features preserved
        assert digest.cultural_features["tradition_specificity"] == 0.8
        assert digest.cultural_features["avg_score"] == 0.75
        # Tier-2 features merged
        assert digest.cultural_features["style_elements"] == ["calligraphic strokes"]
        assert digest.cultural_features["emotional_tone"] == ["meditative"]

    @pytest.mark.asyncio
    async def test_background_enrichment_failure_preserves_tier1(self):
        """If Tier-2 fails, Tier-1 features are untouched."""
        from app.prototype.api.create_routes import _enrich_cultural_features_background

        digest = SessionDigest(
            session_id="test-fail",
            cultural_features={"tradition_specificity": 0.8, "risk_level": 0.0},
        )

        with patch(
            "app.prototype.api.create_routes._extract_cultural_features_async",
            new_callable=AsyncMock,
            side_effect=Exception("Network error"),
        ):
            await _enrich_cultural_features_background(
                digest, intent="Something", tradition="default",
            )

        # Tier-1 features preserved, no Tier-2 keys added
        assert digest.cultural_features == {"tradition_specificity": 0.8, "risk_level": 0.0}

    @pytest.mark.asyncio
    async def test_background_enrichment_empty_tier2(self):
        """If Tier-2 returns empty dict, no changes to digest."""
        from app.prototype.api.create_routes import _enrich_cultural_features_background

        digest = SessionDigest(
            session_id="test-empty-t2",
            cultural_features={"tradition_specificity": 0.3},
        )

        with patch(
            "app.prototype.api.create_routes._extract_cultural_features_async",
            new_callable=AsyncMock,
            return_value={},
        ):
            await _enrich_cultural_features_background(
                digest, intent="", tradition="default",
            )

        assert digest.cultural_features == {"tradition_specificity": 0.3}
