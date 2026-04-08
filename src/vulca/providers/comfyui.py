"""ComfyUI local image generation provider."""
from __future__ import annotations

import asyncio
import base64
import os

from vulca.providers.base import ImageProvider, ImageResult


class ComfyUIImageProvider:
    """Image generation via ComfyUI REST API (local deployment)."""

    capabilities: frozenset[str] = frozenset({"raw_rgba"})

    def __init__(self, base_url: str = "", **kwargs):
        self.base_url = (
            base_url
            or os.environ.get("VULCA_IMAGE_BASE_URL", "http://localhost:8188")
        )

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
        import httpx

        full_prompt = prompt
        if tradition and tradition != "default":
            full_prompt = f"{prompt}, {tradition.replace('_', ' ')} style"

        workflow = {
            "prompt": {
                "3": {"class_type": "KSampler", "inputs": {
                    "seed": 42, "steps": 20, "cfg": 7.0, "sampler_name": "euler",
                    "scheduler": "normal", "denoise": 1.0,
                    "model": ["4", 0], "positive": ["6", 0],
                    "negative": ["7", 0], "latent_image": ["5", 0]}},
                "4": {"class_type": "CheckpointLoaderSimple",
                      "inputs": {"ckpt_name": kwargs.get("checkpoint", "sd_xl_base_1.0.safetensors")}},
                "5": {"class_type": "EmptyLatentImage",
                      "inputs": {"width": width, "height": height, "batch_size": 1}},
                "6": {"class_type": "CLIPTextEncode",
                      "inputs": {"text": full_prompt, "clip": ["4", 1]}},
                "7": {"class_type": "CLIPTextEncode",
                      "inputs": {"text": negative_prompt or "", "clip": ["4", 1]}},
                "8": {"class_type": "VAEDecode",
                      "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
                "9": {"class_type": "SaveImage",
                      "inputs": {"filename_prefix": "vulca", "images": ["8", 0]}},
            }
        }

        async with httpx.AsyncClient(timeout=300) as client:
            resp = await client.post(f"{self.base_url}/prompt", json=workflow)
            resp.raise_for_status()
            prompt_id = resp.json()["prompt_id"]

            for _ in range(60):
                hist = await client.get(f"{self.base_url}/history/{prompt_id}")
                if hist.status_code == 200:
                    data = hist.json()
                    if prompt_id in data:
                        outputs = data[prompt_id].get("outputs", {})
                        for node_out in outputs.values():
                            for img in node_out.get("images", []):
                                img_resp = await client.get(
                                    f"{self.base_url}/view",
                                    params={"filename": img["filename"],
                                            "subfolder": img.get("subfolder", ""),
                                            "type": img.get("type", "output")},
                                )
                                img_b64 = base64.b64encode(img_resp.content).decode()
                                return ImageResult(image_b64=img_b64, mime="image/png",
                                                   metadata={"prompt_id": prompt_id})
                await asyncio.sleep(5)

            raise TimeoutError("ComfyUI generation timed out after 5 minutes")
