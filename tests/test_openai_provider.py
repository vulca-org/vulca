"""Tests for OpenAI provider — gpt-image-1 transparency support."""
import pytest
import inspect

from vulca.providers.openai_provider import OpenAIImageProvider


class TestOpenAIProviderConfig:
    def test_default_model_is_gpt_image_1(self):
        provider = OpenAIImageProvider(api_key="test")
        assert provider.model == "gpt-image-1"

    def test_supports_background_parameter(self):
        provider = OpenAIImageProvider(api_key="test")
        sig = inspect.signature(provider.generate)
        params = list(sig.parameters.keys())
        assert "background" in params, "generate() must accept background parameter"

    def test_legacy_dalle3_still_works(self):
        provider = OpenAIImageProvider(api_key="test", model="dall-e-3")
        assert provider.model == "dall-e-3"
