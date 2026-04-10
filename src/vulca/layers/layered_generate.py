"""A-path layered generation library.

Pure orchestration: plan → concurrent provider calls → keying → validate.
Callable from CLI, MCP, SDK, or tests. Providers must implement the
``raw_prompt=True`` contract on their ``generate(...)`` method (the
``raw_rgba`` capability flag — see ``vulca.providers.base.ImageProvider``).
"""
from __future__ import annotations

import asyncio
import base64
import io
import logging
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import numpy as np
from PIL import Image

from vulca.layers.keying import CanvasSpec, KeyingStrategy, get_keying_strategy
from vulca.layers.layered_cache import LayerCache, build_cache_key
from vulca.layers.layered_prompt import TraditionAnchor, build_anchored_layer_prompt
from vulca.layers.types import LayerInfo
from vulca.layers.validate import ValidationReport, ValidationWarning, validate_layer_alpha

logger = logging.getLogger("vulca.layers.layered_generate")

SCHEMA_VERSION = "0.14"

_RETRY_BUDGET = 2  # additional attempts after the first; 3 total.


@dataclass
class LayerOutcome:
    ok: bool
    info: LayerInfo
    rgba_path: str = ""
    cache_hit: bool = False
    attempts: int = 1
    validation: ValidationReport | None = None
    raw_rgb_bytes: bytes | None = None


LayerFailureReason = Literal["generation_failed", "validation_failed"]


@dataclass
class LayerFailure:
    layer_id: str
    role: str
    reason: LayerFailureReason
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


async def _call_provider(provider, prompt: str, reference_image_b64: str = "") -> bytes:
    """Call provider and return raw image bytes (PNG)."""
    kwargs: dict = {"prompt": prompt, "raw_prompt": True}
    if reference_image_b64:
        kwargs["reference_image_b64"] = reference_image_b64
    result = await provider.generate(**kwargs)
    b64 = result.image_b64 if hasattr(result, "image_b64") else result
    return base64.b64decode(b64)


async def _call_provider_with_retry(
    provider, prompt: str, layer_name: str,
    reference_image_b64: str = "",
) -> tuple[bytes, int]:
    """Call provider with retry budget; return (rgb_bytes, attempts).

    On exhausted budget, raises the last captured exception.
    AssertionError/TypeError/CancelledError propagate immediately — they
    are programmer bugs or control flow, not transient provider failures.
    """
    rgb_bytes: bytes | None = None
    last_exc: Exception | None = None
    for attempt in range(_RETRY_BUDGET + 1):
        attempts = attempt + 1
        try:
            rgb_bytes = await _call_provider(provider, prompt, reference_image_b64)
            return rgb_bytes, attempts
        except (AssertionError, TypeError, asyncio.CancelledError):
            raise
        except Exception as exc:
            last_exc = exc
            logger.warning(
                "provider failed for layer %s (attempt %d/%d): %s",
                layer_name, attempts, _RETRY_BUDGET + 1, exc,
            )
            if attempt < _RETRY_BUDGET:
                delay = random.uniform(0, 0.5 * (2 ** attempt))
                await asyncio.sleep(delay)
    assert last_exc is not None  # type narrowing
    # Attach attempts count so callers can report it without duplicating
    # the retry budget arithmetic (see generate_one_layer).
    last_exc.attempts = _RETRY_BUDGET + 1  # type: ignore[attr-defined]
    raise last_exc


_REPORT_SCHEMA_VERSION = 1


def _report_to_dict(report: ValidationReport) -> dict:
    """Serialize ValidationReport to a JSON-friendly dict for sidecar storage."""
    import dataclasses
    d = dataclasses.asdict(report)
    d["schema_version"] = _REPORT_SCHEMA_VERSION
    return d


def _report_from_dict(d: dict) -> ValidationReport | None:
    """Reconstruct a ValidationReport from a sidecar dict.

    Returns None if the sidecar schema version doesn't match — forces
    re-validation so stale/legacy sidecars don't leak bogus reports.
    """
    if d.get("schema_version") != _REPORT_SCHEMA_VERSION:
        return None
    warnings_raw = d.get("warnings") or []
    warnings = [
        ValidationWarning(
            kind=w.get("kind", ""),
            message=w.get("message", ""),
            detail=dict(w.get("detail") or {}),
        )
        for w in warnings_raw
    ]
    return ValidationReport(
        ok=bool(d.get("ok", True)),
        warnings=warnings,
        coverage_actual=float(d.get("coverage_actual", 0.0)),
        position_iou=float(d.get("position_iou", 0.0)),
    )


def _obtain_validation_report(
    *,
    cache_hit: bool,
    cache: LayerCache | None,
    cache_key: str,
    out_path: str,
    position: str,
    coverage: str,
    cache_put_ok: bool,
) -> ValidationReport:
    """Obtain a ValidationReport: from sidecar cache or fresh validation.

    Three branches:
    1. Cache hit with valid sidecar -> reuse persisted report.
    2. Cache hit, sidecar missing/stale -> re-validate, write fresh sidecar.
    3. Fresh generation -> validate from disk, write sidecar.

    Orphan-sidecar guard (v0.13.2 G4): put_report only called when
    cache_put_ok is True (cache body is known to exist on disk).
    """
    cached_report_dict: dict | None = None
    if cache_hit and cache is not None:
        cached_report_dict = cache.get_report(cache_key)

    report: ValidationReport | None = None
    if cached_report_dict is not None:
        report = _report_from_dict(cached_report_dict)

    if report is None:
        if cache_hit and cached_report_dict is None:
            logger.debug(
                "cache sidecar missing for %s, migrating", cache_key,
            )
        rgba = np.array(Image.open(out_path))
        alpha_only = rgba[:, :, 3].astype(np.float32) / 255.0
        report = validate_layer_alpha(alpha_only, position=position, coverage=coverage)
        if cache is not None and cache_put_ok:
            try:
                cache.put_report(cache_key, _report_to_dict(report))
            except Exception as exc:
                logger.warning(
                    "cache.put_report failed for %s (best-effort): %s",
                    cache_key, exc,
                )

    return report


def _apply_alpha(rgb: np.ndarray, alpha: np.ndarray) -> Image.Image:
    """Combine an RGB numpy array with an alpha mask into an RGBA PIL image."""
    assert rgb.shape[:2] == alpha.shape, (
        f"alpha shape {alpha.shape} does not match rgb shape {rgb.shape[:2]}; "
        "keying ran on a different-sized image than the provider returned"
    )
    rgba = np.dstack([rgb, (alpha * 255).astype(np.uint8)])
    return Image.fromarray(rgba)


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
    reference_image_b64: str = "",
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
    raw_rgb: bytes | None = None

    if cache is not None:
        cached = cache.get(cache_key)
        if cached:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            Path(out_path).write_bytes(cached)
            cache_hit = True

    if not cache_hit:
        try:
            rgb_bytes, attempts = await _call_provider_with_retry(
                provider, prompt, layer.name,
                reference_image_b64=reference_image_b64,
            )
        except (AssertionError, TypeError, asyncio.CancelledError):
            # AssertionError/TypeError are Exception subclasses — without
            # this clause they'd fall into the bare `except Exception` below
            # and be silently converted to a failed LayerOutcome.
            # CancelledError is BaseException (Python 3.9+) so it wouldn't
            # be caught below, but we list it explicitly for clarity and
            # forward-compat with older Pythons.
            raise
        except Exception as exc:
            return LayerOutcome(
                ok=False, info=layer, rgba_path="",
                attempts=getattr(exc, "attempts", 1),
            )

        # Normalize to RGB PNG for style_ref (provider may return RGBA).
        _pil_rgb = Image.open(io.BytesIO(rgb_bytes)).convert("RGB")
        _rgb_buf = io.BytesIO()
        _pil_rgb.save(_rgb_buf, format="PNG")
        raw_rgb = _rgb_buf.getvalue()

        rgb = np.array(_pil_rgb)
        alpha = keying.extract_alpha(rgb, canvas)
        rgba_img = _apply_alpha(rgb, alpha)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        rgba_img.save(out_path)
        cache_put_ok = cache is None
        if cache is not None:
            try:
                # v0.13.2 P2 T10: reuse disk bytes — rgba_img.save(out_path)
                # already wrote the PNG above. Avoid PIL re-encoding.
                cache.put(cache_key, Path(out_path).read_bytes())
                cache_put_ok = True
            except Exception as exc:
                logger.warning(
                    "cache.put failed for layer %s (best-effort): %s",
                    layer.name, exc,
                )
    else:
        cache_put_ok = True  # cache hit → body already exists on disk.

    report = _obtain_validation_report(
        cache_hit=cache_hit, cache=cache, cache_key=cache_key,
        out_path=out_path, position=position, coverage=coverage,
        cache_put_ok=cache_put_ok,
    )

    if not report.ok:
        return LayerOutcome(
            ok=False, info=layer, rgba_path="", attempts=attempts,
            validation=report, cache_hit=cache_hit,
        )

    return LayerOutcome(
        ok=True, info=layer, rgba_path=out_path,
        attempts=attempts, validation=report, cache_hit=cache_hit,
        raw_rgb_bytes=raw_rgb,
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
    reference_image_b64: str = "",
) -> LayeredResult:
    """Generate layers with style-ref anchoring: first layer serial, rest parallel."""
    if not plan:
        return LayeredResult()

    keying = get_keying_strategy(key_strategy_name)
    cache = LayerCache(output_dir, enabled=cache_enabled)
    sem = asyncio.Semaphore(parallelism)

    sibling_roles = [l.tradition_role or l.name for l in plan]
    positions = positions or {}
    coverages = coverages or {}

    common_kw = dict(
        anchor=tradition_anchor,
        canvas=canvas,
        keying=keying,
        provider=provider,
        sibling_roles=sibling_roles,
        output_dir=output_dir,
        cache=cache,
        width=width,
        height=height,
    )

    # --- Phase 1: Generate first layer serially (style anchor) ---
    first = plan[0]
    try:
        first_outcome = await generate_one_layer(
            layer=first,
            position=positions.get(first.name, ""),
            coverage=coverages.get(first.name, ""),
            reference_image_b64=reference_image_b64,
            **common_kw,
        )
    except (AssertionError, TypeError, KeyError, AttributeError, ValueError):
        raise
    except Exception:
        logger.exception("unexpected post-provider failure for layer %s", first.name)
        first_outcome = LayerOutcome(ok=False, info=first, rgba_path="", attempts=1)

    # Derive style_ref from first layer's RAW output (before keying).
    # Using keyed RGBA would pass a partially-transparent image as style
    # reference, degrading provider output quality (P1 review finding).
    # Fallback: on cache hit raw_rgb_bytes is None — read cached RGBA,
    # strip alpha, re-encode as RGB. Slightly lossy but RGB data intact.
    style_ref = ""
    if first_outcome.ok and first_outcome.raw_rgb_bytes:
        style_ref = base64.b64encode(first_outcome.raw_rgb_bytes).decode()
    elif first_outcome.ok and first_outcome.rgba_path:
        try:
            _img = Image.open(first_outcome.rgba_path).convert("RGB")
            _buf = io.BytesIO()
            _img.save(_buf, format="PNG")
            style_ref = base64.b64encode(_buf.getvalue()).decode()
        except Exception as exc:
            logger.warning(
                "failed to derive style_ref from cached first layer %s: %s",
                first_outcome.rgba_path, exc,
            )

    # --- Phase 2: Generate remaining layers in parallel with style_ref ---
    remaining = plan[1:]

    async def _run(layer: LayerInfo) -> LayerOutcome:
        async with sem:
            try:
                return await generate_one_layer(
                    layer=layer,
                    position=positions.get(layer.name, ""),
                    coverage=coverages.get(layer.name, ""),
                    reference_image_b64=style_ref,
                    **common_kw,
                )
            except (AssertionError, TypeError, KeyError, AttributeError, ValueError):
                raise
            except Exception:
                logger.exception("unexpected post-provider failure for layer %s", layer.name)
                return LayerOutcome(ok=False, info=layer, rgba_path="", attempts=1)

    if remaining:
        rest_outcomes = list(await asyncio.gather(*(_run(l) for l in remaining)))
    else:
        rest_outcomes = []

    outcomes = [first_outcome] + rest_outcomes

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
