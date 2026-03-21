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
    """Generates deterministic SVG placeholder images."""

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
        cid = hashlib.md5(f"{prompt}{tradition}".encode()).hexdigest()[:12]
        bg = _TRADITION_COLORS.get(tradition, "#5F8A50")
        tradition_display = tradition.replace("_", " ").title() if tradition else "Default"
        subject_display = (subject or prompt)[:50]
        for old, new in [("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), ('"', "&quot;")]:
            subject_display = subject_display.replace(old, new)
            tradition_display = tradition_display.replace(old, new)

        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
            f'<rect width="{width}" height="{height}" fill="{bg}" rx="24"/>'
            f'<text x="50%" y="40%" text-anchor="middle" fill="white" font-size="18" font-family="Inter, sans-serif">{tradition_display}</text>'
            f'<text x="50%" y="55%" text-anchor="middle" fill="rgba(255,255,255,0.7)" font-size="14" font-family="Inter, sans-serif">{subject_display}</text>'
            f'<text x="50%" y="85%" text-anchor="middle" fill="rgba(255,255,255,0.3)" font-size="10" font-family="monospace">mock://{cid}</text>'
            f'</svg>'
        )
        img_b64 = base64.b64encode(svg.encode()).decode()
        return ImageResult(
            image_b64=img_b64,
            mime="image/svg+xml",
            metadata={"candidate_id": cid, "image_url": f"mock://{cid}.svg"},
        )


class MockVLMProvider:
    """Returns deterministic scores based on tradition weights."""

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
