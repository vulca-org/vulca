"""A-path layered generation library.

Pure orchestration: plan → concurrent provider calls → keying → validate.
Decoupled from the pipeline so it can be called from CLI, MCP, SDK, or tests.
"""
from __future__ import annotations

import asyncio
import base64
import io
import logging
import random
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

from vulca.layers.keying import CanvasSpec, KeyingStrategy, get_keying_strategy
from vulca.layers.layered_cache import LayerCache, build_cache_key
from vulca.layers.layered_prompt import TraditionAnchor, build_anchored_layer_prompt
from vulca.layers.types import LayerInfo
from vulca.layers.validate import ValidationReport, validate_layer_alpha

logger = logging.getLogger("vulca.layers.layered_generate")

SCHEMA_VERSION = "0.13"

_RETRY_BUDGET = 2  # additional attempts after the first; 3 total.


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
    validation: ValidationReport | None = None


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
    assert rgb.shape[:2] == alpha.shape, (
        f"alpha shape {alpha.shape} does not match rgb shape {rgb.shape[:2]}; "
        "keying ran on a different-sized image than the provider returned"
    )
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
    width: int = 0,
    height: int = 0,
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
        key_strategy=keying.__class__.__name__,
        key_strategy_version=int(getattr(keying, "cache_version", 1)),
        canvas_invert=bool(getattr(canvas, "invert", False)),
        width=int(width),
        height=int(height),
    )

    out_path = str(Path(output_dir) / f"{layer.name}.png")
    cache_hit = False
    attempts = 1  # default: cache hit reports 1 (one layer operation completed)

    if cache is not None:
        cached = cache.get(cache_key)
        if cached:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            Path(out_path).write_bytes(cached)
            cache_hit = True

    if not cache_hit:
        # In-process retry budget for provider (generation_failed) only.
        # Validation failures are deterministic and never retried (handled below).
        # Programmer bugs (AssertionError/TypeError) and control flow
        # (CancelledError) propagate — they are not "transient provider failures."
        rgb_bytes: bytes | None = None
        last_exc: Exception | None = None
        for attempt in range(_RETRY_BUDGET + 1):
            attempts = attempt + 1
            try:
                rgb_bytes = await _call_provider(provider, prompt)
                last_exc = None
                break
            except (AssertionError, TypeError, asyncio.CancelledError):
                # Not a transient provider failure — surface immediately.
                raise
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "provider failed for layer %s (attempt %d/%d): %s",
                    layer.name, attempts, _RETRY_BUDGET + 1, exc,
                )
                if attempt < _RETRY_BUDGET:
                    delay = random.uniform(0, 0.5 * (2 ** attempt))
                    await asyncio.sleep(delay)
        if last_exc is not None:
            return LayerOutcome(
                ok=False, info=layer, rgba_path="", attempts=attempts,
            )
        assert rgb_bytes is not None  # type narrowing for the next block

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
            ok=False, info=layer, rgba_path="", attempts=attempts,
            validation=report, cache_hit=cache_hit,
        )

    return LayerOutcome(
        ok=True, info=layer, rgba_path=out_path,
        attempts=attempts, validation=report, cache_hit=cache_hit,
    )


async def layered_generate(
    *,
    plan: list[LayerInfo],
    tradition_anchor: TraditionAnchor,
    canvas: CanvasSpec,
    key_strategy_name: str,
    provider,
    output_dir: str,
    positions: dict[str, str] | None = None,
    coverages: dict[str, str] | None = None,
    parallelism: int = 4,
    cache_enabled: bool = True,
    width: int = 0,
    height: int = 0,
) -> LayeredResult:
    """Concurrently generate every layer in the plan, key, validate, and assemble."""
    keying = get_keying_strategy(key_strategy_name)
    cache = LayerCache(output_dir, enabled=cache_enabled)
    sem = asyncio.Semaphore(parallelism)

    sibling_roles = [l.tradition_role or l.name for l in plan]
    positions = positions or {}
    coverages = coverages or {}

    async def _run(layer: LayerInfo) -> LayerOutcome:
        async with sem:
            try:
                return await generate_one_layer(
                    layer=layer,
                    anchor=tradition_anchor,
                    canvas=canvas,
                    keying=keying,
                    provider=provider,
                    sibling_roles=sibling_roles,
                    output_dir=output_dir,
                    position=positions.get(layer.name, ""),
                    coverage=coverages.get(layer.name, ""),
                    cache=cache,
                    width=width,
                    height=height,
                )
            except AssertionError:
                # Programmer/internal bug — surface loudly. Do not collapse.
                raise
            except Exception:
                logger.exception("unexpected failure for layer %s", layer.name)
                return LayerOutcome(ok=False, info=layer, rgba_path="", attempts=1)

    outcomes = await asyncio.gather(*(_run(l) for l in plan))

    layers_ok = [o for o in outcomes if o.ok]
    layers_failed = [
        LayerFailure(
            layer_id=o.info.id,
            role=o.info.tradition_role or o.info.name,
            reason=("validation_failed" if o.validation else "generation_failed"),
            attempts=o.attempts,
            validation=o.validation,
        )
        for o in outcomes if not o.ok
    ]
    return LayeredResult(layers=layers_ok, failed=layers_failed)
