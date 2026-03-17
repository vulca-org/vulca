"""GenerateNode -- image generation via provider API or mock."""

from __future__ import annotations

import base64
import hashlib
import logging
import os
from typing import Any

from vulca.pipeline.node import NodeContext, PipelineNode

logger = logging.getLogger("vulca")


class GenerateNode(PipelineNode):
    """Generate an image from a text prompt.

    Supports two providers:
    - ``mock``: returns a deterministic 1x1 PNG (no external calls).
    - ``nb2``: calls NovitaAI / compatible API for real image generation.
    """

    name = "generate"

    async def run(self, ctx: NodeContext) -> dict[str, Any]:
        provider = ctx.provider or "mock"

        if provider == "mock":
            return self._mock_generate(ctx)

        return await self._nb2_generate(ctx)

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
    # NB2 / NovitaAI provider
    # ------------------------------------------------------------------

    @staticmethod
    async def _nb2_generate(ctx: NodeContext) -> dict[str, Any]:
        """Call NovitaAI-compatible txt2img endpoint."""
        import httpx

        api_key = ctx.api_key or os.environ.get("NB2_API_KEY", "")
        base_url = os.environ.get(
            "NB2_BASE_URL", "https://api.novita.ai/v3/async"
        )

        prompt = ctx.get("prompt") or ctx.subject or ctx.intent
        tradition_hint = ctx.tradition.replace("_", " ")
        full_prompt = f"{prompt}, {tradition_hint} style"

        payload = {
            "model_name": "sd_xl_base_1.0.safetensors",
            "prompt": full_prompt,
            "negative_prompt": "nsfw, watermark, low quality, blurry",
            "width": 1024,
            "height": 1024,
            "steps": 25,
            "seed": -1,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=90) as client:
            resp = await client.post(
                f"{base_url}/txt2img",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()

        # Extract image from response
        images = data.get("images") or data.get("data", {}).get("imgs", [])
        if not images:
            raise RuntimeError("NB2 returned no images")

        img_data = images[0]
        if isinstance(img_data, dict):
            img_b64 = img_data.get("image_file", "")
            img_url = img_data.get("image_url", "")
        else:
            img_b64 = img_data
            img_url = ""

        candidate_id = hashlib.sha256(
            f"{ctx.subject}:{ctx.round_num}:nb2".encode()
        ).hexdigest()[:12]

        return {
            "image_b64": img_b64,
            "image_mime": "image/png",
            "candidate_id": candidate_id,
            "image_url": img_url or f"nb2://{candidate_id}.png",
        }
