"""Gemini image generation provider."""
from __future__ import annotations

import asyncio
import base64
import os

from vulca.providers.base import ImageProvider, ImageResult


class GeminiImageProvider:
    """Image generation via Google Gemini API."""

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

        full_prompt = self._build_prompt(prompt, tradition, subject, kwargs)

        contents: list = []
        if reference_image_b64:
            contents.append(types.Part.from_bytes(
                data=base64.b64decode(reference_image_b64),
                mime_type="image/png",
            ))
        contents.append(full_prompt)

        config = types.GenerateContentConfig(
            response_modalities=["Text", "Image"],
        )

        try:
            response = await asyncio.wait_for(
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

        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                    img_b64 = base64.b64encode(part.inline_data.data).decode()
                    return ImageResult(
                        image_b64=img_b64,
                        mime=part.inline_data.mime_type,
                        metadata={"model": self.model},
                    )

        raise RuntimeError("Gemini returned no image data")

    def _build_prompt(self, prompt: str, tradition: str, subject: str, kwargs: dict) -> str:
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
        parts.append("\nOutput image aspect ratio: 1:1, resolution: 1024x1024")
        return "\n".join(parts)
