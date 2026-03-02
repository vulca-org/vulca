"""ControlNet provider — Draft-Refine conditional inpainting.

Integrates ControlNet (canny/depth) with SD 1.5 inpainting for structure-preserving
local reruns. Maps L1-L5 dimensions to appropriate ControlNet types.

Models:
- Canny: lllyasviel/sd-controlnet-canny (~500MB)
- Depth: lllyasviel/sd-controlnet-depth (~500MB)

VRAM: SD 1.5 + single ControlNet ≈ 4.65GB fp16
Note: Cannot load both canny AND depth simultaneously on 8GB GPU.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

__all__ = [
    "ControlNetInpaintProvider",
    "LAYER_CONTROLNET_MAP",
    "get_controlnet_type_for_layer",
]

# L1-L5 → ControlNet type mapping
LAYER_CONTROLNET_MAP: dict[str, str | None] = {
    "visual_perception": "canny",       # L1: preserve edge structure
    "technical_analysis": "depth",      # L2: preserve 3D structure
    "cultural_context": "depth",        # L3: preserve spatial atmosphere
    "critical_interpretation": "canny", # L4: preserve composition structure
    "philosophical_aesthetic": None,    # L5: free repaint (no ControlNet)
}


def get_controlnet_type_for_layer(layer_id: str) -> str | None:
    """Return the recommended ControlNet type for a given L1-L5 layer."""
    return LAYER_CONTROLNET_MAP.get(layer_id)


class ControlNetInpaintProvider:
    """ControlNet-guided inpainting provider.

    Uses StableDiffusionControlNetInpaintPipeline from diffusers for
    structure-preserving local reruns.
    """

    def __init__(
        self,
        controlnet_type: str = "canny",
        base_model_id: str = "runwayml/stable-diffusion-v1-5",
        device: str = "auto",
    ) -> None:
        if controlnet_type not in ("canny", "depth"):
            raise ValueError(f"controlnet_type must be 'canny' or 'depth', got {controlnet_type!r}")
        self._controlnet_type = controlnet_type
        self._base_model_id = base_model_id
        self._device = device
        self._pipe = None
        self._available: bool | None = None

    @property
    def available(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            import torch
            from diffusers import ControlNetModel
            self._available = torch.cuda.is_available()
        except ImportError:
            self._available = False
        return self._available

    @property
    def model_ref(self) -> str:
        return f"controlnet-{self._controlnet_type}-sd15"

    def _load_pipeline(self) -> None:
        if self._pipe is not None:
            return

        import torch
        from diffusers import ControlNetModel, StableDiffusionControlNetInpaintPipeline

        device = self._device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32

        controlnet_id = f"lllyasviel/sd-controlnet-{self._controlnet_type}"
        logger.info("Loading ControlNet %s ...", controlnet_id)

        controlnet = ControlNetModel.from_pretrained(
            controlnet_id,
            torch_dtype=dtype,
        )

        self._pipe = StableDiffusionControlNetInpaintPipeline.from_pretrained(
            self._base_model_id,
            controlnet=controlnet,
            torch_dtype=dtype,
            safety_checker=None,
            requires_safety_checker=False,
        ).to(device)

        if hasattr(self._pipe, "enable_attention_slicing"):
            self._pipe.enable_attention_slicing()
        logger.info("ControlNet %s pipeline loaded on %s", self._controlnet_type, device)

    def inpaint_with_control(
        self,
        image: Image.Image,
        mask: Image.Image,
        prompt: str,
        negative_prompt: str = "",
        control_image: Image.Image | None = None,
        seed: int = 42,
        strength: float = 0.75,
        steps: int = 20,
        controlnet_conditioning_scale: float = 0.8,
        output_path: str = "",
    ) -> str:
        """Inpaint with ControlNet guidance.

        Parameters
        ----------
        image : PIL.Image
            Base image to inpaint.
        mask : PIL.Image
            Binary mask (white=repaint, black=preserve).
        prompt : str
            Generation prompt.
        control_image : PIL.Image, optional
            Pre-computed control image (canny edges / depth map).
            If None, auto-generated from the base image.
        output_path : str
            Where to save the result.

        Returns
        -------
        str
            Path to the output image.
        """
        if not self.available:
            return self._mock_inpaint(image, mask, output_path)

        import torch

        self._load_pipeline()

        # Ensure consistent sizes
        target_size = (512, 512)
        img_rgb = image.convert("RGB").resize(target_size)
        mask_l = mask.convert("L").resize(target_size)

        # Generate control image if not provided
        if control_image is None:
            control_image = self._generate_control_image(img_rgb)
        else:
            control_image = control_image.convert("RGB").resize(target_size)

        generator = torch.Generator(device=self._pipe.device).manual_seed(seed)

        result = self._pipe(
            prompt=prompt,
            negative_prompt=negative_prompt or None,
            image=img_rgb,
            mask_image=mask_l,
            control_image=control_image,
            num_inference_steps=steps,
            strength=strength,
            generator=generator,
            controlnet_conditioning_scale=controlnet_conditioning_scale,
        )
        out_image = result.images[0]

        out = Path(output_path) if output_path else Path(f"/tmp/controlnet_{self._controlnet_type}_{seed}.png")
        out.parent.mkdir(parents=True, exist_ok=True)
        out_image.save(str(out))
        return str(out)

    def _generate_control_image(self, image: Image.Image) -> Image.Image:
        """Auto-generate control image from base image."""
        if self._controlnet_type == "canny":
            return self._generate_canny(image)
        elif self._controlnet_type == "depth":
            return self._generate_depth_simple(image)
        return image

    @staticmethod
    def _generate_canny(image: Image.Image) -> Image.Image:
        """Generate Canny edge map."""
        try:
            import cv2
            arr = np.array(image)
            gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            # ControlNet expects 3-channel image
            edges_rgb = np.stack([edges, edges, edges], axis=-1)
            return Image.fromarray(edges_rgb)
        except ImportError:
            # Fallback: simple edge detection using numpy
            arr = np.array(image.convert("L"), dtype=np.float32)
            dx = np.abs(np.diff(arr, axis=1, prepend=arr[:, :1]))
            dy = np.abs(np.diff(arr, axis=0, prepend=arr[:1, :]))
            edges = np.clip((dx + dy) * 2, 0, 255).astype(np.uint8)
            edges_rgb = np.stack([edges, edges, edges], axis=-1)
            return Image.fromarray(edges_rgb)

    @staticmethod
    def _generate_depth_simple(image: Image.Image) -> Image.Image:
        """Generate a simple depth-like map using luminance gradient.

        For production, use MiDaS or DPT. This is a CPU-friendly approximation.
        """
        arr = np.array(image.convert("L"), dtype=np.float32)
        # Simple depth heuristic: darker = closer (common in landscape art)
        depth = 255.0 - arr
        # Smooth with simple box blur
        from PIL import ImageFilter
        depth_img = Image.fromarray(depth.astype(np.uint8))
        depth_img = depth_img.filter(ImageFilter.GaussianBlur(radius=5))
        # Convert to 3-channel
        depth_arr = np.array(depth_img)
        depth_rgb = np.stack([depth_arr, depth_arr, depth_arr], axis=-1)
        return Image.fromarray(depth_rgb)

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
    def _mock_inpaint(
        image: Image.Image,
        mask: Image.Image,
        output_path: str,
    ) -> str:
        """CPU-only mock: apply green tint to masked region."""
        base = image.convert("RGB").resize((512, 512))
        mask_l = mask.convert("L").resize((512, 512))

        pixels = base.load()
        mask_pixels = mask_l.load()
        w, h = base.size

        for y in range(h):
            for x in range(w):
                if mask_pixels[x, y] > 127:
                    r, g, b = pixels[x, y]
                    # Green tint to show ControlNet was applied
                    pixels[x, y] = (r // 2, min(255, g + 80), b // 2)

        out = Path(output_path) if output_path else Path("/tmp/controlnet_mock.png")
        out.parent.mkdir(parents=True, exist_ok=True)
        base.save(str(out))
        return str(out)
