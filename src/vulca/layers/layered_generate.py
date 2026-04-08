"""A-path layered generation library.

Pure orchestration: plan → concurrent provider calls → keying → validate.
Decoupled from the pipeline so it can be called from CLI, MCP, SDK, or tests.
"""
from __future__ import annotations

import base64
import io
import logging
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

from vulca.layers.keying import CanvasSpec, KeyingStrategy
from vulca.layers.layered_cache import LayerCache, build_cache_key
from vulca.layers.layered_prompt import TraditionAnchor, build_anchored_layer_prompt
from vulca.layers.types import LayerInfo
from vulca.layers.validate import ValidationReport, validate_layer_alpha

logger = logging.getLogger("vulca.layers.layered_generate")

SCHEMA_VERSION = "0.13"


@dataclass
class LayerOutcome:
    ok: bool
    info: LayerInfo
    rgba_path: str = ""
    cache_hit: bool = False
    attempts: int = 1
    validation: ValidationReport | None = None


@dataclass
class LayerFailure:
    layer_id: str
    role: str
    reason: str
    attempts: int = 1


@dataclass
class LayeredResult:
    layers: list[LayerOutcome] = field(default_factory=list)
    failed: list[LayerFailure] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return not self.failed

    @property
    def is_usable(self) -> bool:
        if not self.layers:
            return False
        has_subject = any(
            l.info.content_type in ("subject", "line_art", "color_block", "color_wash", "detail")
            for l in self.layers
        )
        return has_subject


def _provider_id_of(provider) -> str:
    return getattr(provider, "id", None) or provider.__class__.__name__


def _provider_model_of(provider) -> str:
    return getattr(provider, "model", None) or "unknown"


async def _call_provider(provider, prompt: str) -> bytes:
    """Call provider and return raw image bytes (PNG)."""
    result = await provider.generate(prompt=prompt, raw_prompt=True)
    b64 = result.image_b64 if hasattr(result, "image_b64") else result
    return base64.b64decode(b64)


def _apply_alpha(rgb_bytes: bytes, alpha: np.ndarray) -> Image.Image:
    img = Image.open(io.BytesIO(rgb_bytes)).convert("RGB")
    rgb = np.array(img)
    if rgb.shape[:2] != alpha.shape:
        a_img = Image.fromarray((alpha * 255).astype(np.uint8))
        a_img = a_img.resize((rgb.shape[1], rgb.shape[0]), Image.BILINEAR)
        alpha = np.array(a_img).astype(np.float32) / 255.0
    rgba = np.dstack([rgb, (alpha * 255).astype(np.uint8)])
    return Image.fromarray(rgba, mode="RGBA")


async def generate_one_layer(
    *,
    layer: LayerInfo,
    anchor: TraditionAnchor,
    canvas: CanvasSpec,
    keying: KeyingStrategy,
    provider,
    sibling_roles: list[str],
    output_dir: str,
    position: str = "",
    coverage: str = "",
    cache: LayerCache | None = None,
) -> LayerOutcome:
    prompt = build_anchored_layer_prompt(
        layer, anchor=anchor, sibling_roles=sibling_roles,
        position=position, coverage=coverage,
    )

    cache_key = build_cache_key(
        provider_id=_provider_id_of(provider),
        model_id=_provider_model_of(provider),
        prompt=prompt,
        canvas_color="#%02x%02x%02x" % canvas.color,
        canvas_tolerance=canvas.tolerance,
        schema_version=SCHEMA_VERSION,
    )

    out_path = str(Path(output_dir) / f"{layer.name}.png")
    cache_hit = False

    if cache is not None:
        cached = cache.get(cache_key)
        if cached:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            Path(out_path).write_bytes(cached)
            cache_hit = True

    if not cache_hit:
        try:
            rgb_bytes = await _call_provider(provider, prompt)
        except Exception as exc:
            logger.warning("provider failed for layer %s: %s", layer.name, exc)
            return LayerOutcome(ok=False, info=layer, rgba_path="", attempts=1)

        rgb = np.array(Image.open(io.BytesIO(rgb_bytes)).convert("RGB"))
        alpha = keying.extract_alpha(rgb, canvas)
        rgba_img = _apply_alpha(rgb_bytes, alpha)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        rgba_img.save(out_path)
        if cache is not None:
            buf = io.BytesIO()
            rgba_img.save(buf, format="PNG")
            cache.put(cache_key, buf.getvalue())

    rgba = np.array(Image.open(out_path))
    alpha_only = rgba[:, :, 3].astype(np.float32) / 255.0
    report = validate_layer_alpha(alpha_only, position=position, coverage=coverage)

    if not report.ok:
        return LayerOutcome(
            ok=False, info=layer, rgba_path="", attempts=1,
            validation=report, cache_hit=cache_hit,
        )

    return LayerOutcome(
        ok=True, info=layer, rgba_path=out_path,
        attempts=1, validation=report, cache_hit=cache_hit,
    )
