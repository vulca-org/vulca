"""IP-Adapter provider — Draft-Style wind格迁移.

Loads IP-Adapter weights on top of an existing SD 1.5 pipeline for style transfer.
Input: original image + reference style image → output: style-transferred image.

Model: h94/IP-Adapter, weights: ip-adapter_sd15.bin (~200MB)
VRAM: SD 1.5 base (~4GB) + IP-Adapter (~200MB) ≈ 4.25GB fp16
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)

__all__ = [
    "IPAdapterProvider",
]


class IPAdapterProvider:
    """Draft-Style: IP-Adapter-based style transfer on SD 1.5.

    Lazy-loads the pipeline on first call. Requires GPU for real inference.
    Falls back to a simple blend operation in mock/CPU mode.
    """

    def __init__(
        self,
        base_model_id: str = "runwayml/stable-diffusion-v1-5",
        ip_adapter_repo: str = "h94/IP-Adapter",
        ip_adapter_weight: str = "ip-adapter_sd15.bin",
        device: str = "auto",
    ) -> None:
        self._base_model_id = base_model_id
        self._ip_adapter_repo = ip_adapter_repo
        self._ip_adapter_weight = ip_adapter_weight
        self._device = device
        self._pipe = None
        self._available: bool | None = None

    @property
    def available(self) -> bool:
        """Check if diffusers + torch CUDA are importable."""
        if self._available is not None:
            return self._available
        try:
            import torch
            from diffusers import StableDiffusionPipeline
            self._available = torch.cuda.is_available()
        except ImportError:
            self._available = False
        return self._available

    @property
    def model_ref(self) -> str:
        return "ip-adapter-sd15"

    def _load_pipeline(self) -> None:
        if self._pipe is not None:
            return

        import torch
        from diffusers import StableDiffusionPipeline

        device = self._device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"

        dtype = torch.float16 if device == "cuda" else torch.float32

        # Clear any leftover VRAM from previous models
        if device == "cuda":
            import gc
            gc.collect()
            torch.cuda.empty_cache()

        logger.info("Loading SD 1.5 + IP-Adapter pipeline ...")
        self._pipe = StableDiffusionPipeline.from_pretrained(
            self._base_model_id,
            torch_dtype=dtype,
            safety_checker=None,
            requires_safety_checker=False,
        ).to(device)

        # Load IP-Adapter weights
        # NOTE: Do NOT call enable_attention_slicing() after load_ip_adapter()!
        # It overwrites IP-Adapter's custom attention processors (IPAdapterAttnProcessor2_0)
        # with standard ones, causing 'tuple' object has no attribute 'shape' error.
        # See: https://github.com/huggingface/diffusers/issues/7263
        self._pipe.load_ip_adapter(
            self._ip_adapter_repo,
            subfolder="models",
            weight_name=self._ip_adapter_weight,
        )
        logger.info("IP-Adapter pipeline loaded on %s", device)

    def transfer_style(
        self,
        image: Image.Image,
        reference_image: Image.Image,
        prompt: str,
        negative_prompt: str = "",
        scale: float = 0.6,
        seed: int = 42,
        steps: int = 20,
        width: int = 512,
        height: int = 512,
        output_path: str = "",
    ) -> str:
        """Transfer style from reference_image to a new generation guided by prompt.

        Parameters
        ----------
        image : PIL.Image
            Source/content image (used for img2img if available).
        reference_image : PIL.Image
            Style reference image for IP-Adapter.
        prompt : str
            Text prompt guiding generation.
        scale : float
            IP-Adapter influence scale [0, 1]. Default 0.6.
        output_path : str
            Where to save the result.

        Returns
        -------
        str
            Path to the output image.
        """
        if not self.available:
            return self._mock_transfer(image, reference_image, output_path)

        import torch

        self._load_pipeline()
        self._pipe.set_ip_adapter_scale(scale)

        generator = torch.Generator(device=self._pipe.device).manual_seed(seed)

        # Resize reference to expected size
        ref_resized = reference_image.convert("RGB").resize((width, height))

        result = self._pipe(
            prompt=prompt,
            negative_prompt=negative_prompt or None,
            ip_adapter_image=ref_resized,
            num_inference_steps=steps,
            generator=generator,
            width=width,
            height=height,
        )
        out_image = result.images[0]

        out = Path(output_path) if output_path else Path(f"/tmp/ip_adapter_{seed}.png")
        out.parent.mkdir(parents=True, exist_ok=True)
        out_image.save(str(out))
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
    def _mock_transfer(
        image: Image.Image,
        reference_image: Image.Image,
        output_path: str,
    ) -> str:
        """CPU-only mock: blend source and reference as proof of concept."""
        src = image.convert("RGB").resize((512, 512))
        ref = reference_image.convert("RGB").resize((512, 512))

        # Simple alpha blend (30% reference style)
        blended = Image.blend(src, ref, alpha=0.3)

        out = Path(output_path) if output_path else Path("/tmp/ip_adapter_mock.png")
        out.parent.mkdir(parents=True, exist_ok=True)
        blended.save(str(out))
        return str(out)
