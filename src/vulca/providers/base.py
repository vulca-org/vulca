"""Protocol definitions for pluggable providers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass
class ImageResult:
    """Result from an image generation provider."""
    image_b64: str
    mime: str = "image/png"
    metadata: dict | None = None


@dataclass
class L1L5Scores:
    """L1-L5 dimension scores from a VLM provider."""
    L1: float
    L2: float
    L3: float
    L4: float
    L5: float
    rationales: dict[str, str] | None = None


@runtime_checkable
class ImageProvider(Protocol):
    """Protocol for image generation backends."""
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
    ) -> ImageResult: ...


@runtime_checkable
class VLMProvider(Protocol):
    """Protocol for VLM scoring backends."""
    async def score(
        self,
        image_b64: str,
        *,
        tradition: str = "",
        subject: str = "",
        guidance: str = "",
        **kwargs,
    ) -> L1L5Scores: ...
