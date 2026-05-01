"""OpenAI Responses image tool provider."""
from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

from vulca.providers.base import ImageResult
from vulca.providers.openai_provider import (
    _mime_for_output_format,
    _normalize_openai_base_url,
)
from vulca.providers.retry import with_retry


DEFAULT_RESPONSE_MODEL = "gpt-5.5"
DEFAULT_IMAGE_MODEL = "gpt-image-2"
AsyncOpenAI: Any = None


def _async_openai_class() -> Any:
    global AsyncOpenAI
    if AsyncOpenAI is not None:
        return AsyncOpenAI
    try:
        from openai import AsyncOpenAI as async_openai
    except ImportError as exc:
        raise ImportError(
            "OpenAIResponsesImageProvider requires the openai SDK. "
            "Install with `pip install vulca[providers]`."
        ) from exc
    AsyncOpenAI = async_openai
    return AsyncOpenAI


def _get_field(value: Any, key: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(key, default)
    return getattr(value, key, default)


def _as_dict(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        dumped = value.model_dump(exclude_none=True)
        return dumped if isinstance(dumped, dict) else None
    keys = (
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "input_tokens_details",
        "output_tokens_details",
    )
    data = {
        key: getattr(value, key)
        for key in keys
        if getattr(value, key, None) is not None
    }
    return data or None


def _response_size(width: int, height: int) -> str:
    if width <= 0 or height <= 0:
        return "auto"
    if width == height:
        return "1024x1024"
    return "1536x1024" if width > height else "1024x1536"


def _normalize_output_format(output_format: str | None) -> str:
    normalized = (output_format or "png").lower()
    if normalized == "jpg":
        return "jpeg"
    if normalized in {"png", "jpeg", "webp"}:
        return normalized
    return "png"


def _image_data_url(image_b64: str, mime: str = "image/png") -> str:
    if image_b64.startswith("data:image/"):
        return image_b64
    return f"data:{mime};base64,{image_b64}"


def _build_input(prompt: str, reference_image_b64: str, reference_mime: str) -> Any:
    if not reference_image_b64:
        return prompt
    return [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": _image_data_url(reference_image_b64, reference_mime),
                },
            ],
        }
    ]


def _extract_image_call(response: Any) -> tuple[str, Any]:
    for item in _get_field(response, "output", []) or []:
        if _get_field(item, "type") != "image_generation_call":
            continue
        image_b64 = _get_field(item, "result")
        if image_b64:
            return image_b64, item
    raise RuntimeError("OpenAI Responses returned no image_generation_call result")


def _is_retryable(exc: Exception) -> bool:
    status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    code = str(getattr(exc, "code", "") or "").lower()
    message = str(exc).lower()
    if code == "insufficient_quota" or "insufficient_quota" in message:
        return False
    if "exceeded your current quota" in message:
        return False
    if status in (429, 500, 503):
        return True
    if isinstance(status, int):
        return False
    return type(exc).__name__ in {
        "APIConnectionError",
        "APITimeoutError",
        "TimeoutException",
        "ConnectError",
    }


class OpenAIResponsesImageProvider:
    """Image generation through the OpenAI Responses API image tool."""

    capabilities: frozenset[str] = frozenset(
        {"raw_rgba", "reference_image", "multi_turn", "agentic_image_tool"}
    )

    def __init__(
        self,
        api_key: str = "",
        model: str = DEFAULT_IMAGE_MODEL,
        response_model: str = DEFAULT_RESPONSE_MODEL,
        base_url: str = "",
        timeout: int = 120,
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model or os.environ.get("VULCA_OPENAI_IMAGE_MODEL", DEFAULT_IMAGE_MODEL)
        self.response_model = (
            response_model
            or os.environ.get("VULCA_OPENAI_RESPONSES_MODEL", DEFAULT_RESPONSE_MODEL)
        )
        self.base_url = _normalize_openai_base_url(
            base_url
            or os.environ.get("VULCA_OPENAI_BASE_URL", "")
            or os.environ.get("OPENAI_BASE_URL", "")
        )
        self.timeout = timeout

    async def generate(
        self,
        prompt: str,
        *,
        tradition: str = "",
        subject: str = "",
        reference_image_b64: str = "",
        negative_prompt: str = "",
        seed: int | None = None,
        steps: int | None = None,
        cfg_scale: float | None = None,
        width: int = 1024,
        height: int = 1024,
        input_fidelity: str | None = None,
        quality: str | None = None,
        output_format: str | None = None,
        **kwargs,
    ) -> ImageResult:
        _ = (seed, steps, cfg_scale)

        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var "
                "or pass api_key to OpenAIResponsesImageProvider()."
            )

        raw_prompt = kwargs.pop("raw_prompt", False)
        full_prompt = prompt
        if not raw_prompt:
            prompt_parts = [prompt]
            if tradition and tradition != "default":
                prompt_parts.append(
                    f"Cultural tradition: {tradition.replace('_', ' ')}"
                )
            if subject:
                prompt_parts.append(f"Subject: {subject}")
            full_prompt = "\n".join(prompt_parts)
        if negative_prompt:
            full_prompt = f"{full_prompt}\nAvoid: {negative_prompt}"

        response_model = kwargs.pop("response_model", self.response_model)
        image_model = kwargs.pop("image_model", kwargs.pop("model", self.model))
        output_format = _normalize_output_format(output_format)
        size = kwargs.pop("size", None) or _response_size(width, height)

        tool: dict[str, Any] = {
            "type": "image_generation",
            "model": image_model,
            "size": size,
            "quality": quality or "auto",
            "output_format": output_format,
            "action": kwargs.pop("action", "generate"),
        }
        if input_fidelity:
            tool["input_fidelity"] = input_fidelity
        for key in (
            "background",
            "moderation",
            "output_compression",
            "partial_images",
            "input_image_mask",
        ):
            value = kwargs.pop(key, None)
            if value is not None:
                tool[key] = value

        previous_response_id = kwargs.pop("previous_response_id", None)
        force_tool = kwargs.pop("force_tool", True)
        reference_mime = kwargs.pop("reference_mime", "image/png")

        request: dict[str, Any] = {
            "model": response_model,
            "input": _build_input(full_prompt, reference_image_b64, reference_mime),
            "tools": [tool],
        }
        if previous_response_id:
            request["previous_response_id"] = previous_response_id
        if force_tool:
            request["tool_choice"] = kwargs.pop(
                "tool_choice",
                {"type": "image_generation"},
            )
        elif "tool_choice" in kwargs:
            request["tool_choice"] = kwargs.pop("tool_choice")

        for key in (
            "instructions",
            "max_output_tokens",
            "metadata",
            "parallel_tool_calls",
            "temperature",
            "top_p",
            "truncation",
            "store",
        ):
            value = kwargs.pop(key, None)
            if value is not None:
                request[key] = value

        async_openai = _async_openai_class()
        client = async_openai(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

        async def _call() -> object:
            try:
                return await client.responses.create(**request)
            except Exception as exc:
                message = str(exc).lower()
                if (
                    "insufficient_quota" in message
                    or "exceeded your current quota" in message
                ):
                    raise RuntimeError(
                        "OpenAI quota exhausted or billing blocked for Responses "
                        "image generation. Check OpenAI billing/credits or use "
                        "another provider."
                    ) from exc
                raise

        response = await with_retry(
            _call,
            max_retries=3,
            base_delay_ms=500,
            max_delay_ms=16_000,
            retryable_check=_is_retryable,
        )
        image_b64, image_call = _extract_image_call(response)

        metadata: dict[str, Any] = {
            "provider": "openai-responses",
            "response_model": response_model,
            "image_model": image_model,
            "response_id": _get_field(response, "id"),
            "tool_call_id": _get_field(image_call, "id"),
            "revised_prompt": _get_field(image_call, "revised_prompt"),
        }
        usage = _as_dict(_get_field(response, "usage"))
        if usage is not None:
            metadata["usage"] = usage

        return ImageResult(
            image_b64=image_b64,
            mime=_mime_for_output_format(output_format),
            metadata=metadata,
        )


__all__ = ["OpenAIResponsesImageProvider"]
