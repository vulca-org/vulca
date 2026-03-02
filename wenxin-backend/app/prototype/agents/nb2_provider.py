"""NB2 Provider — Nano Banana 2 (gemini-3.1-flash-image-preview) draft image generator.

Key differences from FLUX/SD providers:
- No seed control (NB2 is internally stochastic, accept_threshold relies on score not seed)
- No negative_prompt parameter — converted to AVOID: clause in positive prompt
- 32K token context: full EvidencePack JSON can be injected, unlike FLUX T5 (512 tokens)
- Internal thinking loop (Plan→Review→Correct) — enabled by thinking_level="High"
- Returns PIL image saved to output_path; AbstractProvider interface maintained

Usage in ablation:
  G condition:  NB2Provider(full_evidence_mode=False) — basic prompt, same as H condition baseline
  Gp condition: NB2Provider(full_evidence_mode=True)  — full EvidencePack in 32K context
"""

from __future__ import annotations

import io
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from app.prototype.agents.draft_provider import AbstractProvider

logger = logging.getLogger(__name__)

__all__ = [
    "NB2Provider",
    "build_full_evidence_prompt",
]

# NB2 image size codes: maps to approximate pixel area
_SIZE_MAP = {
    "0.5K": (512, 512),    # ~0.25 megapixels
    "1K": (1024, 1024),    # ~1 megapixel
    "2K": (2048, 2048),    # ~4 megapixels
    "4K": (4096, 4096),    # ~16 megapixels
}

# Aspect ratio codes NB2 supports
_ASPECT_RATIOS = {"1:1", "4:3", "3:4", "16:9", "9:16"}


def _resolve_image_size(width: int, height: int) -> tuple[str, str]:
    """Map pixel dimensions to NB2 image_size code and aspect_ratio.

    NB2 doesn't accept arbitrary resolutions — we pick the closest preset.
    Returns (image_size, aspect_ratio) as strings.
    """
    # Determine aspect ratio
    ratio = width / max(height, 1)
    if abs(ratio - 1.0) < 0.15:
        aspect = "1:1"
    elif abs(ratio - 4/3) < 0.15:
        aspect = "4:3"
    elif abs(ratio - 3/4) < 0.15:
        aspect = "3:4"
    elif abs(ratio - 16/9) < 0.15:
        aspect = "16:9"
    elif abs(ratio - 9/16) < 0.15:
        aspect = "9:16"
    else:
        aspect = "1:1"  # fallback

    # Determine image size from max dimension
    max_dim = max(width, height)
    if max_dim <= 640:
        size = "0.5K"
    elif max_dim <= 1280:
        size = "1K"
    elif max_dim <= 2560:
        size = "2K"
    else:
        size = "4K"

    return size, aspect


class NB2Provider(AbstractProvider):
    """Nano Banana 2 (gemini-3.1-flash-image-preview) image generation provider.

    Integrates into the existing VULCA-Agent AbstractProvider interface while
    leveraging NB2's 32K token context window for full EvidencePack injection.

    Parameters
    ----------
    api_key : str, optional
        Google API key. Falls back to GOOGLE_API_KEY environment variable.
    thinking_level : str
        "High" (2 internal review passes, better cultural fidelity) or "minimal".
    timeout : int
        Request timeout in seconds.
    """

    MODEL_ID = "gemini-3.1-flash-image-preview"

    def __init__(
        self,
        api_key: Optional[str] = None,
        thinking_level: str = "High",
        timeout: int = 120,
    ) -> None:
        import os
        self._api_key = api_key or os.environ.get("GOOGLE_API_KEY", "")
        if not self._api_key:
            raise ValueError("GOOGLE_API_KEY not set — required for NB2Provider")
        self._thinking_level = thinking_level
        self._timeout = timeout
        self._call_log: list[dict] = []
        # Lazily initialized genai.Client — reused across calls
        self._client: Any = None

    @property
    def model_ref(self) -> str:
        return "nb2:gemini-3.1-flash-image-preview"

    @property
    def call_log(self) -> list[dict]:
        return list(self._call_log)

    def generate(
        self,
        prompt: str,
        negative_prompt: str,
        seed: int,          # Ignored — NB2 stochastic; kept for interface compat
        width: int,
        height: int,
        steps: int,         # Ignored — NB2 handles denoising internally
        sampler: str,       # Ignored — NB2 no sampler param
        output_path: str,
    ) -> str:
        """Generate image via NB2 API and save to output_path.

        seed/steps/sampler are accepted but silently ignored — NB2 does not
        expose these knobs. Each call produces a different image (stochastic).

        Returns the actual output path (with .png extension).
        """
        # Build full prompt: merge negative_prompt as AVOID clause
        full_prompt = _build_nb2_prompt(prompt, negative_prompt)

        image_size, aspect_ratio = _resolve_image_size(width, height)

        out = Path(output_path).with_suffix(".png")
        out.parent.mkdir(parents=True, exist_ok=True)

        t0 = time.monotonic()
        thinking_text = ""
        try:
            img_bytes, thinking_text = self._call_api(
                full_prompt, image_size, aspect_ratio
            )
        except Exception as exc:
            self._log_call(full_prompt, image_size, t0, None, str(exc), thinking_text)
            # Re-raise as appropriate type for FallbackProvider to catch
            msg = str(exc)
            if "timeout" in msg.lower() or "deadline" in msg.lower():
                raise TimeoutError(f"NB2 timeout: {exc}") from exc
            if "connection" in msg.lower() or "network" in msg.lower():
                raise ConnectionError(f"NB2 connection: {exc}") from exc
            raise OSError(f"NB2 API error: {exc}") from exc

        out.write_bytes(img_bytes)
        latency_ms = int((time.monotonic() - t0) * 1000)
        self._log_call(full_prompt, image_size, t0, latency_ms, None, thinking_text)
        logger.info(
            "NB2 generated %s (%s, %dms) thinking=%d chars",
            out.name, image_size, latency_ms, len(thinking_text),
        )
        return str(out)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _call_api(
        self, prompt: str, image_size: str, aspect_ratio: str
    ) -> tuple[bytes, str]:
        """Call NB2 API, return (image_bytes, thinking_text)."""
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ImportError(
                "google-genai package required for NB2Provider: "
                "pip install google-genai"
            ) from exc

        if self._client is None:
            self._client = genai.Client(api_key=self._api_key)
        client = self._client
        config = types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=image_size,
            ),
            thinking_config=types.ThinkingConfig(
                thinking_level=self._thinking_level,
                include_thoughts=True,
            ),
        )

        response = client.models.generate_content(
            model=self.MODEL_ID,
            contents=prompt,
            config=config,
        )

        thinking_text = ""
        result_image_bytes: bytes | None = None

        for part in response.parts:
            # Use explicit None check — part.text can be "" for non-text parts
            if part.text is not None:
                thinking_text += part.text
            else:
                # NB2 may emit multiple image parts: thought images followed by final image.
                # We overwrite each time so the LAST image (final result) is kept.
                img_extracted: bytes | None = None
                try:
                    img = part.as_image()
                    if img is not None:
                        buf = io.BytesIO()
                        img.save(buf, format="PNG")
                        img_extracted = buf.getvalue()
                except Exception:
                    pass
                # Fallback: try inline_data (raw bytes) directly
                if img_extracted is None and hasattr(part, "inline_data"):
                    if part.inline_data and part.inline_data.data:
                        img_extracted = part.inline_data.data
                if img_extracted is not None:
                    result_image_bytes = img_extracted  # overwrite → last image wins

        if result_image_bytes is None:
            raise OSError(
                f"NB2 response contained no image. Parts: "
                f"{[type(p).__name__ for p in response.parts]}"
            )

        return result_image_bytes, thinking_text

    def _log_call(
        self,
        prompt: str,
        image_size: str,
        t0: float,
        latency_ms: Optional[int],
        error: Optional[str],
        thinking_text: str,
    ) -> None:
        self._call_log.append({
            "model": self.MODEL_ID,
            "prompt_len": len(prompt),
            "image_size": image_size,
            "thinking_level": self._thinking_level,
            "thinking_chars": len(thinking_text),
            "latency_ms": latency_ms if latency_ms is not None else int((time.monotonic() - t0) * 1000),
            "error": error,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


def _build_nb2_prompt(prompt: str, negative_prompt: str) -> str:
    """Merge positive prompt and negative_prompt into a single NB2-compatible string.

    NB2/Gemini does not have a native negative_prompt parameter. Instead,
    we append avoidance instructions as a positive clause at the end.
    """
    if not negative_prompt:
        return prompt
    # Convert to "AVOID:" directive — NB2 understands this instruction style
    return f"{prompt}\n\nAVOID the following in the image: {negative_prompt}"


def build_full_evidence_prompt(
    subject: str,
    tradition: str,
    evidence_pack,  # EvidencePack object (from app.prototype.tools.evidence_pack)
) -> tuple[str, str]:
    """Build a rich NB2 prompt from a full EvidencePack, exploiting NB2's 32K context.

    Unlike the FLUX prompt builder (_build_prompt_from_pack, which compresses to ~512 tokens),
    this function serializes the full EvidencePack into structured natural language,
    allowing NB2's Gemini encoder to process the complete cultural knowledge base.

    The key difference: FLUX T5 truncates at ~512 tokens → most EvidencePack content is lost.
    NB2 Gemini accepts 32K tokens → the full cultural context enters the generation loop.

    Args:
        subject: The artwork subject (e.g. "bamboo in mist")
        tradition: The cultural tradition key (e.g. "chinese_xieyi")
        evidence_pack: EvidencePack dataclass object from scout_service.build_evidence_pack()

    Returns:
        (positive_prompt, negative_prompt) — negative merged into positive by _build_nb2_prompt.
    """
    # Normalize: accept EvidencePack object or fallback gracefully
    # EvidencePack fields: anchors (TerminologyAnchor), compositions (CompositionReference),
    #                      styles (StyleConstraint), taboos (TabooConstraint)
    try:
        anchors = getattr(evidence_pack, "anchors", [])
        compositions = getattr(evidence_pack, "compositions", [])
        styles = getattr(evidence_pack, "styles", [])
        taboos = getattr(evidence_pack, "taboos", [])
        coverage = getattr(evidence_pack, "coverage", 0.0)
    except Exception:
        # Graceful fallback: return minimal prompt if pack is malformed
        return (
            f"Create a {tradition.replace('_', ' ')} artwork depicting: {subject}",
            ""
        )

    lines: list[str] = []

    # --- Core task (always present) ---
    lines.append(f"Create a {tradition.replace('_', ' ')} artwork depicting: {subject}")
    lines.append(f"Cultural tradition: {tradition.replace('_', ' ')}")
    if coverage > 0:
        lines.append(f"Evidence coverage: {coverage:.0%}")
    lines.append("")

    # --- Style constraints (StyleConstraint: .attribute, .value, .tradition_source) ---
    if styles:
        lines.append("STYLE REQUIREMENTS:")
        for s in styles:
            lines.append(f"  • {s.attribute}: {s.value}")
        lines.append("")

    # --- Terminology anchors (TerminologyAnchor: .term, .definition, .usage_hint, .l_levels) ---
    # Unlike FLUX which compresses to top 5, NB2 gets ALL anchors with full context
    if anchors:
        lines.append("CULTURAL TERMS TO EMBODY (each term carries philosophical weight):")
        for anchor in anchors:
            layer_info = f" [{', '.join(anchor.l_levels)}]" if anchor.l_levels else ""
            usage = f" — {anchor.usage_hint}" if anchor.usage_hint else ""
            defn = f": {anchor.definition[:120]}" if anchor.definition else ""
            lines.append(f"  • {anchor.term}{layer_info}{defn}{usage}")
        lines.append("")

    # --- Composition references (CompositionReference: .description, .spatial_strategy, .example_prompt_fragment) ---
    if compositions:
        lines.append("COMPOSITION GUIDANCE:")
        for comp in compositions:
            lines.append(f"  • Strategy: {comp.spatial_strategy}")
            if comp.description:
                lines.append(f"    {comp.description}")
            if comp.example_prompt_fragment:
                lines.append(f"    Prompt fragment: {comp.example_prompt_fragment}")
        lines.append("")

    # --- Taboo constraints (TabooConstraint: .description, .severity, .tradition_source) ---
    # Group by severity: critical first, then others
    critical_taboos = [t for t in taboos if t.severity == "critical"]
    other_taboos = [t for t in taboos if t.severity != "critical"]
    negative_parts: list[str] = []

    if critical_taboos:
        lines.append("⚠️  CRITICAL TABOOS — violation makes the artwork culturally offensive:")
        for tab in critical_taboos:
            lines.append(f"  ✗ {tab.description}")
            negative_parts.append(tab.description)
        lines.append("")

    if other_taboos:
        lines.append("AVOID in this tradition:")
        for tab in other_taboos:
            severity_tag = f"[{tab.severity}] " if tab.severity not in ("", "medium") else ""
            lines.append(f"  ✗ {severity_tag}{tab.description}")
            negative_parts.append(tab.description)
        lines.append("")

    # --- Coverage note for NB2's thinking process ---
    if coverage < 0.5:
        lines.append(
            "NOTE: Evidence coverage is low for this tradition. "
            "Apply your general knowledge of this cultural art form "
            "to fill gaps in the above guidance."
        )

    positive_prompt = "\n".join(lines).strip()
    negative_prompt = ", ".join(negative_parts) if negative_parts else ""

    return positive_prompt, negative_prompt
