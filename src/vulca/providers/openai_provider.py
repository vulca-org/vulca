"""OpenAI DALL-E image generation provider."""
from __future__ import annotations

import os

from vulca.providers.base import ImageProvider, ImageResult


class OpenAIImageProvider:
    """Image generation via OpenAI DALL-E 3 API."""

    def __init__(self, api_key: str = "", model: str = "dall-e-3"):
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
        **kwargs,
    ) -> ImageResult:
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var "
                "or pass api_key to OpenAIImageProvider()."
            )

        import httpx

        full_prompt = prompt
        if tradition and tradition != "default":
            full_prompt = f"{prompt} (cultural tradition: {tradition.replace('_', ' ')})"

        # DALL-E 3 only supports: 1024x1024, 1024x1792, 1792x1024
        dalle3_sizes = {(1024, 1024), (1024, 1792), (1792, 1024)}
        size = f"{width}x{height}" if (width, height) in dalle3_sizes else "1024x1024"

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                "https://api.openai.com/v1/images/generations",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "n": 1,
                    "size": size,
                    "response_format": "b64_json",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        img_b64 = data["data"][0]["b64_json"]
        return ImageResult(
            image_b64=img_b64,
            mime="image/png",
            metadata={"model": self.model, "revised_prompt": data["data"][0].get("revised_prompt", "")},
        )
