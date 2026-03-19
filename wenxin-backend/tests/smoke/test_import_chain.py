"""Unit 1: Backend import chain audit.

Verifies every critical import path used by the B2B API evaluate_routes
can be loaded without errors. No API keys or network access required.
"""

from __future__ import annotations

import importlib
import sys


# ---------------------------------------------------------------------------
# Core module import tests
# ---------------------------------------------------------------------------

class TestCoreImports:
    """Verify leaf modules load without ImportError / SyntaxError."""

    def test_evaluate_schemas(self):
        mod = importlib.import_module("app.prototype.api.evaluate_schemas")
        assert hasattr(mod, "EvaluateRequest")
        assert hasattr(mod, "EvaluateResponse")
        assert hasattr(mod, "IdentifyTraditionRequest")
        assert hasattr(mod, "IdentifyTraditionResponse")
        assert hasattr(mod, "KnowledgeBaseResponse")

    def test_auth(self):
        mod = importlib.import_module("app.prototype.api.auth")
        assert hasattr(mod, "verify_api_key")
        assert hasattr(mod, "RATE_LIMIT_PER_MINUTE")

    def test_image_utils(self):
        mod = importlib.import_module("app.prototype.tools.image_utils")
        assert hasattr(mod, "resolve_image_input")
        assert hasattr(mod, "cleanup_temp_image")
        assert hasattr(mod, "decode_base64_image")

    def test_cultural_weights(self):
        mod = importlib.import_module("app.prototype.cultural_pipelines.cultural_weights")
        assert hasattr(mod, "get_weights")
        assert hasattr(mod, "get_all_weight_tables")
        assert hasattr(mod, "KNOWN_TRADITIONS")
        assert hasattr(mod, "get_known_traditions")
        # Dynamic version must return a list
        assert isinstance(mod.get_known_traditions(), list)

    def test_tradition_loader(self):
        mod = importlib.import_module("app.prototype.cultural_pipelines.tradition_loader")
        assert hasattr(mod, "get_tradition")
        assert hasattr(mod, "get_all_traditions")
        assert hasattr(mod, "validate_tradition_yaml")

    def test_pipeline_router(self):
        mod = importlib.import_module("app.prototype.cultural_pipelines.pipeline_router")
        assert hasattr(mod, "CulturalPipelineRouter")
        assert hasattr(mod, "PipelineRoute")
        assert hasattr(mod, "PipelineVariant")

    def test_critic_config(self):
        mod = importlib.import_module("app.prototype.agents.critic_config")
        assert hasattr(mod, "CriticConfig")
        assert hasattr(mod, "DIMENSIONS")
        assert len(mod.DIMENSIONS) == 5

    def test_model_router(self):
        mod = importlib.import_module("app.prototype.agents.model_router")
        assert hasattr(mod, "MODELS")
        assert hasattr(mod, "ModelSpec")
        assert hasattr(mod, "ModelRouter")

    def test_model_constants_exported(self):
        """Verify model constants are accessible from model_router."""
        from app.prototype.agents.model_router import MODEL_VLM, MODEL_FAST, MODEL_DECISION
        assert isinstance(MODEL_VLM, str)
        assert isinstance(MODEL_FAST, str)
        assert isinstance(MODEL_DECISION, str)
        assert "gemini" in MODEL_VLM
        assert "gemini" in MODEL_FAST
        assert "gemini" in MODEL_DECISION

    def test_vlm_scoring(self):
        mod = importlib.import_module("vulca._vlm")
        assert hasattr(mod, "score_image")

    def test_scout_service(self):
        mod = importlib.import_module("app.prototype.tools.scout_service")
        assert hasattr(mod, "ScoutService")

    def test_scout_types(self):
        mod = importlib.import_module("app.prototype.tools.scout_types")
        assert hasattr(mod, "ScoutEvidence")

    def test_evidence_pack(self):
        mod = importlib.import_module("app.prototype.tools.evidence_pack")
        assert hasattr(mod, "EvidencePack")

    def test_terminology_loader(self):
        mod = importlib.import_module("app.prototype.tools.terminology_loader")
        assert hasattr(mod, "TerminologyLoader")

    def test_taboo_rule_engine(self):
        mod = importlib.import_module("app.prototype.tools.taboo_rule_engine")
        assert hasattr(mod, "TabooRuleEngine")

    def test_sample_matcher(self):
        mod = importlib.import_module("app.prototype.tools.sample_matcher")
        assert hasattr(mod, "SampleMatcher")

    def test_async_bridge(self):
        mod = importlib.import_module("app.prototype.utils.async_bridge")
        assert hasattr(mod, "run_async_from_sync")


# ---------------------------------------------------------------------------
# Full dependency chain tests (top-down)
# ---------------------------------------------------------------------------

class TestDependencyChains:
    """Verify multi-level import chains resolve correctly."""

    def test_evaluate_routes_full_chain(self):
        """The ultimate test: evaluate_routes.py imports everything."""
        mod = importlib.import_module("app.prototype.api.evaluate_routes")
        assert hasattr(mod, "evaluate_router")
        # Verify the router has the expected endpoints
        # Routes include the prefix /api/v1/ from APIRouter(prefix=...)
        routes = [r.path for r in mod.evaluate_router.routes]
        assert "/api/v1/knowledge-base" in routes
        assert "/api/v1/evaluate" in routes
        assert "/api/v1/identify-tradition" in routes

    def test_cultural_pipelines_init(self):
        """cultural_pipelines/__init__.py re-exports all public symbols."""
        mod = importlib.import_module("app.prototype.cultural_pipelines")
        assert hasattr(mod, "CulturalPipelineRouter")
        assert hasattr(mod, "get_weights")
        assert hasattr(mod, "get_all_traditions")
        assert hasattr(mod, "validate_tradition_yaml")

    def test_main_app_imports(self):
        """app.main imports and registers the evaluate_router."""
        mod = importlib.import_module("app.main")
        assert hasattr(mod, "app")
        # Check that evaluate_router is included
        route_paths = [r.path for r in mod.app.routes]
        assert any("/api/v1/knowledge-base" in p for p in route_paths), (
            f"evaluate_router not found in app routes: {route_paths}"
        )


# ---------------------------------------------------------------------------
# No circular import test
# ---------------------------------------------------------------------------

class TestNoCircularImports:
    """Ensure no circular import issues in the prototype package."""

    def test_reload_without_error(self):
        """Force-reload key modules to detect stale caches or circulars."""
        modules_to_check = [
            "app.prototype.agents.critic_config",
            "app.prototype.cultural_pipelines.cultural_weights",
            "app.prototype.cultural_pipelines.tradition_loader",
            "app.prototype.cultural_pipelines.pipeline_router",
            "app.prototype.api.evaluate_schemas",
            "app.prototype.api.auth",
        ]
        for name in modules_to_check:
            if name in sys.modules:
                importlib.reload(sys.modules[name])
            else:
                importlib.import_module(name)
