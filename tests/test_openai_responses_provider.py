"""Tests for the OpenAI Responses image tool provider."""
from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from vulca.providers.base import ImageProvider
from vulca.providers.openai_responses import OpenAIResponsesImageProvider


class _FakeResponses:
    def __init__(self):
        self.calls = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            id="resp_123",
            output=[
                SimpleNamespace(
                    id="ig_123",
                    type="image_generation_call",
                    result="aW1n",
                    revised_prompt="revised prompt",
                    status="completed",
                )
            ],
            usage=SimpleNamespace(input_tokens=7, output_tokens=11),
        )


class _FakeAsyncOpenAI:
    instances = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.responses = _FakeResponses()
        self.__class__.instances.append(self)


class _QuotaResponses:
    async def create(self, **kwargs):
        raise Exception("insufficient_quota")


class _QuotaAsyncOpenAI:
    def __init__(self, **kwargs):
        self.responses = _QuotaResponses()


def test_protocol_compliance():
    p = OpenAIResponsesImageProvider(api_key="test-key")
    assert isinstance(p, ImageProvider)


def test_insufficient_quota_is_not_retryable():
    import vulca.providers.openai_responses as module

    class InsufficientQuota(Exception):
        status_code = 429
        code = "insufficient_quota"

    assert module._is_retryable(InsufficientQuota("insufficient_quota")) is False


def test_generate_reports_openai_quota_block(monkeypatch):
    import vulca.providers.openai_responses as module

    monkeypatch.setattr(module, "AsyncOpenAI", _QuotaAsyncOpenAI)

    provider = OpenAIResponsesImageProvider(api_key="test-key")
    with pytest.raises(RuntimeError, match="quota exhausted"):
        asyncio.run(provider.generate("make a poster"))


def test_generate_uses_responses_image_tool(monkeypatch):
    import vulca.providers.openai_responses as module

    _FakeAsyncOpenAI.instances.clear()
    monkeypatch.setattr(module, "AsyncOpenAI", _FakeAsyncOpenAI)

    provider = OpenAIResponsesImageProvider(
        api_key="test-key",
        response_model="gpt-5.5",
        model="gpt-image-2",
    )
    result = asyncio.run(
        provider.generate(
            "make a poster",
            tradition="chinese_xieyi",
            width=1536,
            height=1024,
            quality="high",
            output_format="jpeg",
            previous_response_id="resp_prev",
        )
    )

    assert result.image_b64 == "aW1n"
    assert result.mime == "image/jpeg"
    assert result.metadata == {
        "provider": "openai-responses",
        "response_model": "gpt-5.5",
        "image_model": "gpt-image-2",
        "response_id": "resp_123",
        "tool_call_id": "ig_123",
        "revised_prompt": "revised prompt",
        "usage": {"input_tokens": 7, "output_tokens": 11},
    }

    client = _FakeAsyncOpenAI.instances[0]
    assert client.kwargs["api_key"] == "test-key"
    call = client.responses.calls[0]
    assert call["model"] == "gpt-5.5"
    assert call["previous_response_id"] == "resp_prev"
    assert call["tool_choice"] == {"type": "image_generation"}
    assert call["tools"] == [
        {
            "type": "image_generation",
            "model": "gpt-image-2",
            "size": "1536x1024",
            "quality": "high",
            "output_format": "jpeg",
            "action": "generate",
        }
    ]
    assert "chinese xieyi" in call["input"]
