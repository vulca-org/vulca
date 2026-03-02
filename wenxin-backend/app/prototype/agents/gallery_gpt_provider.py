"""GalleryGPT provider — painting-specialized VLM for L1/L2 artwork analysis.

Uses LLaVA 1.5 7B (llava-hf/llava-1.5-7b-hf) as the multimodal backbone.
GalleryGPT (ACM MM 2024 Oral) is based on LLaVA architecture fine-tuned on
PaintingForm 19k dataset. For the prototype, we use the base LLaVA model
with art-specific prompts; GalleryGPT LoRA weights can be layered later.

VRAM: ~3.5GB with 4-bit NF4 quantization (bitsandbytes)
Usage: Critic phase L1/L2 analysis when local GPU available and API not needed.
Ref: https://github.com/steven640pixel/GalleryGPT
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)

__all__ = [
    "GalleryGPTProvider",
]


class GalleryGPTProvider:
    """Painting-specialized VLM for artwork analysis.

    4-bit quantized LLaVA model for professional art criticism.
    Lazy-loads on first call (~4GB download on first run).
    """

    def __init__(
        self,
        base_model_id: str = "llava-hf/llava-1.5-7b-hf",
        device: str = "auto",
    ) -> None:
        self._base_model_id = base_model_id
        self._device = device
        self._model = None
        self._processor = None
        self._available: bool | None = None

    @property
    def available(self) -> bool:
        """Check if transformers + bitsandbytes + CUDA are available."""
        if self._available is not None:
            return self._available
        try:
            import torch
            from transformers import LlavaForConditionalGeneration  # noqa: F401
            import bitsandbytes  # noqa: F401
            self._available = torch.cuda.is_available()
        except ImportError:
            self._available = False
        return self._available

    @property
    def model_ref(self) -> str:
        return "gallery-gpt-7b-4bit"

    def _load_model(self) -> None:
        if self._model is not None:
            return

        import torch
        from transformers import AutoProcessor, BitsAndBytesConfig, LlavaForConditionalGeneration

        # Clear any leftover VRAM from previous models
        import gc
        gc.collect()
        torch.cuda.empty_cache()

        logger.info("Loading LLaVA 1.5 7B (4-bit) from %s ...", self._base_model_id)

        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )

        self._processor = AutoProcessor.from_pretrained(self._base_model_id)
        self._model = LlavaForConditionalGeneration.from_pretrained(
            self._base_model_id,
            quantization_config=quant_config,
            device_map="auto",
            torch_dtype=torch.float16,
        )
        logger.info("LLaVA 1.5 7B loaded (4-bit NF4, device_map=auto)")

    def analyze_artwork(
        self,
        image: Image.Image | str,
        prompt: str = "",
        layer: str = "L1",
        max_new_tokens: int = 512,
    ) -> dict:
        """Analyze an artwork image and return structured art criticism.

        Parameters
        ----------
        image : PIL.Image or str
            Image object or path to image file.
        prompt : str
            Custom analysis prompt. If empty, uses layer-specific default.
        layer : str
            L1-L5 layer hint for prompt selection.
        max_new_tokens : int
            Maximum generation length.

        Returns
        -------
        dict
            {"analysis": str, "model_ref": str, "latency_ms": int, "success": bool}
        """
        if not self.available:
            return self._mock_analysis(layer)

        t0 = time.monotonic()

        try:
            import torch

            self._load_model()

            # Load image
            if isinstance(image, str):
                image = Image.open(image).convert("RGB")
            else:
                image = image.convert("RGB")

            # Build prompt with LLaVA conversation format
            if not prompt:
                prompt = self._layer_prompt(layer)

            # LLaVA 1.5 prompt format
            full_prompt = f"USER: <image>\n{prompt}\nASSISTANT:"

            inputs = self._processor(
                text=full_prompt,
                images=image,
                return_tensors="pt",
            ).to(self._model.device)

            with torch.no_grad():
                output_ids = self._model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=False,
                )

            # Decode, skip input tokens
            generated = output_ids[0][inputs["input_ids"].shape[1]:]
            analysis = self._processor.decode(generated, skip_special_tokens=True).strip()

            ms = int((time.monotonic() - t0) * 1000)
            return {
                "analysis": analysis,
                "model_ref": self.model_ref,
                "latency_ms": ms,
                "success": True,
            }

        except Exception as exc:
            ms = int((time.monotonic() - t0) * 1000)
            logger.error("GalleryGPT analysis failed: %s", exc)
            return {
                "analysis": "",
                "model_ref": self.model_ref,
                "latency_ms": ms,
                "success": False,
                "error": str(exc),
            }

    def release(self) -> None:
        """Release GPU memory."""
        if self._model is not None:
            del self._model
            self._model = None
        if self._processor is not None:
            del self._processor
            self._processor = None
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass

    @staticmethod
    def _layer_prompt(layer: str) -> str:
        """Return layer-specific analysis prompt."""
        prompts = {
            "L1": (
                "Analyze this artwork's visual elements: composition, color palette, "
                "spatial arrangement, focal points, and visual hierarchy. "
                "Provide a structured professional critique."
            ),
            "L2": (
                "Analyze this artwork's technique: brushwork, medium, surface texture, "
                "use of light and shadow, and technical execution quality. "
                "Compare to established artistic conventions."
            ),
            "L3": (
                "Identify the cultural context of this artwork: tradition, symbolic elements, "
                "cultural references, and how it relates to its artistic heritage."
            ),
            "L4": (
                "Provide a critical interpretation of this artwork: narrative meaning, "
                "artistic intent, emotional impact, and how it communicates ideas."
            ),
            "L5": (
                "Discuss the philosophical and aesthetic dimensions of this artwork: "
                "artistic philosophy, aesthetic theory, and its contribution to art discourse."
            ),
        }
        return prompts.get(layer, prompts["L1"])

    @staticmethod
    def _mock_analysis(layer: str) -> dict:
        """Return mock analysis when GPU is unavailable."""
        mock_texts = {
            "L1": (
                "Visual analysis: The composition features a balanced arrangement with "
                "warm tones dominating the palette. Central focal point draws the eye, "
                "with supporting elements creating depth through atmospheric perspective."
            ),
            "L2": (
                "Technical analysis: The work demonstrates skilled brushwork with visible "
                "texture in the foreground. Medium appears to be oil on canvas with "
                "evidence of both wet-on-wet and glazing techniques."
            ),
        }
        return {
            "analysis": mock_texts.get(layer, mock_texts["L1"]),
            "model_ref": "gallery-gpt-mock",
            "latency_ms": 0,
            "success": True,
        }
