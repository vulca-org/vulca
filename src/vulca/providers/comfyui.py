"""ComfyUI local image generation provider."""
from __future__ import annotations

import asyncio
import base64
import os
import secrets

from vulca.providers.base import ImageProvider, ImageResult


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
        import io
        image_bytes = base64.b64decode(image_b64)
        files = {"image": (filename, io.BytesIO(image_bytes), "image/png")}
        resp = await client.post(
            f"{self.base_url}/upload/image", files=files, timeout=30,
        )
        resp.raise_for_status()
        try:
            return resp.json().get("name", filename)
        except (ValueError, KeyError):
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
        import httpx

        full_prompt = prompt
        if not kwargs.get("raw_prompt", False):
            if tradition and tradition != "default":
                full_prompt = f"{prompt}, {tradition.replace('_', ' ')} style"

        use_img2img = bool(reference_image_b64)
        denoise = kwargs.get("denoise", 0.75 if use_img2img else 1.0)

        async with httpx.AsyncClient(timeout=300) as client:
            # Upload reference image if doing img2img
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
                # img2img: LoadImage → VAEEncode → KSampler (denoise < 1.0)
                nodes["10"] = {"class_type": "LoadImage",
                               "inputs": {"image": ref_filename}}
                nodes["11"] = {"class_type": "VAEEncode",
                               "inputs": {"pixels": ["10", 0], "vae": ["4", 2]}}
                nodes["3"] = {"class_type": "KSampler", "inputs": {
                    "seed": secrets.randbelow(2**63), "steps": 20, "cfg": 7.0,
                    "sampler_name": "euler", "scheduler": "normal",
                    "denoise": denoise,
                    "model": ["4", 0], "positive": ["6", 0],
                    "negative": ["7", 0], "latent_image": ["11", 0]}}
            else:
                # txt2img: EmptyLatentImage → KSampler (denoise = 1.0)
                nodes["5"] = {"class_type": "EmptyLatentImage",
                              "inputs": {"width": width, "height": height, "batch_size": 1}}
                nodes["3"] = {"class_type": "KSampler", "inputs": {
                    "seed": secrets.randbelow(2**63), "steps": 20, "cfg": 7.0,
                    "sampler_name": "euler", "scheduler": "normal",
                    "denoise": denoise,
                    "model": ["4", 0], "positive": ["6", 0],
                    "negative": ["7", 0], "latent_image": ["5", 0]}}

            workflow = {"prompt": nodes}

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
                                raw_bytes = img_resp.content
                                if len(raw_bytes) < 1000 or raw_bytes[:4] != b'\x89PNG':
                                    raise ValueError(
                                        f"ComfyUI returned invalid image "
                                        f"({len(raw_bytes)} bytes, "
                                        f"header={raw_bytes[:4]!r})"
                                    )
                                img_b64 = base64.b64encode(raw_bytes).decode()
                                return ImageResult(image_b64=img_b64, mime="image/png",
                                                   metadata={"prompt_id": prompt_id})
                await asyncio.sleep(5)

            raise TimeoutError("ComfyUI generation timed out after 5 minutes")
