"""Mock providers for testing without API keys."""
from __future__ import annotations

import base64
import hashlib

from vulca.providers.base import ImageProvider, ImageResult, L1L5Scores, VLMProvider

_TRADITION_COLORS: dict[str, str] = {
    "chinese_xieyi": "#3a3a3a",
    "chinese_gongbi": "#c43f2f",
    "japanese_traditional": "#264653",
    "islamic_geometric": "#2a9d8f",
    "watercolor": "#89c2d9",
    "western_academic": "#8a5a44",
    "african_traditional": "#bc6c25",
    "south_asian": "#e9c46a",
}


class MockImageProvider:
    """Generates deterministic solid-color PNG placeholder images."""

    capabilities: frozenset[str] = frozenset({"raw_rgba"})

    def __init__(self, **kwargs):
        pass  # Accept and ignore any kwargs for registry compatibility

    async def generate(
        self,
        prompt: str,
        *,
        tradition: str = "",
        subject: str = "",
        reference_image_b64: str = "",
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        **kwargs,
    ) -> ImageResult:
        import io
        from PIL import Image

        cid = hashlib.md5(f"{prompt}{tradition}".encode()).hexdigest()[:12]

        # Deterministic color from tradition
        hex_color = _TRADITION_COLORS.get(tradition, "#5F8A50")
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)

        img = Image.new("RGBA", (width, height), (r, g, b, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode()

        return ImageResult(
            image_b64=img_b64,
            mime="image/png",
            metadata={"candidate_id": cid, "image_url": f"mock://{cid}.png"},
        )


class MockVLMProvider:
    """Returns deterministic scores based on tradition weights."""

    def __init__(self, **kwargs):
        pass  # Accept and ignore any kwargs for registry compatibility

    async def score(
        self,
        image_b64: str,
        *,
        tradition: str = "",
        subject: str = "",
        guidance: str = "",
        **kwargs,
    ) -> L1L5Scores:
        seed = hash(f"{image_b64[:20]}{tradition}") % 100
        base = 0.65 + (seed % 20) / 100
        scores = {
            "L1": round(min(base + 0.10, 1.0), 2),
            "L2": round(min(base + 0.05, 1.0), 2),
            "L3": round(min(base + 0.15, 1.0), 2),
            "L4": round(min(base + 0.08, 1.0), 2),
            "L5": round(min(base + 0.13, 1.0), 2),
        }
        rationales = {
            "L1": "Mock: Visual composition assessment.",
            "L2": "Mock: Technical execution assessment.",
            "L3": "Mock: Cultural context assessment.",
            "L4": "Mock: Critical interpretation assessment.",
            "L5": "Mock: Philosophical aesthetics assessment.",
        }
        return L1L5Scores(**scores, rationales=rationales)
