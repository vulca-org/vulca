"""Gemini image generation provider.

Supports imageSize (512/1K/2K/4K) and aspectRatio via Google GenAI API.
"""
from __future__ import annotations

import asyncio
import base64
import math
import os

from vulca.providers.base import ImageProvider, ImageResult
from vulca.providers.retry import with_retry

# Gemini API uses named size tiers, not arbitrary pixel dimensions.
# Map pixel dimensions to the closest imageSize tier.
_SIZE_TIERS = [
    (512, "512"),
    (1024, "1K"),
    (2048, "2K"),
    (4096, "4K"),
]

# Supported aspect ratios (Gemini API).
_ASPECT_RATIOS = {
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1",
    "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
}


def _pixels_to_image_size(long_edge: int) -> str:
    """Map pixel dimension (long edge) to Gemini imageSize tier."""
    for threshold, tier in _SIZE_TIERS:
        if long_edge <= threshold:
            return tier
    return "4K"


def _dims_to_aspect_ratio(width: int, height: int) -> str:
    """Find the closest supported aspect ratio for given dimensions."""
    if width == height or width <= 0 or height <= 0:
        return "1:1"
    target = width / height
    best_ratio = "1:1"
    best_diff = float("inf")
    for ar in _ASPECT_RATIOS:
        a, b = ar.split(":")
        ratio = int(a) / int(b)
        diff = abs(ratio - target)
        if diff < best_diff:
            best_diff = diff
            best_ratio = ar
    return best_ratio


class GeminiImageProvider:
    """Image generation via Google Gemini API.

    Supports imageSize control (512/1K/2K/4K) and aspectRatio.
    Width/height params are mapped to the closest Gemini tier + ratio.
    """

    def __init__(
        self,
        api_key: str = "",
        model: str = "gemini-3.1-flash-image-preview",
        timeout: int = 90,
    ):
        self.api_key = (
            api_key
            or os.environ.get("GOOGLE_API_KEY", "")
            or os.environ.get("GEMINI_API_KEY", "")
        )
        self.model = model
        self.timeout = timeout

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
        **kwargs,
    ) -> ImageResult:
        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Set GOOGLE_API_KEY env var "
                "or pass api_key to GeminiImageProvider()."
            )

        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.api_key)

        # Map width/height to Gemini imageSize + aspectRatio
        long_edge = max(width, height)
        image_size = kwargs.pop("image_size", None) or _pixels_to_image_size(long_edge)
        aspect_ratio = kwargs.pop("aspect_ratio", None) or _dims_to_aspect_ratio(width, height)

        full_prompt = self._build_prompt(prompt, tradition, subject, aspect_ratio, kwargs)

        contents: list = []
        if reference_image_b64:
            contents.append(types.Part.from_bytes(
                data=base64.b64decode(reference_image_b64),
                mime_type="image/png",
            ))
        contents.append(full_prompt)

        config = types.GenerateContentConfig(
            response_modalities=["Text", "Image"],
            image_config=types.ImageConfig(
                image_size=image_size,
                aspect_ratio=aspect_ratio,
            ),
        )

        def _is_retryable(exc: Exception) -> bool:
            if isinstance(exc, asyncio.TimeoutError):
                return True
            # Retry on rate-limit (429), server error (500), or unavailable (503)
            status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
            if status in (429, 500, 503):
                return True
            return False

        async def _call() -> object:
            try:
                return await asyncio.wait_for(
                    asyncio.to_thread(
                        client.models.generate_content,
                        model=self.model,
                        contents=contents,
                        config=config,
                    ),
                    timeout=self.timeout,
                )
            except asyncio.TimeoutError:
                raise TimeoutError(f"Gemini image generation timed out after {self.timeout}s")

        response = await with_retry(
            _call,
            max_retries=3,
            base_delay_ms=500,
            max_delay_ms=16_000,
            retryable_check=_is_retryable,
        )

        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                    img_b64 = base64.b64encode(part.inline_data.data).decode()
                    return ImageResult(
                        image_b64=img_b64,
                        mime=part.inline_data.mime_type,
                        metadata={
                            "model": self.model,
                            "image_size": image_size,
                            "aspect_ratio": aspect_ratio,
                        },
                    )

        raise RuntimeError("Gemini returned no image data")

    def _build_prompt(
        self, prompt: str, tradition: str, subject: str,
        aspect_ratio: str, kwargs: dict,
    ) -> str:
        parts = [f"Generate a high-quality artwork: {prompt}"]
        if tradition and tradition != "default":
            parts.append(f"Style: {tradition.replace('_', ' ')} tradition")
        if subject:
            parts.append(f"Subject: {subject}")
        cultural_guidance = kwargs.get("cultural_guidance", "")
        if cultural_guidance:
            parts.append(f"\n{cultural_guidance}")
        improvement_focus = kwargs.get("improvement_focus", "")
        if improvement_focus:
            parts.append(f"\n{improvement_focus}")
        return "\n".join(parts)
