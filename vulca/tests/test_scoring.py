"""Tests for scoring subsystem -- model router, config, VLM re-export."""

from __future__ import annotations

import pytest


class TestModelRouter:
    def test_model_spec(self):
        from vulca.scoring.model_router import ModelSpec
        spec = ModelSpec(
            litellm_id="gemini/gemini-2.5-pro",
            display_name="Gemini Pro",
            cost_per_call_usd=0.001,
            supports_vlm=True,
        )
        assert spec.supports_vlm
        d = spec.to_dict()
        assert d["litellm_id"] == "gemini/gemini-2.5-pro"

    def test_models_catalog(self):
        from vulca.scoring.model_router import MODELS
        assert "gemini_direct" in MODELS
        assert MODELS["gemini_direct"].supports_vlm

    def test_default_layer_models(self):
        from vulca.scoring.model_router import DEFAULT_LAYER_MODELS
        assert "visual_perception" in DEFAULT_LAYER_MODELS
        assert "cultural_context" in DEFAULT_LAYER_MODELS
        assert len(DEFAULT_LAYER_MODELS) == 5

    def test_model_router_select(self):
        from vulca.scoring.model_router import ModelRouter
        router = ModelRouter(budget_remaining_usd=5.0)
        spec = router.select_model("visual_perception", requires_vlm=True)
        assert spec is not None
        assert spec.supports_vlm

    def test_model_router_budget_exceeded(self):
        from vulca.scoring.model_router import ModelRouter
        router = ModelRouter(budget_remaining_usd=0.0001)
        spec = router.select_model("visual_perception")
        assert spec is None

    def test_model_router_record_cost(self):
        from vulca.scoring.model_router import ModelRouter
        router = ModelRouter(budget_remaining_usd=1.0)
        router.record_cost(0.5)
        assert router.budget_remaining_usd == 0.5
        router.record_cost(1.0)
        assert router.budget_remaining_usd == 0.0

    def test_semantic_model_constants(self):
        from vulca.scoring.model_router import MODEL_VLM, MODEL_FAST, MODEL_DECISION
        assert "gemini" in MODEL_VLM
        assert "flash" in MODEL_FAST
        assert "flash" in MODEL_DECISION


class TestScoringConfig:
    def test_config_re_export(self):
        from vulca.scoring.config import CriticConfig, DIMENSIONS
        assert len(DIMENSIONS) == 5
        cc = CriticConfig()
        assert cc.pass_threshold == 0.4


class TestScoringVlm:
    def test_vlm_re_export(self):
        from vulca.scoring.vlm import score_image
        import inspect
        assert inspect.iscoroutinefunction(score_image)

    def test_tradition_guidance_available(self):
        from vulca.scoring.vlm import _TRADITION_GUIDANCE
        assert "chinese_xieyi" in _TRADITION_GUIDANCE
        assert len(_TRADITION_GUIDANCE) == 9


class TestScoringInit:
    def test_init_exports(self):
        from vulca.scoring import (
            CriticConfig, CritiqueOutput, DimensionScore,
            DIMENSIONS, LayerID, LayerState,
            ModelRouter, ModelSpec,
        )
        assert CriticConfig is not None
        assert len(DIMENSIONS) == 5
