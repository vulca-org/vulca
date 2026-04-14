"""OpenAI DALL-E image generation provider."""
from __future__ import annotations

import base64
import io
import os

from vulca.providers.base import ImageProvider, ImageResult
from vulca.providers.retry import with_retry


class OpenAIImageProvider:
    """Image generation via OpenAI DALL-E 3 API."""

    capabilities: frozenset[str] = frozenset({"raw_rgba"})

    def __init__(self, api_key: str = "", model: str = "gpt-image-1"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model

    async def generate(
        self,
        prompt: str,
        *,
        tradition: str = "",
        subject: str = "",
        reference_image_b64: str = "",
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        background: str = "auto",
        **kwargs,
    ) -> ImageResult:
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var "
                "or pass api_key to OpenAIImageProvider()."
            )

        import httpx

        full_prompt = prompt
        if not kwargs.get("raw_prompt", False):
            if tradition and tradition != "default":
                full_prompt = f"{prompt} (cultural tradition: {tradition.replace('_', ' ')})"

        # DALL-E 3 only supports: 1024x1024, 1024x1792, 1792x1024
        dalle3_sizes = {(1024, 1024), (1024, 1792), (1792, 1024)}
        size = f"{width}x{height}" if (width, height) in dalle3_sizes else "1024x1024"

        def _is_retryable(exc: Exception) -> bool:
            # httpx.HTTPStatusError carries a response with status_code
            response = getattr(exc, "response", None)
            if response is not None:
                status = getattr(response, "status_code", None)
                if status in (429, 500, 503):
                    return True
                return False
            # Network-level errors (timeout, connect) are retryable
            if isinstance(exc, (httpx.TimeoutException, httpx.ConnectError)):
                return True
            return False

        # Only gpt-image-* supports reference-based editing without a mask.
        # dall-e-2 /edits requires a mask + square PNG + returns URLs by default,
        # none of which this provider currently handles.
        use_edits = bool(reference_image_b64)
        if use_edits and not self.model.startswith("gpt-image"):
            raise ValueError(
                f"OpenAI img2img (reference_image_b64) requires a gpt-image-* "
                f"model; current model={self.model!r} is not supported on /edits."
            )

        async def _call() -> ImageResult:
            async with httpx.AsyncClient(timeout=120) as client:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                if use_edits:
                    ref_bytes = base64.b64decode(reference_image_b64)
                    files = {
                        "image": ("ref.png", io.BytesIO(ref_bytes), "image/png"),
                    }
                    form = {
                        "model": self.model,
                        "prompt": full_prompt,
                        "n": "1",
                        "size": size,
                    }
                    resp = await client.post(
                        "https://api.openai.com/v1/images/edits",
                        headers=headers, files=files, data=form,
                    )
                else:
                    payload = {
                        "model": self.model,
                        "prompt": full_prompt,
                        "n": 1,
                        "size": size,
                    }
                    if self.model.startswith("gpt-image"):
                        payload["background"] = background
                        payload["output_format"] = "png"
                    else:
                        payload["response_format"] = "b64_json"
                    resp = await client.post(
                        "https://api.openai.com/v1/images/generations",
                        headers=headers, json=payload,
                    )
                resp.raise_for_status()
                data = resp.json()

            img_b64 = data["data"][0].get("b64_json") or data["data"][0].get("b64", "")
            return ImageResult(
                image_b64=img_b64,
                mime="image/png",
                metadata={"model": self.model,
                          "endpoint": "edits" if use_edits else "generations",
                          "revised_prompt": data["data"][0].get("revised_prompt", "")},
            )

        return await with_retry(
            _call,
            max_retries=3,
            base_delay_ms=500,
            max_delay_ms=16_000,
            retryable_check=_is_retryable,
        )
