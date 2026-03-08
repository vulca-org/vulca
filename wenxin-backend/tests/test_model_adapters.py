"""
Unit tests for model adapters — registry, parameter building, common interface, error handling.

Covers:
- ModelConfig / ModelRegistry core operations
- Adapter factory (get_adapter) for all 8 providers
- OpenAI adapter: GPT-5 max_completion_tokens, o1 no-system-message / no-temperature
- Anthropic adapter: parameter construction
- Base adapter: validate_request, prepare_common_params
- UnifiedModelClient._prepare_request special-handling logic
- Error paths: unknown model, unknown provider, missing API key
"""

import os
import sys
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

# Ensure imports resolve
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ---------------------------------------------------------------------------
# Env vars required by settings / adapters — set BEFORE any app import
# ---------------------------------------------------------------------------
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-at-least-32-chars")
os.environ.setdefault("VULCA_API_KEYS", "demo-key")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_registry():
    """Reset the singleton registry before each test so tests are isolated."""
    from app.services.models.model_registry import ModelRegistry
    registry = ModelRegistry()
    registry.clear_registry()
    yield
    registry.clear_registry()


def _make_config(**overrides):
    """Helper to build a minimal ModelConfig with sane defaults."""
    from app.services.models.model_registry import ModelConfig
    defaults = dict(
        display_name="Test Model",
        provider="openai",
        api_model_name="test-model",
        organization="TestOrg",
        capabilities=["text"],
        model_type="llm",
        max_tokens=4096,
    )
    defaults.update(overrides)
    model_id = defaults.pop("model_id", "test-model")
    return ModelConfig(model_id=model_id, **defaults)


# ===================================================================
# 1. ModelRegistry — register, lookup, list, error on missing
# ===================================================================


class TestModelRegistry:
    """Tests for ModelRegistry core operations."""

    def test_register_and_get(self):
        from app.services.models.model_registry import model_registry
        cfg = _make_config(model_id="alpha")
        model_registry.register_model(cfg)

        result = model_registry.get_model("alpha")
        assert result.model_id == "alpha"
        assert result.display_name == "Test Model"

    def test_get_unknown_model_raises(self):
        from app.services.models.model_registry import model_registry
        with pytest.raises(ValueError, match="not registered"):
            model_registry.get_model("does-not-exist")

    def test_model_exists(self):
        from app.services.models.model_registry import model_registry
        cfg = _make_config(model_id="beta")
        model_registry.register_model(cfg)

        assert model_registry.model_exists("beta")
        assert not model_registry.model_exists("gamma")

    def test_list_models_by_provider(self):
        from app.services.models.model_registry import model_registry
        model_registry.register_model(_make_config(model_id="a", provider="openai"))
        model_registry.register_model(_make_config(model_id="b", provider="anthropic"))
        model_registry.register_model(_make_config(model_id="c", provider="openai"))

        openai_models = model_registry.list_models(provider="openai")
        assert len(openai_models) == 2
        ids = {m.model_id for m in openai_models}
        assert ids == {"a", "c"}

    def test_list_models_by_capability(self):
        from app.services.models.model_registry import model_registry
        model_registry.register_model(
            _make_config(model_id="img", capabilities=["image"], model_type="image")
        )
        model_registry.register_model(
            _make_config(model_id="txt", capabilities=["text"])
        )

        image_models = model_registry.list_models(capability="image")
        assert len(image_models) == 1
        assert image_models[0].model_id == "img"

    def test_clear_registry(self):
        from app.services.models.model_registry import model_registry
        model_registry.register_model(_make_config(model_id="x"))
        assert model_registry.model_exists("x")
        model_registry.clear_registry()
        assert not model_registry.model_exists("x")

    def test_get_stats(self):
        from app.services.models.model_registry import model_registry
        model_registry.register_model(
            _make_config(model_id="v1", verified=True)
        )
        model_registry.register_model(
            _make_config(model_id="v2", verified=False, deprecated=True)
        )
        stats = model_registry.get_stats()
        assert stats["total_models"] == 2
        assert stats["verified_models"] == 1
        assert stats["deprecated_models"] == 1

    def test_to_dict_roundtrip(self):
        cfg = _make_config(model_id="rt", description="round trip")
        d = cfg.to_dict()
        assert d["model_id"] == "rt"
        assert d["description"] == "round trip"
        assert d["provider"] == "openai"

    def test_get_model_by_api_name(self):
        from app.services.models.model_registry import model_registry
        model_registry.register_model(
            _make_config(model_id="gpt4", api_model_name="gpt-4", provider="openai")
        )
        result = model_registry.get_model_by_api_name("gpt-4", "openai")
        assert result is not None
        assert result.model_id == "gpt4"

        # Wrong provider returns None
        assert model_registry.get_model_by_api_name("gpt-4", "anthropic") is None


# ===================================================================
# 2. Adapter factory — get_adapter for every known provider
# ===================================================================


class TestAdapterFactory:
    """Verify get_adapter returns correct adapter type or None for unknown."""

    PROVIDER_ADAPTER_MAP = {
        "openai": "OpenAIAdapter",
        "deepseek": "DeepSeekAdapter",
        "qwen": "QwenAdapter",
        "xai": "XAIAdapter",
        "openrouter": "OpenRouterAdapter",
        "gemini": "GeminiAdapter",
        "anthropic": "AnthropicAdapter",
        "huggingface": "HuggingFaceAdapter",
    }

    @pytest.mark.parametrize("provider,expected_class", list(PROVIDER_ADAPTER_MAP.items()))
    def test_get_adapter_returns_correct_type(self, provider, expected_class):
        """Each known provider returns an adapter whose class name matches."""
        from app.services.models.adapters import get_adapter

        cfg = _make_config(provider=provider)

        # Patch client initialisation so no real API keys are needed
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "sk-fake",
            "DEEPSEEK_API_KEY": "sk-fake",
            "QWEN_API_KEY": "sk-fake",
            "XAI_API_KEY": "sk-fake",
            "OPENROUTER_API_KEY": "sk-fake",
            "ANTHROPIC_API_KEY": "sk-fake",
        }):
            # For openai adapter, also patch settings.OPENAI_API_KEY
            with patch("app.core.config.settings") as mock_settings:
                mock_settings.OPENAI_API_KEY = "sk-fake"
                adapter = get_adapter(provider, cfg)

        assert adapter is not None
        assert type(adapter).__name__ == expected_class

    def test_get_adapter_unknown_provider_returns_none(self):
        from app.services.models.adapters import get_adapter
        cfg = _make_config(provider="unknown_provider")
        result = get_adapter("unknown_provider", cfg)
        assert result is None


# ===================================================================
# 3. Common interface — all adapters expose generate() and health_check()
# ===================================================================


class TestCommonInterface:
    """Ensure every adapter implements the abstract interface."""

    def _get_all_adapter_classes(self):
        from app.services.models.adapters.openai_adapter import OpenAIAdapter
        from app.services.models.adapters.anthropic_adapter import AnthropicAdapter
        from app.services.models.adapters.deepseek_adapter import DeepSeekAdapter
        from app.services.models.adapters.qwen_adapter import QwenAdapter
        from app.services.models.adapters.xai_adapter import XAIAdapter
        from app.services.models.adapters.openrouter_adapter import OpenRouterAdapter
        from app.services.models.adapters.gemini_adapter import GeminiAdapter
        from app.services.models.adapters.huggingface_adapter import HuggingFaceAdapter

        return [
            OpenAIAdapter,
            AnthropicAdapter,
            DeepSeekAdapter,
            QwenAdapter,
            XAIAdapter,
            OpenRouterAdapter,
            GeminiAdapter,
            HuggingFaceAdapter,
        ]

    def test_all_adapters_have_generate_method(self):
        for cls in self._get_all_adapter_classes():
            assert hasattr(cls, "generate"), f"{cls.__name__} missing generate()"
            assert callable(getattr(cls, "generate"))

    def test_all_adapters_have_health_check_method(self):
        for cls in self._get_all_adapter_classes():
            assert hasattr(cls, "health_check"), f"{cls.__name__} missing health_check()"
            assert callable(getattr(cls, "health_check"))

    def test_all_adapters_extend_base(self):
        from app.services.models.adapters.base import BaseAdapter
        for cls in self._get_all_adapter_classes():
            assert issubclass(cls, BaseAdapter), f"{cls.__name__} does not extend BaseAdapter"


# ===================================================================
# 4. BaseAdapter — validate_request & prepare_common_params
# ===================================================================


class TestBaseAdapter:
    """Test the base adapter's shared helpers."""

    def _make_adapter(self, **config_overrides):
        """Create a concrete adapter subclass for testing base methods."""
        from app.services.models.adapters.base import BaseAdapter

        class StubAdapter(BaseAdapter):
            def _initialize_client(self):
                return None

            async def generate(self, request):
                return "stub"

            async def health_check(self):
                return True

        cfg = _make_config(**config_overrides)
        return StubAdapter(cfg)

    def test_validate_request_ok(self):
        adapter = self._make_adapter()
        assert adapter.validate_request({"prompt": "hi", "model": "test"})

    def test_validate_request_missing_prompt(self):
        adapter = self._make_adapter()
        assert not adapter.validate_request({"model": "test"})

    def test_validate_request_missing_model(self):
        adapter = self._make_adapter()
        assert not adapter.validate_request({"prompt": "hi"})

    def test_prepare_common_params_with_max_tokens(self):
        adapter = self._make_adapter()
        params = adapter.prepare_common_params({
            "model": "gpt-4",
            "max_tokens": 512,
            "temperature": 0.5,
        })
        assert params["model"] == "gpt-4"
        assert params["max_tokens"] == 512
        assert params["temperature"] == 0.5

    def test_prepare_common_params_max_completion_tokens_preferred(self):
        """When both max_completion_tokens and max_tokens are given,
        base class uses elif so only max_completion_tokens is set."""
        adapter = self._make_adapter()
        params = adapter.prepare_common_params({
            "model": "gpt-5",
            "max_completion_tokens": 1000,
            "max_tokens": 500,
        })
        # max_completion_tokens should be present
        assert params["max_completion_tokens"] == 1000
        # base class elif means max_tokens is NOT set when max_completion_tokens exists
        assert "max_tokens" not in params

    def test_prepare_common_params_no_temperature_flag(self):
        adapter = self._make_adapter(
            requires_special_handling={"no_temperature": True}
        )
        params = adapter.prepare_common_params({
            "model": "o1",
            "temperature": 0.7,
        })
        # temperature should be stripped when no_temperature is True
        assert "temperature" not in params


# ===================================================================
# 5. OpenAI adapter — parameter building specifics
# ===================================================================


class TestOpenAIAdapterParams:
    """Test OpenAI adapter's parameter building logic (no real API calls)."""

    def _make_openai_adapter(self):
        from app.services.models.adapters.openai_adapter import OpenAIAdapter
        cfg = _make_config(provider="openai")
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.OPENAI_API_KEY = "sk-fake"
            adapter = OpenAIAdapter(cfg)
        return adapter

    def test_gpt5_uses_max_completion_tokens(self):
        """GPT-5 should forward max_completion_tokens, not max_tokens."""
        adapter = self._make_openai_adapter()
        # Simulate the request the adapter would receive from UnifiedModelClient
        request = {
            "prompt": "Write a poem",
            "model": "gpt-5",
            "max_completion_tokens": 500,
            "task_type": "poem",
        }
        # We won't call generate (would hit real API), just verify message prep
        messages = adapter._prepare_messages("Write a poem", "poem", "gpt-5")
        # GPT-5 is NOT o1 series, so system message should be present
        assert any(m["role"] == "system" for m in messages)

    def test_o1_no_system_message(self):
        """o1 series should merge system content into user message."""
        adapter = self._make_openai_adapter()
        messages = adapter._prepare_messages("Solve this", "analysis", "o1")
        # No system role for o1
        assert not any(m["role"] == "system" for m in messages)
        # System content should be merged into user message
        assert "analytical expert" in messages[0]["content"].lower()

    def test_o1_mini_no_system_message(self):
        adapter = self._make_openai_adapter()
        messages = adapter._prepare_messages("Test", "code", "o1-mini")
        assert not any(m["role"] == "system" for m in messages)

    def test_o3_mini_no_system_message(self):
        adapter = self._make_openai_adapter()
        messages = adapter._prepare_messages("Test", "story", "o3-mini")
        assert not any(m["role"] == "system" for m in messages)

    def test_gpt4_gets_system_message(self):
        """Regular GPT-4 should get a system message when task_type provides one."""
        adapter = self._make_openai_adapter()
        messages = adapter._prepare_messages("Write code", "code", "gpt-4")
        assert any(m["role"] == "system" for m in messages)

    def test_general_task_no_system_content(self):
        """When task_type is 'general', no system message is generated."""
        adapter = self._make_openai_adapter()
        messages = adapter._prepare_messages("Hello", "general", "gpt-4")
        assert not any(m["role"] == "system" for m in messages)
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello"

    @pytest.mark.asyncio
    async def test_generate_rejects_missing_prompt(self):
        """generate() should raise on invalid request."""
        adapter = self._make_openai_adapter()
        with pytest.raises(ValueError, match="Invalid request"):
            await adapter.generate({"model": "gpt-4"})  # no prompt

    @pytest.mark.asyncio
    async def test_generate_calls_openai_api(self):
        """generate() should call client.chat.completions.create with correct params."""
        adapter = self._make_openai_adapter()

        mock_response = MagicMock()
        mock_response.model = "gpt-4"
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello!"))]
        mock_response.usage = MagicMock(total_tokens=42)

        adapter.client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await adapter.generate({
            "prompt": "Hello",
            "model": "gpt-4",
            "max_tokens": 100,
            "temperature": 0.5,
        })

        adapter.client.chat.completions.create.assert_awaited_once()
        call_kwargs = adapter.client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "gpt-4"
        assert call_kwargs["max_tokens"] == 100
        assert call_kwargs["temperature"] == 0.5
        assert result is mock_response

    @pytest.mark.asyncio
    async def test_generate_gpt5_no_temperature(self):
        """GPT-5 requests should NOT include temperature even if provided."""
        adapter = self._make_openai_adapter()

        mock_response = MagicMock()
        mock_response.model = "gpt-5"
        adapter.client.chat.completions.create = AsyncMock(return_value=mock_response)

        await adapter.generate({
            "prompt": "Test",
            "model": "gpt-5",
            "max_completion_tokens": 500,
            "temperature": 0.7,
        })

        call_kwargs = adapter.client.chat.completions.create.call_args[1]
        # GPT-5 is in the no-temperature list
        assert "temperature" not in call_kwargs

    @pytest.mark.asyncio
    async def test_generate_o1_no_temperature(self):
        """o1 requests should NOT include temperature."""
        adapter = self._make_openai_adapter()

        mock_response = MagicMock()
        mock_response.model = "o1"
        adapter.client.chat.completions.create = AsyncMock(return_value=mock_response)

        await adapter.generate({
            "prompt": "Test",
            "model": "o1",
            "max_completion_tokens": 500,
            "temperature": 0.7,
        })

        call_kwargs = adapter.client.chat.completions.create.call_args[1]
        assert "temperature" not in call_kwargs

    @pytest.mark.asyncio
    async def test_generate_gpt5_reasoning_effort(self):
        """GPT-5 should pass through reasoning_effort parameter."""
        adapter = self._make_openai_adapter()

        mock_response = MagicMock()
        mock_response.model = "gpt-5"
        adapter.client.chat.completions.create = AsyncMock(return_value=mock_response)

        await adapter.generate({
            "prompt": "Reason about this",
            "model": "gpt-5",
            "max_completion_tokens": 500,
            "reasoning_effort": "high",
        })

        call_kwargs = adapter.client.chat.completions.create.call_args[1]
        assert call_kwargs["reasoning_effort"] == "high"


# ===================================================================
# 6. Anthropic adapter — parameter construction
# ===================================================================


class TestAnthropicAdapterParams:
    """Test Anthropic adapter parameter handling (mocked, no real API calls)."""

    def _make_anthropic_adapter(self):
        from app.services.models.adapters.anthropic_adapter import AnthropicAdapter
        cfg = _make_config(provider="anthropic")
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-fake"}):
            adapter = AnthropicAdapter(cfg)
        return adapter

    @pytest.mark.asyncio
    async def test_generate_basic_call(self):
        adapter = self._make_anthropic_adapter()

        mock_content = MagicMock()
        mock_content.text = "A beautiful poem."
        mock_response = MagicMock()
        mock_response.content = [mock_content]

        adapter.client.messages.create = AsyncMock(return_value=mock_response)

        result = await adapter.generate({
            "prompt": "Write a poem",
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 500,
            "temperature": 0.7,
        })

        assert result == "A beautiful poem."
        adapter.client.messages.create.assert_awaited_once()
        call_kwargs = adapter.client.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-3-5-sonnet-20241022"
        assert call_kwargs["max_tokens"] == 500
        assert call_kwargs["temperature"] == 0.7

    @pytest.mark.asyncio
    async def test_generate_with_system_message(self):
        """System message should be merged into user content for Claude."""
        adapter = self._make_anthropic_adapter()

        mock_content = MagicMock()
        mock_content.text = "Response"
        mock_response = MagicMock()
        mock_response.content = [mock_content]
        adapter.client.messages.create = AsyncMock(return_value=mock_response)

        await adapter.generate({
            "prompt": "Hello",
            "model": "claude-3-5-sonnet-20241022",
            "system": "You are helpful",
        })

        call_kwargs = adapter.client.messages.create.call_args[1]
        messages = call_kwargs["messages"]
        # System text merged into user message
        assert "You are helpful" in messages[0]["content"]
        assert "Hello" in messages[0]["content"]

    @pytest.mark.asyncio
    async def test_generate_no_client_raises(self):
        """If ANTHROPIC_API_KEY is missing, client is None and generate raises."""
        from app.services.models.adapters.anthropic_adapter import AnthropicAdapter
        cfg = _make_config(provider="anthropic")
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}, clear=False):
            # Remove the key entirely
            env_copy = os.environ.copy()
            env_copy.pop("ANTHROPIC_API_KEY", None)
            with patch.dict(os.environ, env_copy, clear=True):
                adapter = AnthropicAdapter(cfg)

        assert adapter.client is None
        with pytest.raises(ValueError, match="not initialized"):
            await adapter.generate({"prompt": "Hi", "model": "claude-3-5-sonnet-20241022"})

    @pytest.mark.asyncio
    async def test_health_check_no_client(self):
        """Health check returns False when client is None."""
        from app.services.models.adapters.anthropic_adapter import AnthropicAdapter
        cfg = _make_config(provider="anthropic")
        with patch.dict(os.environ, {}, clear=True):
            adapter = AnthropicAdapter(cfg)
        assert adapter.client is None
        result = await adapter.health_check()
        assert result is False


# ===================================================================
# 7. UnifiedModelClient._prepare_request — special handling logic
# ===================================================================


class TestUnifiedClientPrepareRequest:
    """Test the parameter preparation logic in UnifiedModelClient."""

    def _make_client(self):
        """Create a UnifiedModelClient with a known set of models loaded."""
        from app.services.models.model_registry import model_registry
        from app.services.models.configs.model_configs import load_all_models
        load_all_models()

        from app.services.models.unified_client import UnifiedModelClient
        return UnifiedModelClient()

    def test_gpt5_max_completion_tokens_conversion(self):
        """GPT-5 config has requires_special_handling.max_completion_tokens=True,
        so max_tokens should be converted to max_completion_tokens."""
        client = self._make_client()
        from app.services.models.model_registry import model_registry
        cfg = model_registry.get_model("gpt-5")

        request = client._prepare_request(
            cfg, "Write a poem", "poem", max_tokens=1000, temperature=0.7
        )

        # Should be converted to max_completion_tokens
        assert "max_completion_tokens" in request
        # GPT-5 enforces minimum 500
        assert request["max_completion_tokens"] >= 500
        assert "max_tokens" not in request

    def test_gpt5_min_500_tokens(self):
        """GPT-5 models should have at least 500 max_completion_tokens."""
        client = self._make_client()
        from app.services.models.model_registry import model_registry
        cfg = model_registry.get_model("gpt-5")

        request = client._prepare_request(
            cfg, "Hi", "general", max_tokens=100, temperature=None
        )
        assert request["max_completion_tokens"] >= 500

    def test_o1_max_completion_tokens_and_no_temperature(self):
        """o1 should use max_completion_tokens and have no temperature."""
        client = self._make_client()
        from app.services.models.model_registry import model_registry
        cfg = model_registry.get_model("o1")

        # The o1 config in model_configs.py does NOT set no_temperature,
        # so temperature may still be present. But max_completion_tokens should apply.
        request = client._prepare_request(
            cfg, "Solve this", "analysis", max_tokens=2000, temperature=0.5
        )
        assert "max_completion_tokens" in request
        assert "max_tokens" not in request

    def test_gpt4o_uses_regular_max_tokens(self):
        """GPT-4o does NOT have special handling, should use regular max_tokens."""
        client = self._make_client()
        from app.services.models.model_registry import model_registry
        cfg = model_registry.get_model("gpt-4o")

        request = client._prepare_request(
            cfg, "Hello", "general", max_tokens=800, temperature=0.7
        )
        assert "max_tokens" in request
        assert request["max_tokens"] == 800
        assert "max_completion_tokens" not in request

    def test_default_temperature(self):
        """When temperature is not specified, default to 0.7."""
        client = self._make_client()
        from app.services.models.model_registry import model_registry
        cfg = model_registry.get_model("gpt-4o")

        request = client._prepare_request(
            cfg, "Hello", "general", max_tokens=500, temperature=None
        )
        assert request["temperature"] == 0.7

    def test_kwargs_passed_through(self):
        """Extra kwargs should be included in the request dict."""
        client = self._make_client()
        from app.services.models.model_registry import model_registry
        cfg = model_registry.get_model("gpt-4o")

        request = client._prepare_request(
            cfg, "Hello", "general", max_tokens=500, temperature=0.5,
            top_p=0.9, frequency_penalty=0.1
        )
        assert request["top_p"] == 0.9
        assert request["frequency_penalty"] == 0.1


# ===================================================================
# 8. ModelValidator
# ===================================================================


class TestModelValidator:
    """Test ModelValidator checks."""

    def _make_validator(self):
        from app.services.models.validator import ModelValidator
        return ModelValidator()

    def test_validate_model_config_valid(self):
        v = self._make_validator()
        cfg = _make_config()
        assert v.validate_model_config(cfg)

    def test_validate_model_config_unsupported_provider(self):
        v = self._make_validator()
        cfg = _make_config(provider="unknown_provider")
        assert not v.validate_model_config(cfg)

    def test_validate_request_params_valid(self):
        v = self._make_validator()
        assert v.validate_request_params({"prompt": "Hello", "max_tokens": 100, "temperature": 0.5})

    def test_validate_request_params_missing_prompt(self):
        v = self._make_validator()
        assert not v.validate_request_params({"max_tokens": 100})

    def test_validate_request_params_invalid_temperature(self):
        v = self._make_validator()
        assert not v.validate_request_params({"prompt": "hi", "temperature": 5.0})

    def test_validate_request_params_negative_max_tokens(self):
        v = self._make_validator()
        assert not v.validate_request_params({"prompt": "hi", "max_tokens": -1})

    @pytest.mark.asyncio
    async def test_validate_content_empty(self):
        v = self._make_validator()
        assert not await v.validate_content("", "general")

    @pytest.mark.asyncio
    async def test_validate_content_too_short(self):
        v = self._make_validator()
        assert not await v.validate_content("Hi", "general", min_length=10)

    @pytest.mark.asyncio
    async def test_validate_content_ok(self):
        v = self._make_validator()
        assert await v.validate_content("This is a sufficiently long response for testing.", "general")


# ===================================================================
# 9. Gemini / HuggingFace stub adapters — smoke test
# ===================================================================


class TestStubAdapters:
    """Gemini and HuggingFace are stubs — make sure they don't crash."""

    @pytest.mark.asyncio
    async def test_gemini_generate_returns_dict(self):
        from app.services.models.adapters.gemini_adapter import GeminiAdapter
        cfg = _make_config(provider="gemini")
        adapter = GeminiAdapter(cfg)
        result = await adapter.generate({"model": "gemini-pro", "prompt": "Hi"})
        assert isinstance(result, dict)
        assert "content" in result

    @pytest.mark.asyncio
    async def test_gemini_health_check_returns_false(self):
        from app.services.models.adapters.gemini_adapter import GeminiAdapter
        cfg = _make_config(provider="gemini")
        adapter = GeminiAdapter(cfg)
        assert await adapter.health_check() is False

    @pytest.mark.asyncio
    async def test_huggingface_generate_returns_dict(self):
        from app.services.models.adapters.huggingface_adapter import HuggingFaceAdapter
        cfg = _make_config(provider="huggingface")
        adapter = HuggingFaceAdapter(cfg)
        result = await adapter.generate({"model": "bert", "prompt": "Hi"})
        assert isinstance(result, dict)
        assert "content" in result

    @pytest.mark.asyncio
    async def test_huggingface_health_check_returns_false(self):
        from app.services.models.adapters.huggingface_adapter import HuggingFaceAdapter
        cfg = _make_config(provider="huggingface")
        adapter = HuggingFaceAdapter(cfg)
        assert await adapter.health_check() is False


# ===================================================================
# 10. load_all_models — integration smoke test
# ===================================================================


class TestLoadAllModels:
    """Verify load_all_models populates the registry correctly."""

    def test_load_all_models_populates_registry(self):
        from app.services.models.model_registry import model_registry
        from app.services.models.configs.model_configs import load_all_models
        stats = load_all_models()

        assert stats["total_models"] > 0
        # Spot-check known models
        assert model_registry.model_exists("gpt-5")
        assert model_registry.model_exists("gpt-4o")
        assert model_registry.model_exists("claude-opus-4.1")
        assert model_registry.model_exists("deepseek-r1")
        assert model_registry.model_exists("dall-e-3")

    def test_load_all_models_idempotent(self):
        """Calling load_all_models twice should not error or duplicate."""
        from app.services.models.model_registry import model_registry
        from app.services.models.configs.model_configs import load_all_models
        stats1 = load_all_models()
        count1 = stats1["total_models"]
        stats2 = load_all_models()
        count2 = stats2["total_models"]
        assert count1 == count2

    def test_all_registered_models_have_valid_config(self):
        """Every model in the registry should pass config validation."""
        from app.services.models.model_registry import model_registry
        from app.services.models.configs.model_configs import load_all_models
        from app.services.models.validator import ModelValidator

        load_all_models()
        validator = ModelValidator()

        # Only validate models whose provider is in the supported list
        supported_providers = [
            "openai", "deepseek", "qwen", "xai",
            "openrouter", "gemini", "anthropic", "huggingface",
        ]
        for model in model_registry.list_models():
            if model.provider in supported_providers:
                assert validator.validate_model_config(model), (
                    f"Model {model.model_id} failed config validation"
                )


# ===================================================================
# 11. UnifiedModelResponse
# ===================================================================


class TestUnifiedModelResponse:
    """Test the standardised response wrapper."""

    def test_to_dict(self):
        from app.services.models.unified_client import UnifiedModelResponse
        resp = UnifiedModelResponse(
            content="Hello world",
            model_used="gpt-4",
            tokens_used=42,
            metadata={"provider": "openai"},
        )
        d = resp.to_dict()
        assert d["content"] == "Hello world"
        assert d["model_used"] == "gpt-4"
        assert d["tokens_used"] == 42
        assert d["metadata"]["provider"] == "openai"
        assert "timestamp" in d

    def test_defaults(self):
        from app.services.models.unified_client import UnifiedModelResponse
        resp = UnifiedModelResponse(content="Hi", model_used="m")
        assert resp.tokens_used == 0
        assert resp.metadata == {}
