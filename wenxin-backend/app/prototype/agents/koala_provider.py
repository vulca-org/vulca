"""KOALA-Lightning 700M provider — lightweight high-res image generation.

etri-vilab/koala-lightning-700m: Only 700M params, 10 steps, 1024x1024.
Serves as local fallback when Together.ai FLUX API is unavailable.

VRAM: ~6GB fp16 (fits RTX 2070 8GB)
Speed: ~3-5s per image on RTX 2070 (10 steps)
Key: Must use EulerDiscreteScheduler with timestep_spacing="trailing"
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)

__all__ = [
    "KoalaProvider",
]


class KoalaProvider:
    """KOALA-Lightning 700M image generation.

    Standard diffusers SDXL pipeline with custom scheduler settings.
    Lazy-loaded on first generate() call.
    """

    def __init__(
        self,
        model_id: str = "etri-vilab/koala-lightning-700m",
        device: str = "auto",
    ) -> None:
        self._model_id = model_id
        self._device = device
        self._pipe = None
        self._available: bool | None = None

    @property
    def available(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            import torch
            from diffusers import StableDiffusionXLPipeline
            self._available = torch.cuda.is_available()
        except ImportError:
            self._available = False
        return self._available

    @property
    def model_ref(self) -> str:
        return "koala-lightning-700m"

    def _load_pipeline(self) -> None:
        if self._pipe is not None:
            return

        import torch
        from diffusers import EulerDiscreteScheduler, StableDiffusionXLPipeline

        device = self._device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32

        # Clear any leftover VRAM from previous models before loading KOALA
        if device == "cuda":
            import gc
            gc.collect()
            torch.cuda.empty_cache()
            logger.info("VRAM cleared before KOALA load")

        logger.info("Loading KOALA-Lightning 700M ...")
        # SDXL pipelines don't have safety_checker — no need to pass it
        self._pipe = StableDiffusionXLPipeline.from_pretrained(
            self._model_id,
            torch_dtype=dtype,
        ).to(device)

        # Critical: KOALA requires trailing timestep spacing
        self._pipe.scheduler = EulerDiscreteScheduler.from_config(
            self._pipe.scheduler.config,
            timestep_spacing="trailing",
        )

        if hasattr(self._pipe, "enable_attention_slicing"):
            self._pipe.enable_attention_slicing()
        logger.info("KOALA-Lightning loaded on %s", device)

    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        seed: int = 42,
        width: int = 1024,
        height: int = 1024,
        steps: int = 10,
        guidance_scale: float = 3.5,
        output_path: str = "",
    ) -> str:
        """Generate a high-resolution image.

        Parameters
        ----------
        prompt : str
            Generation prompt.
        width, height : int
            Output resolution (default 1024x1024).
        steps : int
            Inference steps (KOALA needs only 10).
        guidance_scale : float
            CFG scale (default 3.5 for KOALA).

        Returns
        -------
        str
            Path to the output image.
        """
        if not self.available:
            return self._mock_generate(prompt, seed, width, height, output_path)

        import torch

        t0 = time.monotonic()
        self._load_pipeline()

        generator = torch.Generator(device=self._pipe.device).manual_seed(seed)

        result = self._pipe(
            prompt=prompt,
            negative_prompt=negative_prompt or None,
            width=width,
            height=height,
            num_inference_steps=steps,
            guidance_scale=guidance_scale,
            generator=generator,
        )
        out_image = result.images[0]

        out = Path(output_path) if output_path else Path(f"/tmp/koala_{seed}.png")
        out.parent.mkdir(parents=True, exist_ok=True)
        out_image.save(str(out))

        ms = int((time.monotonic() - t0) * 1000)
        logger.info("KOALA generated %dx%d in %dms", width, height, ms)
        return str(out)

    def release(self) -> None:
        """Release GPU memory."""
        if self._pipe is not None:
            del self._pipe
            self._pipe = None
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass

    @staticmethod
    def _mock_generate(
        prompt: str,
        seed: int,
        width: int,
        height: int,
        output_path: str,
    ) -> str:
        """CPU-only mock: generate a solid-color 1024x1024 PNG."""
        r = (seed * 47) % 256
        g = (seed * 113) % 256
        b = (seed * 197) % 256

        # Create small image scaled to target resolution label
        img = Image.new("RGB", (64, 64), (r, g, b))
        # Resize up to target (just for testing — real inference outputs full res)
        img = img.resize((width, height), Image.NEAREST)

        out = Path(output_path) if output_path else Path(f"/tmp/koala_mock_{seed}.png")
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(out))
        return str(out)
