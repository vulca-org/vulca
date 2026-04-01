"""VulcaTool protocol — foundational types for VULCA Tool Protocol system.

Defines:
- ToolCategory: 8 analysis categories
- ToolSchema: Pydantic-based I/O schema base class
- VisualEvidence: annotated image + analysis summary
- ToolConfig: runtime configuration for tool execution
- VulcaTool: abstract base class for all VULCA tools
- ImageData: cross-platform unified image type
"""

from __future__ import annotations

import abc
import base64
import enum
import io
import logging
from typing import Any, ClassVar, Literal

import numpy as np
from PIL import Image
from pydantic import BaseModel, Field

logger = logging.getLogger("vulca.tools")


# ---------------------------------------------------------------------------
# ToolCategory
# ---------------------------------------------------------------------------


class ToolCategory(str, enum.Enum):
    """Tool categories — determines UI grouping and color coding."""

    # A: Image processing / post-processing
    FILTER = "filter"
    COMPOSITE = "composite"
    TRANSFORM = "transform"
    # B: Procedural generation
    GENERATOR = "generator"
    PATTERN = "pattern"
    # C: Cultural / style analysis (VULCA differentiator)
    CULTURAL_CHECK = "cultural"
    COMPOSITION = "composition"
    STYLE_ANALYSIS = "style"


# ---------------------------------------------------------------------------
# ToolSchema — Pydantic-based I/O schema base class
# ---------------------------------------------------------------------------


class ToolSchema(BaseModel):
    """Base class for tool Input and Output schemas.

    Subclass for each tool's Input and Output:

        class MyTool(VulcaTool):
            class Input(ToolSchema):
                image: ImageData
            class Output(ToolSchema):
                score: float
    """

    model_config = {"arbitrary_types_allowed": True}


# ---------------------------------------------------------------------------
# VisualEvidence
# ---------------------------------------------------------------------------


class VisualEvidence(ToolSchema):
    """Visual evidence from a tool — annotated image + analysis summary.

    Fields:
        annotated_image: PNG-encoded bytes of annotated result image (optional).
        summary: Human-readable single-sentence finding.
        details: Structured key/value analysis data.
        confidence: Confidence score in [0, 1].
    """

    annotated_image: bytes | None = Field(
        default=None,
        description="PNG-encoded bytes of the annotated result image.",
    )
    summary: str = Field(description="Human-readable single-sentence finding.")
    details: dict[str, Any] = Field(description="Structured key/value analysis data.")
    confidence: float = Field(description="Confidence score in [0, 1].")


# ---------------------------------------------------------------------------
# ToolConfig
# ---------------------------------------------------------------------------


class ToolConfig(BaseModel):
    """User-controllable configuration for any tool invocation."""

    mode: Literal["check", "fix", "suggest"] = Field(
        default="check",
        description="check=analyze only, fix=analyze+auto-correct, suggest=analyze+recommend",
    )
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="Tool-specific parameter overrides.",
    )
    thresholds: dict[str, float] = Field(
        default_factory=dict,
        description="Pass/fail threshold values.",
    )
    force_verdict: str | None = Field(
        default=None,
        description="Override tool verdict.",
    )


# ---------------------------------------------------------------------------
# VulcaTool — abstract base class
# ---------------------------------------------------------------------------


class VulcaTool(abc.ABC):
    """Abstract base class for all VULCA analysis tools.

    Subclass and implement:
        - name: str
        - display_name: str
        - description: str
        - category: ToolCategory
        - max_seconds: float
        - replaces: list[str]
        - Input(ToolSchema): Input schema
        - Output(ToolSchema): Output schema
        - execute(input_data, config) -> Output

    Use safe_execute() at runtime — it validates inputs before calling execute().
    """

    # --- Required class attributes ---
    name: ClassVar[str]
    display_name: ClassVar[str]
    description: ClassVar[str]
    category: ClassVar[ToolCategory]
    max_seconds: ClassVar[float]
    replaces: ClassVar[dict[str, list[str]]]

    # Concurrency and safety attributes (fail-closed defaults)
    is_concurrent_safe: ClassVar[bool] = False
    is_read_only: ClassVar[bool] = True

    # --- Inner schema classes (must be overridden) ---
    class Input(ToolSchema):
        """Override in subclass."""

    class Output(ToolSchema):
        """Override in subclass."""

    @abc.abstractmethod
    def execute(self, input_data: "VulcaTool.Input", config: ToolConfig) -> "VulcaTool.Output":
        """Run the tool analysis. Must be implemented by each concrete tool.

        Args:
            input_data: Validated instance of this tool's Input schema.
            config: Runtime ToolConfig.

        Returns:
            Validated instance of this tool's Output schema.
        """

    def safe_execute(
        self, input_data: "VulcaTool.Input", config: ToolConfig | None = None
    ) -> "VulcaTool.Output":
        """Framework entry point — wraps execute() with robustness guarantees.

        Args:
            input_data: Input data (must be an instance of this tool's Input schema).
            config: Optional runtime ToolConfig. Defaults to ToolConfig().

        Returns:
            Validated Output instance.
        """
        if not isinstance(input_data, self.Input):
            raise TypeError(
                f"input_data must be an instance of {self.__class__.__name__}.Input, "
                f"got {type(input_data).__name__}"
            )
        if config is None:
            config = ToolConfig()

        result = self.execute(input_data, config)

        # Evidence completeness check + low confidence warning
        if hasattr(result, "evidence") and result.evidence is not None:
            ev = result.evidence
            if ev.confidence < 0.5:
                logger.warning(
                    "Tool %s returned low confidence %.2f: %s",
                    self.name,
                    ev.confidence,
                    ev.summary,
                )

        return result


# ---------------------------------------------------------------------------
# ImageData — cross-platform unified image type
# ---------------------------------------------------------------------------


class ImageData:
    """Cross-platform unified image type with PNG-encoded internal storage.

    Internal storage: PNG bytes (_bytes).

    Factory methods:
        from_bytes(data)      — from raw PNG bytes
        from_numpy(arr)       — from (H, W, C) uint8 RGB ndarray
        from_base64(b64)      — from base64-encoded string
        from_path(path)       — load from file path
        from_pil(image)       — from PIL.Image

    Conversion methods:
        to_bytes()   — PNG bytes
        to_numpy()   — (H, W, C) uint8 RGB ndarray
        to_base64()  — base64-encoded string
        to_pil()     — PIL.Image (RGB)
        save(path)   — write PNG to path
    """

    __slots__ = ("_bytes",)

    def __init__(self, png_bytes: bytes) -> None:
        """Internal constructor — prefer factory methods."""
        if not isinstance(png_bytes, bytes):
            raise TypeError(f"png_bytes must be bytes, got {type(png_bytes).__name__}")
        self._bytes: bytes = png_bytes

    # --- Factory methods ---

    @classmethod
    def from_bytes(cls, data: bytes) -> "ImageData":
        """Create ImageData from raw image bytes (PNG, JPEG, etc.).

        The data is re-encoded as PNG for lossless internal storage.
        """
        pil = Image.open(io.BytesIO(data))
        return cls(_pil_to_png_bytes(pil))

    @classmethod
    def from_numpy(cls, arr: np.ndarray) -> "ImageData":
        """Create ImageData from (H, W, C) uint8 RGB ndarray."""
        if arr.ndim != 3 or arr.shape[2] != 3:
            raise ValueError(
                f"Expected (H, W, 3) uint8 ndarray, got shape {arr.shape}"
            )
        if arr.dtype != np.uint8:
            arr = arr.astype(np.uint8)
        pil = Image.fromarray(arr, mode="RGB")
        return cls(_pil_to_png_bytes(pil))

    @classmethod
    def from_base64(cls, b64: str) -> "ImageData":
        """Create ImageData from base64-encoded image string."""
        raw = base64.b64decode(b64)
        return cls.from_bytes(raw)

    @classmethod
    def from_path(cls, path: str) -> "ImageData":
        """Load ImageData from a file path."""
        pil = Image.open(path)
        return cls(_pil_to_png_bytes(pil))

    @classmethod
    def from_pil(cls, image: Image.Image) -> "ImageData":
        """Create ImageData from a PIL Image."""
        return cls(_pil_to_png_bytes(image))

    # --- Conversion methods ---

    def to_bytes(self) -> bytes:
        """Return PNG-encoded bytes."""
        return self._bytes

    def to_numpy(self) -> np.ndarray:
        """Return (H, W, C) uint8 RGB ndarray."""
        pil = Image.open(io.BytesIO(self._bytes)).convert("RGB")
        return np.array(pil, dtype=np.uint8)

    def to_base64(self) -> str:
        """Return base64-encoded PNG string."""
        return base64.b64encode(self._bytes).decode("ascii")

    def to_pil(self) -> Image.Image:
        """Return PIL Image (RGB mode)."""
        return Image.open(io.BytesIO(self._bytes)).convert("RGB")

    def save(self, path: str) -> None:
        """Write PNG to path."""
        with open(path, "wb") as f:
            f.write(self._bytes)

    def __repr__(self) -> str:
        size = len(self._bytes)
        try:
            pil = self.to_pil()
            return f"<ImageData {pil.width}x{pil.height} RGB, {size} bytes>"
        except Exception:
            return f"<ImageData {size} bytes>"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _pil_to_png_bytes(pil: Image.Image) -> bytes:
    """Convert a PIL image to PNG bytes, normalising to RGB."""
    if pil.mode != "RGB":
        pil = pil.convert("RGB")
    buf = io.BytesIO()
    pil.save(buf, format="PNG", optimize=False, compress_level=1)
    return buf.getvalue()
