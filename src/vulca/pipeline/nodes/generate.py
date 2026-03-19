"""GenerateNode -- image generation via Gemini or mock."""

from __future__ import annotations

import base64
import hashlib
import logging
import os
import time
from pathlib import Path
from typing import Any

from vulca.pipeline.node import NodeContext, PipelineNode

logger = logging.getLogger("vulca")


class GenerateNode(PipelineNode):
    """Generate an image from a text prompt.

    Supports two providers:
    - ``mock``: returns a deterministic 1x1 PNG (no external calls).
    - ``nb2``: calls Google Gemini image generation model.
    """

    name = "generate"

    async def run(self, ctx: NodeContext) -> dict[str, Any]:
        provider = ctx.provider or "mock"

        if provider == "mock":
            return self._mock_generate(ctx)

        return await self._gemini_generate(ctx)

    # ------------------------------------------------------------------
    # Mock provider
    # ------------------------------------------------------------------

    @staticmethod
    def _mock_generate(ctx: NodeContext) -> dict[str, Any]:
        """Return a deterministic 1x1 white PNG."""
        # Minimal valid PNG (1x1 white pixel)
        png_bytes = (
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde"
            b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05"
            b"\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        img_b64 = base64.b64encode(png_bytes).decode()
        candidate_id = hashlib.sha256(
            f"{ctx.subject}:{ctx.round_num}".encode()
        ).hexdigest()[:12]
        return {
            "image_b64": img_b64,
            "image_mime": "image/png",
            "candidate_id": candidate_id,
            "image_url": f"mock://{candidate_id}.png",
        }

    # ------------------------------------------------------------------
    # Gemini image generation (NB2)
    # ------------------------------------------------------------------

    @staticmethod
    async def _gemini_generate(ctx: NodeContext) -> dict[str, Any]:
        """Call Google Gemini image generation model."""
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ImportError(
                "google-genai package required for image generation: "
                "pip install google-genai"
            ) from exc

        api_key = ctx.api_key or os.environ.get("GOOGLE_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY required for image generation")

        prompt = ctx.get("prompt") or ctx.subject or ctx.intent
        tradition_hint = ctx.tradition.replace("_", " ")
        full_prompt = (
            f"Generate a high-quality artwork: {prompt}\n"
            f"Style: {tradition_hint} tradition\n"
            f"Output image aspect ratio: 1:1, resolution: 1024x1024"
        )

        t0 = time.monotonic()
        client = genai.Client(
            api_key=api_key,
            http_options={"timeout": 120_000},
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                temperature=1.0,
            ),
        )

        # Extract image from response parts
        img_bytes = None
        for part in response.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data is not None:
                img_bytes = part.inline_data.data
                break

        if not img_bytes:
            raise RuntimeError("Gemini returned no image in response")

        latency_ms = int((time.monotonic() - t0) * 1000)
        img_b64 = base64.b64encode(img_bytes).decode()
        candidate_id = hashlib.sha256(
            f"{ctx.subject}:{ctx.round_num}:gemini".encode()
        ).hexdigest()[:12]

        logger.info("Gemini generated image (%dms, %d bytes)", latency_ms, len(img_bytes))

        return {
            "image_b64": img_b64,
            "image_mime": "image/png",
            "candidate_id": candidate_id,
            "image_url": f"gemini://{candidate_id}.png",
        }
