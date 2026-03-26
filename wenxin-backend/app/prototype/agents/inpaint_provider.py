"""Inpaint providers — local ControlNet/SD inpainting for targeted local reruns.

AbstractInpaintProvider defines the interface for img2img inpainting operations.
DiffusersInpaintProvider uses HuggingFace diffusers StableDiffusionInpaintPipeline.
MockInpaintProvider generates deterministic test outputs.

Usage flow:
    1. MaskGenerator converts Critic dimension feedback → binary mask (PIL Image)
    2. InpaintProvider takes base_image + mask + prompt_delta → refined image
    3. DraftAgent.refine_candidate() orchestrates both steps
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from PIL import Image

__all__ = [
    "AbstractInpaintProvider",
    "ControlNetInpaintProviderAdapter",
    "DiffusersInpaintProvider",
    "MaskGenerator",
    "MockInpaintProvider",
    "get_inpaint_provider",
]


class AbstractInpaintProvider(ABC):
    """Base class for inpainting image generators."""

    @abstractmethod
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
        """Inpaint masked regions of the base image.

        Parameters
        ----------
        base_image_path : str
            Path to the base image to modify.
        mask_image : PIL.Image.Image
            Binary mask — white (255) = region to repaint, black (0) = preserve.
        prompt : str
            Generation prompt for the inpainted region.
        negative_prompt : str
            Negative prompt for the inpainted region.
        seed : int
            Random seed for reproducibility.
        strength : float
            Denoising strength [0, 1]. Higher = more change.
        steps : int
            Number of inference steps.
        output_path : str
            Where to save the result.

        Returns
        -------
        str
            Actual output path on success.
        """
        ...

    @property
    @abstractmethod
    def model_ref(self) -> str:
        """Human-readable model identifier."""
        ...


class MockInpaintProvider(AbstractInpaintProvider):
    """Deterministic mock inpaint for testing.

    Copies the base image and tints the masked region with a seed-derived colour
    to prove the mask was applied. Output is always PNG.
    """

    @property
    def model_ref(self) -> str:
        return "mock-inpaint-v1"

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
        with Image.open(base_image_path) as raw:
            base = raw.convert("RGB")

        # Resize mask to match base image
        mask = mask_image.convert("L").resize(base.size)

        # Seed-derived tint colour
        r = (seed * 47) % 256
        g = (seed * 113) % 256
        b = (seed * 197) % 256

        # Apply tint to masked pixels
        pixels = base.load()
        mask_pixels = mask.load()
        w, h = base.size
        for y in range(h):
            for x in range(w):
                if mask_pixels[x, y] > 127:  # white = repaint
                    orig = pixels[x, y]
                    # Blend: strength controls how much tint
                    pixels[x, y] = (
                        int(orig[0] * (1 - strength) + r * strength),
                        int(orig[1] * (1 - strength) + g * strength),
                        int(orig[2] * (1 - strength) + b * strength),
                    )

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        base.save(str(out))
        return str(out)


class DiffusersInpaintProvider(AbstractInpaintProvider):
    """Stable Diffusion inpainting via HuggingFace diffusers.

    Uses runwayml/stable-diffusion-inpainting (SD 1.5 inpaint variant).
    Model is lazy-loaded on first call. ~4GB VRAM with float16.
    """

    def __init__(
        self,
        model_id: str = "runwayml/stable-diffusion-inpainting",
        device: str = "auto",
    ) -> None:
        self._model_id = model_id
        self._device = device
        self._pipe = None

    @property
    def model_ref(self) -> str:
        return f"diffusers-inpaint:{self._model_id.split('/')[-1]}"

    def _load_pipeline(self):
        if self._pipe is not None:
            return
        import torch
        from diffusers import AutoPipelineForInpainting

        device = self._device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"

        dtype = torch.float16 if device == "cuda" else torch.float32
        self._pipe = AutoPipelineForInpainting.from_pretrained(
            self._model_id,
            torch_dtype=dtype,
            safety_checker=None,
            requires_safety_checker=False,
        ).to(device)
        if hasattr(self._pipe, "enable_attention_slicing"):
            self._pipe.enable_attention_slicing()

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
        import torch

        self._load_pipeline()

        base = Image.open(base_image_path).convert("RGB")
        # SD inpaint expects 512x512 — resize if needed
        target_size = (512, 512)
        original_size = base.size
        base_resized = base.resize(target_size)
        # AutoPipelineForInpainting accepts L-mode mask (white=repaint)
        mask_resized = mask_image.convert("L").resize(target_size)

        generator = torch.Generator(device=self._pipe.device).manual_seed(seed)

        result = self._pipe(
            prompt=prompt,
            negative_prompt=negative_prompt or None,
            image=base_resized,
            mask_image=mask_resized,
            num_inference_steps=steps,
            strength=strength,
            generator=generator,
        )
        image = result.images[0]

        # Resize back to original
        if image.size != original_size:
            image = image.resize(original_size, Image.LANCZOS)

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        image.save(str(out))
        return str(out)


# ---------------------------------------------------------------------------
# Mask Generator — maps Critic feedback to binary masks
# ---------------------------------------------------------------------------

class MaskGenerator:
    """Generate inpainting masks from Critic dimension feedback.

    Maps L1-L5 dimension deficiencies to spatial mask regions:
    - L1 (visual_perception): Full-image mask (global visual issues)
    - L2 (technical_analysis): Centre-weighted mask (composition/technique)
    - L3 (cultural_context): Foreground emphasis (symbolic elements)
    - L4 (critical_interpretation): Upper portion (atmospheric/narrative)
    - L5 (philosophical_aesthetic): Diffuse soft mask (subtle refinement)

    The mask strategy reflects that different cultural art dimensions
    typically manifest in different spatial regions.
    """

    # Dimension → mask strategy mapping (accepts both dimension names and L-labels)
    _STRATEGIES: dict[str, str] = {
        "visual_perception": "full",
        "technical_analysis": "centre",
        "cultural_context": "foreground",
        "critical_interpretation": "upper",
        "philosophical_aesthetic": "diffuse",
        # L-label aliases (FixItPlan uses "L1"-"L5" format)
        "L1": "full",
        "L2": "centre",
        "L3": "foreground",
        "L4": "upper",
        "L5": "diffuse",
    }

    def generate(
        self,
        target_layers: list[str],
        image_width: int = 512,
        image_height: int = 512,
        mask_specs: list[dict] | None = None,
        preserve_layers: list[str] | None = None,
    ) -> Image.Image:
        """Generate a composite mask for the target layers.

        Parameters
        ----------
        target_layers : list[str]
            Dimension IDs that need refinement.
        image_width, image_height : int
            Output mask dimensions.
        mask_specs : list[dict], optional
            Override masks with explicit specs: [{layer, strength, region}].
        preserve_layers : list[str], optional
            Layers to exclude from the mask (keep unchanged during inpainting).

        Returns
        -------
        PIL.Image.Image
            Binary mask — white=repaint, black=preserve. Mode "L".
        """
        mask = Image.new("L", (image_width, image_height), 0)
        _preserve = set(preserve_layers or [])

        for layer_id in target_layers:
            if layer_id in _preserve:
                continue

            strategy = self._STRATEGIES.get(layer_id, "centre")
            strength = 1.0

            # Check for override in mask_specs
            if mask_specs:
                for spec in mask_specs:
                    if spec.get("layer") == layer_id:
                        strength = spec.get("strength", 1.0)
                        if "region" in spec:
                            strategy = spec["region"]
                        break

            layer_mask = self._generate_strategy_mask(
                strategy, image_width, image_height, strength,
            )
            # Composite: max of existing mask and new layer mask
            mask = _max_images(mask, layer_mask)

        return mask

    def _generate_strategy_mask(
        self,
        strategy: str,
        w: int,
        h: int,
        strength: float,
    ) -> Image.Image:
        """Generate a single-strategy mask."""
        mask = Image.new("L", (w, h), 0)
        pixels = mask.load()
        val = int(255 * min(1.0, max(0.0, strength)))

        if strategy == "full":
            # Entire image
            for y in range(h):
                for x in range(w):
                    pixels[x, y] = val

        elif strategy == "centre":
            # Centre 60% of image
            x0, y0 = int(w * 0.2), int(h * 0.2)
            x1, y1 = int(w * 0.8), int(h * 0.8)
            for y in range(y0, y1):
                for x in range(x0, x1):
                    pixels[x, y] = val

        elif strategy == "foreground":
            # Lower 70% (foreground in most art compositions)
            y0 = int(h * 0.3)
            for y in range(y0, h):
                for x in range(w):
                    pixels[x, y] = val

        elif strategy == "upper":
            # Upper 50% (sky/atmosphere/narrative framing)
            y1 = int(h * 0.5)
            for y in range(y1):
                for x in range(w):
                    pixels[x, y] = val

        elif strategy == "diffuse":
            # Soft gradient from center — subtle refinement
            cx, cy = w // 2, h // 2
            max_dist = ((w / 2) ** 2 + (h / 2) ** 2) ** 0.5
            for y in range(h):
                for x in range(w):
                    dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                    factor = max(0.0, 1.0 - dist / max_dist)
                    pixels[x, y] = int(val * factor)

        return mask


class ControlNetInpaintProviderAdapter(AbstractInpaintProvider):
    """Adapter wrapping ControlNetInpaintProvider to fit AbstractInpaintProvider interface."""

    def __init__(self, controlnet_type: str = "canny"):
        self._controlnet_type = controlnet_type
        self._provider = None

    @property
    def model_ref(self) -> str:
        return f"controlnet-{self._controlnet_type}-inpaint"

    def _ensure_provider(self):
        if self._provider is None:
            from app.prototype.agents.controlnet_provider import ControlNetInpaintProvider
            self._provider = ControlNetInpaintProvider(controlnet_type=self._controlnet_type)

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
        self._ensure_provider()
        base = Image.open(base_image_path).convert("RGB")
        return self._provider.inpaint_with_control(
            image=base,
            mask=mask_image,
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
            strength=strength,
            steps=steps,
            output_path=output_path,
        )


def get_inpaint_provider(name: str) -> AbstractInpaintProvider:
    """Public factory for inpaint providers including ControlNet variants."""
    if name in ("mock", "mock_inpaint"):
        return MockInpaintProvider()
    if name in ("diffusers", "diffusers_inpaint"):
        return DiffusersInpaintProvider()
    if name == "controlnet_canny":
        return ControlNetInpaintProviderAdapter("canny")
    if name == "controlnet_depth":
        return ControlNetInpaintProviderAdapter("depth")
    import logging
    logging.getLogger("vulca").warning(
        "Unknown inpaint provider '%s', falling back to MockInpaintProvider", name
    )
    return MockInpaintProvider()


def _max_images(a: Image.Image, b: Image.Image) -> Image.Image:
    """Element-wise max of two L-mode images (union of masks)."""
    assert a.size == b.size, f"Mask size mismatch: {a.size} != {b.size}"
    a_data = a.tobytes()
    b_data = b.tobytes()
    merged = bytes(max(x, y) for x, y in zip(a_data, b_data))
    result = Image.frombytes("L", a.size, merged)
    return result
