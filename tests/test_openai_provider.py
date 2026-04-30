"""Tests for OpenAI provider — gpt-image-1 transparency support."""
import asyncio
import base64
import json
from contextlib import contextmanager

import httpx
import pytest
import inspect

from vulca.providers.openai_provider import OpenAIImageProvider


def _png_bytes() -> bytes:
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
        b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
        b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )


@contextmanager
def _httpx_with_handler(handler):
    transport = httpx.MockTransport(handler)
    original = httpx.AsyncClient

    def factory(*args, **kwargs):
        kwargs["transport"] = transport
        return original(*args, **kwargs)

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(httpx, "AsyncClient", factory)
        yield


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


def test_gpt_image_2_drops_input_fidelity_from_edit_form():
    captured_bodies: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_bodies.append(request.content)
        return httpx.Response(200, json={"data": [{"b64_json": "AAAA"}]})

    ref_b64 = base64.b64encode(_png_bytes()).decode()
    with _httpx_with_handler(handler):
        result = asyncio.run(
            OpenAIImageProvider(api_key="test-token", model="gpt-image-2").generate(
                "edit this",
                reference_image_b64=ref_b64,
                input_fidelity="high",
                quality="high",
                output_format="webp",
            )
        )

    body = captured_bodies[0]
    assert b'name="input_fidelity"' not in body
    assert b'name="quality"' in body
    assert b'name="output_format"' in body
    assert result.mime == "image/webp"
    assert result.metadata["output_format"] == "webp"


def test_gpt_image_15_keeps_input_fidelity_in_edit_form():
    captured_bodies: list[bytes] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_bodies.append(request.content)
        return httpx.Response(200, json={"data": [{"b64_json": "AAAA"}]})

    ref_b64 = base64.b64encode(_png_bytes()).decode()
    with _httpx_with_handler(handler):
        asyncio.run(
            OpenAIImageProvider(api_key="test-token", model="gpt-image-1.5").generate(
                "edit this",
                reference_image_b64=ref_b64,
                input_fidelity="high",
                quality="high",
                output_format="webp",
            )
        )

    body = captured_bodies[0]
    assert b'name="input_fidelity"' in body


def test_usage_cost_populates_cost_usd_metadata():
    captured_payloads: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_payloads.append(json.loads(request.content.decode()))
        return httpx.Response(
            200,
            json={
                "data": [{"b64_json": "AAAA"}],
                "usage": {"input_tokens": 2_000, "output_tokens": 4_000},
            },
        )

    with _httpx_with_handler(handler):
        result = asyncio.run(
            OpenAIImageProvider(api_key="test-token", model="gpt-image-1").generate(
                "a sunset",
                quality="high",
            )
        )

    assert captured_payloads[0]["quality"] == "high"
    assert result.metadata["cost_usd"] == pytest.approx(0.18)


def test_custom_base_url_is_used_for_image_generations():
    requested_urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested_urls.append(str(request.url))
        return httpx.Response(200, json={"data": [{"b64_json": "AAAA"}]})

    with _httpx_with_handler(handler):
        asyncio.run(
            OpenAIImageProvider(
                api_key="test-token",
                model="gpt-image-2",
                base_url="https://gateway.example/v1/",
            ).generate("a sunset")
        )

    assert requested_urls == ["https://gateway.example/v1/images/generations"]


def test_openai_base_url_can_come_from_environment(monkeypatch):
    requested_urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested_urls.append(str(request.url))
        return httpx.Response(200, json={"data": [{"b64_json": "AAAA"}]})

    monkeypatch.setenv("VULCA_OPENAI_BASE_URL", "https://env-gateway.example")

    with _httpx_with_handler(handler):
        asyncio.run(
            OpenAIImageProvider(api_key="test-token", model="gpt-image-2").generate(
                "a sunset"
            )
        )

    assert requested_urls == ["https://env-gateway.example/v1/images/generations"]
