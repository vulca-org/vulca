"""Tests for cultural tradition loader -- YAML loading, weight resolution."""

from __future__ import annotations

import pytest


class TestTraditionLoader:
    def test_reload_traditions(self):
        from vulca.cultural.loader import reload_traditions
        count = reload_traditions()
        # Should load the bundled YAML files (9 traditions excl. _template)
        assert count >= 8

    def test_get_all_traditions(self):
        from vulca.cultural.loader import get_all_traditions
        traditions = get_all_traditions()
        assert "default" in traditions
        assert "chinese_xieyi" in traditions
        assert len(traditions) >= 8

    def test_get_tradition(self):
        from vulca.cultural.loader import get_tradition
        tc = get_tradition("chinese_xieyi")
        assert tc is not None
        assert tc.name == "chinese_xieyi"
        assert "L5" in tc.weights_l
        # Xieyi should emphasize L5
        assert tc.weights_l.get("L5", 0) >= 0.25

    def test_get_tradition_not_found(self):
        from vulca.cultural.loader import get_tradition
        tc = get_tradition("nonexistent_tradition_xyz")
        assert tc is None

    def test_get_weights(self):
        from vulca.cultural.loader import get_weights
        weights = get_weights("chinese_xieyi")
        assert abs(sum(weights.values()) - 1.0) < 0.05
        assert "L1" in weights

    def test_get_weights_fallback(self):
        from vulca.cultural.loader import get_weights
        weights = get_weights("totally_unknown")
        assert abs(sum(weights.values()) - 1.0) < 0.05

    def test_get_known_traditions(self):
        from vulca.cultural.loader import get_known_traditions
        traditions = get_known_traditions()
        assert "chinese_xieyi" in traditions
        assert "default" in traditions
        assert len(traditions) >= 8

    def test_get_all_weight_tables(self):
        from vulca.cultural.loader import get_all_weight_tables
        tables = get_all_weight_tables()
        assert "default" in tables
        for name, weights in tables.items():
            total = sum(weights.values())
            assert abs(total - 1.0) < 0.05, f"{name} weights sum to {total}"

    def test_tradition_has_terminology(self):
        from vulca.cultural.loader import get_tradition
        tc = get_tradition("chinese_xieyi")
        if tc:
            # Chinese xieyi should have some terminology
            assert isinstance(tc.terminology, list)

    def test_tradition_weights_dim(self):
        from vulca.cultural.loader import get_tradition
        tc = get_tradition("default")
        if tc:
            wd = tc.weights_dim
            assert "visual_perception" in wd or "cultural_context" in wd


class TestIntentSubsystem:
    def test_intent_result_type(self):
        from vulca.intent.types import IntentResult
        ir = IntentResult(tradition="chinese_xieyi", context="test", confidence=0.9, raw_intent="test")
        assert ir.tradition == "chinese_xieyi"
        assert ir.confidence == 0.9

    def test_result_card_type(self):
        from vulca.intent.types import ResultCard
        rc = ResultCard(
            score=0.8, summary="Good", risk_level="low",
            dimensions={"L1": 0.8}, recommendations=[], tradition_used="default",
        )
        assert rc.score == 0.8

    def test_intent_agent_import(self):
        from vulca.intent import IntentAgent
        agent = IntentAgent.get()
        assert agent is not None

    def test_intent_agent_fallback(self):
        from vulca.intent.agent import IntentAgent
        result = IntentAgent._fallback("test intent")
        assert result.tradition == "default"
        assert result.confidence == 0.0
        assert result.raw_intent == "test intent"

    def test_intent_agent_parse_response_valid(self):
        from vulca.intent.agent import IntentAgent
        result = IntentAgent._parse_response('{"tradition": "chinese_xieyi", "confidence": 0.9}')
        assert result is not None
        assert result["tradition"] == "chinese_xieyi"

    def test_intent_agent_parse_response_markdown(self):
        from vulca.intent.agent import IntentAgent
        result = IntentAgent._parse_response('```json\n{"tradition": "default"}\n```')
        assert result is not None
        assert result["tradition"] == "default"

    def test_intent_agent_parse_response_invalid(self):
        from vulca.intent.agent import IntentAgent
        result = IntentAgent._parse_response("this is not json")
        assert result is None

    def test_intent_agent_parse_response_empty(self):
        from vulca.intent.agent import IntentAgent
        result = IntentAgent._parse_response("")
        assert result is None

    def test_intent_init_exports(self):
        from vulca.intent import IntentAgent, IntentResult, ResultCard
        assert IntentAgent is not None
        assert IntentResult is not None
        assert ResultCard is not None
