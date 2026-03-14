"""FLUX.2 Pro / FLUX image provider via Replicate API.

Supports FLUX.2 Pro (default, high quality, up to 4MP, 28 steps)
and FLUX Schnell (fast, up to 1MP, 1-4 steps) via model_id parameter.
"""

import os
import logging
import httpx
from pathlib import Path

from app.prototype.agents.draft_provider import AbstractProvider, ProviderRegistry

logger = logging.getLogger(__name__)

# Models and their characteristics
_MODEL_CAPS = {
    "black-forest-labs/flux-2-pro": {"max_steps": 28, "max_dim": 2048},
    "black-forest-labs/flux-schnell": {"max_steps": 4, "max_dim": 1024},
}


@ProviderRegistry.register("replicate", aliases=["flux"])
class ReplicateProvider(AbstractProvider):
    """Generate images via Replicate (FLUX.2 Pro, FLUX Schnell, etc.)."""

    def __init__(
        self,
        api_key: str = "",
        model_id: str = "black-forest-labs/flux-2-pro",
        quality: int | None = None,
    ):
        self.api_key = api_key or os.environ.get("REPLICATE_API_TOKEN", "")
        if not self.api_key:
            raise ValueError("REPLICATE_API_TOKEN required for Replicate provider")
        self.model_id = model_id
        # FLUX.2 Pro quality parameter (1-100, higher = better quality, slower)
        self.quality = quality

    @property
    def model_ref(self) -> str:
        return self.model_id.split("/")[-1]

    def generate(
        self,
        prompt: str,
        negative_prompt: str,
        seed: int,
        width: int,
        height: int,
        steps: int,
        sampler: str,
        output_path: str,
    ) -> str:
        import replicate

        caps = _MODEL_CAPS.get(self.model_id, _MODEL_CAPS["black-forest-labs/flux-2-pro"])
        max_steps = caps["max_steps"]
        max_dim = caps["max_dim"]

        input_params: dict = {
            "prompt": prompt,
            "num_inference_steps": min(steps, max_steps),
            "width": _snap(width, max_dim=max_dim),
            "height": _snap(height, max_dim=max_dim),
            "seed": seed,
        }

        # FLUX.2 Pro supports quality parameter
        if self.quality is not None and "flux-2-pro" in self.model_id:
            input_params["quality"] = max(1, min(self.quality, 100))

        client = replicate.Client(api_token=self.api_key)
        output = client.run(self.model_id, input=input_params)

        # output is a list of URLs or FileOutput objects
        image_url = str(output[0]) if isinstance(output, list) else str(output)

        with httpx.Client(timeout=60) as http:
            resp = http.get(image_url)
            resp.raise_for_status()

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(resp.content)
        return str(out)


def _snap(v: int, multiple: int = 8, max_dim: int = 2048) -> int:
    """Snap dimension to nearest multiple, clamped to max_dim."""
    clamped = min(v, max_dim)
    return max(multiple, (clamped // multiple) * multiple)
