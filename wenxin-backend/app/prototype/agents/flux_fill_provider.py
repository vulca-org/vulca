"""FLUX.1 Fill Inpaint Provider — cloud API-based targeted inpainting.

Calls FLUX.1 Fill Dev API (via fal.ai or BFL) for real mask-based
inpainting. Replaces MockInpaintProvider for FLUX conditions.

API: fal.ai endpoint (default)
  POST https://fal.run/fal-ai/flux-general/inpainting  (Dev)
  POST https://fal.run/fal-ai/flux-pro/v1/fill          (Pro)
  Headers: Authorization: Key $FAL_KEY
  Body: { image_url, mask_url, prompt, num_inference_steps }

Cost: ~$0.035/megapixel (Dev) / ~$0.05/megapixel (Pro)

Part of Line B in the VULCA upgrade roadmap.
"""

from __future__ import annotations

import base64
import io
import logging
import os
import time
from pathlib import Path

import requests
from PIL import Image

from app.prototype.agents.inpaint_provider import AbstractInpaintProvider

logger = logging.getLogger(__name__)

__all__ = [
    "FluxFillProvider",
]

# fal.ai endpoints (updated 2026-02-27)
_FAL_FLUX_FILL_DEV = "https://fal.run/fal-ai/flux-general/inpainting"
_FAL_FLUX_FILL_PRO = "https://fal.run/fal-ai/flux-pro/v1/fill"

# Timeouts
_REQUEST_TIMEOUT = 120  # seconds


class FluxFillProvider(AbstractInpaintProvider):
    """FLUX.1 Fill inpainting via fal.ai API.

    Requires FAL_KEY environment variable.
    Falls back to MockInpaintProvider behavior if API unavailable.

    Parameters
    ----------
    api_key : str
        fal.ai API key. Reads from FAL_KEY env if empty.
    use_pro : bool
        If True, use FLUX.1 Fill Pro ($0.050) instead of Dev ($0.025).
    """

    def __init__(
        self,
        api_key: str | None = None,
        use_pro: bool = False,
    ) -> None:
        self._api_key = api_key if api_key is not None else os.environ.get("FAL_KEY", "")
        self._endpoint = _FAL_FLUX_FILL_PRO if use_pro else _FAL_FLUX_FILL_DEV
        self._variant = "pro" if use_pro else "dev"

    @property
    def model_ref(self) -> str:
        return f"flux-fill-{self._variant}"

    @property
    def available(self) -> bool:
        """Check if API key is configured."""
        return bool(self._api_key)

    def inpaint(
        self,
        base_image_path: str,
        mask_image: Image.Image,
        prompt: str,
        negative_prompt: str,
        seed: int,
        strength: float,
        steps: int,
        output_path: str,
    ) -> str:
        """Inpaint masked regions using FLUX.1 Fill API.

        Parameters match AbstractInpaintProvider interface.
        Note: FLUX Fill doesn't use negative_prompt or sampler —
        these are accepted but ignored for API compatibility.
        """
        if not self.available:
            logger.warning("FAL_KEY not set, falling back to mock inpainting")
            return self._mock_fallback(
                base_image_path, mask_image, prompt, seed,
                strength, output_path,
            )

        t0 = time.monotonic()

        # FLUX is guidance-free (no classifier-free guidance), so negative_prompt
        # cannot be sent as a separate API field. Convert to positive guidance.
        effective_prompt = prompt
        if negative_prompt and negative_prompt.strip():
            effective_prompt = f"{prompt}. Avoid: {negative_prompt.strip()}"

        # Prepare images
        base_b64 = self._encode_image_file(base_image_path)
        mask_b64 = self._encode_pil_image(mask_image, base_image_path)

        if not base_b64 or not mask_b64:
            logger.error("Failed to encode images for FLUX Fill")
            return self._mock_fallback(
                base_image_path, mask_image, prompt, seed,
                strength, output_path,
            )

        # API call
        payload: dict = {
            "image_url": f"data:image/png;base64,{base_b64}",
            "mask_url": f"data:image/png;base64,{mask_b64}",
            "prompt": effective_prompt,
            "num_inference_steps": min(steps, 28),  # FLUX Fill optimal range
            "strength": strength,
        }
        # seed is only supported by the Pro endpoint; Dev returns 422
        if self._variant == "pro":
            payload["seed"] = seed

        headers = {
            "Authorization": f"Key {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self._endpoint,
                json=payload,
                headers=headers,
                timeout=_REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            result = response.json()

            elapsed_ms = int((time.monotonic() - t0) * 1000)
            logger.info("FLUX Fill API call: %dms", elapsed_ms)

            # Extract result image
            images = result.get("images", [])
            if not images:
                logger.error("FLUX Fill returned no images: %s", result)
                return self._mock_fallback(
                    base_image_path, mask_image, prompt, seed,
                    strength, output_path,
                )

            image_url = images[0].get("url", "")
            if not image_url:
                logger.error("FLUX Fill image has no URL")
                return self._mock_fallback(
                    base_image_path, mask_image, prompt, seed,
                    strength, output_path,
                )

            # Download result image
            result_path = self._download_and_save(image_url, output_path)
            if not result_path:
                logger.error("FLUX Fill download failed, falling back to mock")
                return self._mock_fallback(
                    base_image_path, mask_image, prompt, seed,
                    strength, output_path,
                )
            return result_path

        except requests.exceptions.RequestException as exc:
            logger.error("FLUX Fill API error: %s", exc)
            return self._mock_fallback(
                base_image_path, mask_image, prompt, seed,
                strength, output_path,
            )

    # ------------------------------------------------------------------
    # Image encoding helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _encode_image_file(image_path: str) -> str:
        """Read and encode image file to base64 PNG."""
        try:
            img = Image.open(image_path).convert("RGB")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return base64.b64encode(buf.getvalue()).decode("ascii")
        except Exception as exc:
            logger.error("Failed to encode image %s: %s", image_path, exc)
            return ""

    @staticmethod
    def _encode_pil_image(
        mask: Image.Image,
        base_image_path: str,
    ) -> str:
        """Encode PIL mask to base64 PNG, resized to match base image."""
        try:
            # Ensure mask matches base image dimensions
            with Image.open(base_image_path) as base:
                base_size = base.size
            mask_resized = mask.convert("L").resize(base_size)

            buf = io.BytesIO()
            mask_resized.save(buf, format="PNG")
            return base64.b64encode(buf.getvalue()).decode("ascii")
        except Exception as exc:
            logger.error("Failed to encode mask: %s", exc)
            return ""

    @staticmethod
    def _download_and_save(url: str, output_path: str) -> str:
        """Download image from URL and save to output_path."""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            img = Image.open(io.BytesIO(response.content)).convert("RGB")
            img.save(output_path)
            logger.info("FLUX Fill result saved to %s", output_path)
            return output_path

        except Exception as exc:
            logger.error("Failed to download FLUX Fill result: %s", exc)
            return ""

    # ------------------------------------------------------------------
    # Mock fallback (when API unavailable)
    # ------------------------------------------------------------------

    @staticmethod
    def _mock_fallback(
        base_image_path: str,
        mask_image: Image.Image,
        prompt: str,
        seed: int,
        strength: float,
        output_path: str,
    ) -> str:
        """Deterministic fallback when FLUX Fill API is unavailable."""
        from app.prototype.agents.inpaint_provider import MockInpaintProvider

        mock = MockInpaintProvider()
        return mock.inpaint(
            base_image_path=base_image_path,
            mask_image=mask_image,
            prompt=prompt,
            negative_prompt="",
            seed=seed,
            strength=strength,
            steps=1,
            output_path=output_path,
        )
