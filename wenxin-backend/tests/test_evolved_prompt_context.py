"""Tests for evolved prompt context injection (WU-2)."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from app.prototype.cultural_pipelines.cultural_weights import (
    get_evolved_prompt_context,
    _build_evolved_context,
    _evolved_prompt_cache,
)


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the cache before each test."""
    _evolved_prompt_cache.clear()
    yield
    _evolved_prompt_cache.clear()


class TestGetEvolvedPromptContext:
    def test_empty_evolved_context_returns_empty(self, tmp_path):
        """Returns empty string when evolved_context has 0 evolutions."""
        ctx_file = tmp_path / "evolved_context.json"
        ctx_file.write_text('{"tradition_weights":{},"version":1,"evolutions":0}')
        with patch(
            "app.prototype.cultural_pipelines.cultural_weights._EVOLVED_CONTEXT_PATH",
            str(ctx_file),
        ):
            result = get_evolved_prompt_context("default")
        assert result == ""

    def test_returns_string(self):
        """Always returns a string."""
        result = get_evolved_prompt_context("nonexistent_tradition")
        assert isinstance(result, str)

    def test_cache_works(self):
        """Second call uses cache and returns same result."""
        r1 = get_evolved_prompt_context("default")
        r2 = get_evolved_prompt_context("default")
        assert r1 == r2


class TestBuildEvolvedContext:
    def test_no_file(self, tmp_path):
        """Returns empty when file doesn't exist."""
        with patch(
            "app.prototype.cultural_pipelines.cultural_weights._EVOLVED_CONTEXT_PATH",
            str(tmp_path / "nonexistent.json"),
        ):
            result = _build_evolved_context("default", 200)
        assert result == ""

    def test_zero_evolutions(self, tmp_path):
        """Returns empty when evolutions is 0."""
        ctx_file = tmp_path / "evolved_context.json"
        ctx_file.write_text(json.dumps({
            "tradition_weights": {},
            "version": 1,
            "evolutions": 0,
        }))
        with patch(
            "app.prototype.cultural_pipelines.cultural_weights._EVOLVED_CONTEXT_PATH",
            str(ctx_file),
        ):
            result = _build_evolved_context("default", 200)
        assert result == ""

    def test_with_evolved_data(self, tmp_path):
        """Returns formatted context when data exists."""
        ctx_data = {
            "tradition_weights": {
                "chinese_xieyi": {
                    "cultural_context": 0.30,
                    "visual_perception": 0.25,
                    "philosophical_aesthetic": 0.20,
                    "technical_analysis": 0.15,
                    "critical_interpretation": 0.10,
                },
            },
            "version": 2,
            "evolutions": 3,
            "prompt_contexts": {
                "chinese_xieyi": {"top_keywords": ["ink", "brush", "landscape", "qi"]}
            },
            "cultures": {
                "Modern Ink Fusion": {"tradition": "chinese_xieyi"},
            },
        }
        ctx_file = tmp_path / "evolved_context.json"
        ctx_file.write_text(json.dumps(ctx_data))

        with patch(
            "app.prototype.cultural_pipelines.cultural_weights._EVOLVED_CONTEXT_PATH",
            str(ctx_file),
        ):
            result = _build_evolved_context("chinese_xieyi", 200)

        assert "[Evolved Context]" in result
        assert "Successful patterns" in result
        assert "ink" in result
        assert "Emerged concepts" in result
        assert "Modern Ink Fusion" in result
        assert "Priority dimensions" in result

    def test_cultures_as_list(self, tmp_path):
        """Handles cultures stored as list format."""
        ctx_data = {
            "tradition_weights": {},
            "version": 2,
            "evolutions": 1,
            "cultures": [
                {"name": "Neo-Brushwork", "tradition": "chinese_xieyi"},
            ],
        }
        ctx_file = tmp_path / "evolved_context.json"
        ctx_file.write_text(json.dumps(ctx_data))

        with patch(
            "app.prototype.cultural_pipelines.cultural_weights._EVOLVED_CONTEXT_PATH",
            str(ctx_file),
        ):
            result = _build_evolved_context("chinese_xieyi", 200)

        assert "Neo-Brushwork" in result


class TestSystemPromptIntegration:
    def test_agent_runtime_get_system_prompt(self):
        """Verify _get_system_prompt returns a string."""
        from app.prototype.agents.agent_runtime import _get_system_prompt
        prompt = _get_system_prompt("cultural_context", "default")
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_zero_regression(self):
        """When no evolved data, prompts should be identical to base."""
        from app.prototype.agents.agent_runtime import _get_system_prompt, _BASE_SYSTEM_PROMPTS

        # Patch at source — lazy import in _get_system_prompt reads from this module
        with patch(
            "app.prototype.cultural_pipelines.cultural_weights.get_evolved_prompt_context",
            return_value="",
        ):
            for layer in _BASE_SYSTEM_PROMPTS:
                prompt = _get_system_prompt(layer, "default")
                assert prompt == _BASE_SYSTEM_PROMPTS[layer]

    def test_queen_system_prompt_callable(self):
        """QueenLLMAgent._system_prompt accepts tradition parameter."""
        from app.prototype.agents.queen_llm import QueenLLMAgent
        agent = QueenLLMAgent()
        prompt = agent._system_prompt(tradition="default")
        assert isinstance(prompt, str)
        assert "Queen" in prompt
        assert "JSON" in prompt
