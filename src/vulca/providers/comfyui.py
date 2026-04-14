"""ComfyUI local image generation provider."""
from __future__ import annotations

import asyncio
import base64
import io
import os
import secrets
import time

import httpx

from vulca.providers.base import ImageProvider, ImageResult

_GENERATION_TIMEOUT = 600   # seconds (10 minutes) — total wall-clock budget
_POLL_INTERVAL = 5          # seconds between status checks
_HISTORY_REQUEST_TIMEOUT = 30
_MAX_CONSECUTIVE_POLL_FAILURES = 12  # ~1 minute of sustained errors → fail fast


class ComfyUIImageProvider:
    """Image generation via ComfyUI REST API (local deployment)."""

    capabilities: frozenset[str] = frozenset({"raw_rgba"})

    def __init__(self, base_url: str = "", **kwargs):
        self.base_url = (
            base_url
            or os.environ.get("VULCA_IMAGE_BASE_URL", "http://localhost:8188")
        )

    async def _upload_image(self, client, image_b64: str, filename: str) -> str:
        """Upload a base64 image to ComfyUI's input directory. Returns filename."""
        image_bytes = base64.b64decode(image_b64)
        files = {"image": (filename, io.BytesIO(image_bytes), "image/png")}
        resp = await client.post(
            f"{self.base_url}/upload/image", files=files, timeout=30,
        )
        resp.raise_for_status()
        try:
            return resp.json().get("name", filename)
        except ValueError:
            return filename

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
        full_prompt = prompt
        if not kwargs.get("raw_prompt", False):
            if tradition and tradition != "default":
                full_prompt = f"{prompt}, {tradition.replace('_', ' ')} style"

        use_img2img = bool(reference_image_b64)
        denoise = kwargs.get("denoise", 0.75 if use_img2img else 1.0)

        async with httpx.AsyncClient(timeout=_GENERATION_TIMEOUT) as client:
            ref_filename = ""
            if use_img2img:
                ref_filename = await self._upload_image(
                    client, reference_image_b64,
                    f"vulca_ref_{secrets.randbelow(2**32)}.png",
                )

            # Build workflow: txt2img or img2img
            nodes: dict = {
                "4": {"class_type": "CheckpointLoaderSimple",
                      "inputs": {"ckpt_name": kwargs.get("checkpoint", "sd_xl_base_1.0.safetensors")}},
                "6": {"class_type": "CLIPTextEncode",
                      "inputs": {"text": full_prompt, "clip": ["4", 1]}},
                "7": {"class_type": "CLIPTextEncode",
                      "inputs": {"text": negative_prompt or "", "clip": ["4", 1]}},
                "8": {"class_type": "VAEDecode",
                      "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
                "9": {"class_type": "SaveImage",
                      "inputs": {"filename_prefix": "vulca", "images": ["8", 0]}},
            }

            if use_img2img:
                nodes["10"] = {"class_type": "LoadImage",
                               "inputs": {"image": ref_filename}}
                nodes["11"] = {"class_type": "VAEEncode",
                               "inputs": {"pixels": ["10", 0], "vae": ["4", 2]}}
                latent_src = ["11", 0]
            else:
                nodes["5"] = {"class_type": "EmptyLatentImage",
                              "inputs": {"width": width, "height": height, "batch_size": 1}}
                latent_src = ["5", 0]

            nodes["3"] = {"class_type": "KSampler", "inputs": {
                "seed": secrets.randbelow(2**63), "steps": 20, "cfg": 7.0,
                "sampler_name": "euler", "scheduler": "normal",
                "denoise": denoise,
                "model": ["4", 0], "positive": ["6", 0],
                "negative": ["7", 0], "latent_image": latent_src}}

            workflow = {"prompt": nodes}

            resp = await client.post(f"{self.base_url}/prompt", json=workflow)
            resp.raise_for_status()
            prompt_id = resp.json()["prompt_id"]

            deadline = time.monotonic() + _GENERATION_TIMEOUT
            consecutive_failures = 0

            while time.monotonic() < deadline:
                entry = await self._poll_once(client, prompt_id, deadline)
                if entry is None:
                    consecutive_failures += 1
                    if consecutive_failures >= _MAX_CONSECUTIVE_POLL_FAILURES:
                        raise RuntimeError(
                            f"ComfyUI unreachable: {consecutive_failures} "
                            f"consecutive poll failures"
                        )
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    await asyncio.sleep(min(_POLL_INTERVAL, remaining))
                    continue

                consecutive_failures = 0
                status = entry.get("status", {})
                if status.get("status_str") == "error":
                    raise RuntimeError(
                        f"ComfyUI execution failed: {status.get('messages', [])}"
                    )

                images = [
                    img
                    for node_out in entry.get("outputs", {}).values()
                    for img in node_out.get("images", [])
                ]
                if images:
                    return await self._fetch_result_image(
                        client, images[0], prompt_id, deadline,
                    )
                if status.get("completed", False):
                    raise RuntimeError(
                        "ComfyUI job completed but produced no output images"
                    )

                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                await asyncio.sleep(min(_POLL_INTERVAL, remaining))

            raise TimeoutError(
                f"ComfyUI generation timed out after {_GENERATION_TIMEOUT // 60} minutes"
            )

    async def _poll_once(self, client, prompt_id: str, deadline: float) -> dict | None:
        """Fetch /history once.

        Returns:
            - ``{}``              — job accepted but not yet in history (queued/running).
            - non-empty ``dict``  — job's history entry.
            - ``None``            — transport/parse failure (counts toward fail-fast cap).
        """
        request_timeout = min(
            _HISTORY_REQUEST_TIMEOUT,
            max(0.1, deadline - time.monotonic()),
        )
        try:
            hist = await client.get(
                f"{self.base_url}/history/{prompt_id}",
                timeout=request_timeout,
            )
        except httpx.HTTPError:
            return None
        if hist.status_code != 200:
            return None
        try:
            data = hist.json()
        except ValueError:
            return None
        if not isinstance(data, dict):
            return None
        return data.get(prompt_id, {})

    async def _fetch_result_image(
        self, client, img: dict, prompt_id: str, deadline: float,
    ) -> ImageResult:
        view_timeout = min(
            _HISTORY_REQUEST_TIMEOUT,
            max(0.1, deadline - time.monotonic()),
        )
        img_resp = await client.get(
            f"{self.base_url}/view",
            params={
                "filename": img["filename"],
                "subfolder": img.get("subfolder", ""),
                "type": img.get("type", "output"),
            },
            timeout=view_timeout,
        )
        img_resp.raise_for_status()
        raw_bytes = img_resp.content
        if len(raw_bytes) < 1000 or raw_bytes[:4] != b'\x89PNG':
            raise ValueError(
                f"ComfyUI returned invalid image "
                f"({len(raw_bytes)} bytes, header={raw_bytes[:4]!r})"
            )
        return ImageResult(
            image_b64=base64.b64encode(raw_bytes).decode(),
            mime="image/png",
            metadata={"prompt_id": prompt_id},
        )
