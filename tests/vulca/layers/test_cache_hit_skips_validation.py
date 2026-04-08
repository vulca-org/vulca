"""v0.13.2 P2: cache hit with sidecar skips validate_layer_alpha; legacy
cache entries (no sidecar) auto-migrate by re-validating + writing sidecar."""
from __future__ import annotations

import asyncio
import base64
import io
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from PIL import Image

from vulca.layers.keying import CanvasSpec
from vulca.layers.keying.luminance import LuminanceKeying
from vulca.layers.layered_cache import LayerCache
from vulca.layers.layered_generate import generate_one_layer
from vulca.layers.layered_prompt import TraditionAnchor
from vulca.layers.types import LayerInfo
from vulca.layers.validate import ValidationReport, ValidationWarning


def _png_rgba_bytes(w=32, h=32) -> bytes:
    img = Image.new("RGBA", (w, h), (200, 200, 200, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _png_rgb_bytes(w=32, h=32) -> bytes:
    img = Image.new("RGB", (w, h), (200, 200, 200))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _layer() -> LayerInfo:
    return LayerInfo(
        name="layer1", description="t", z_index=0, content_type="subject",
    )


def _anchor() -> TraditionAnchor:
    return TraditionAnchor(
        canvas_color_hex="#ffffff",
        canvas_description="white paper",
        style_keywords="test",
    )


def _ok_report_dict() -> dict:
    # Matches dataclasses.asdict(ValidationReport(ok=True))
    return {
        "ok": True, "warnings": [], "coverage_actual": 0.5, "position_iou": 0.8,
        "schema_version": 1,
    }


def _kwargs(prov, tmp_path: Path, cache: LayerCache) -> dict:
    return dict(
        layer=_layer(), anchor=_anchor(),
        canvas=CanvasSpec(color=(255, 255, 255)),
        keying=LuminanceKeying(),
        provider=prov,
        sibling_roles=["layer1"],
        output_dir=str(tmp_path),
        cache=cache,
        width=32, height=32,
    )


def test_cache_hit_with_sidecar_skips_validation(tmp_path: Path):
    cache = LayerCache(tmp_path)
    fixed_key = "fixedkey"
    cache.put(fixed_key, _png_rgba_bytes())
    cache.put_report(fixed_key, _ok_report_dict())

    prov = MagicMock()
    prov.generate = AsyncMock(side_effect=AssertionError("provider must NOT be called on cache hit"))
    prov.id = "fake"
    prov.model = "v1"

    with patch("vulca.layers.layered_generate.build_cache_key", return_value=fixed_key), \
         patch("vulca.layers.layered_generate.validate_layer_alpha") as mock_validate:
        outcome = asyncio.run(generate_one_layer(**_kwargs(prov, tmp_path, cache)))

    mock_validate.assert_not_called()
    assert outcome.ok is True
    assert outcome.cache_hit is True
    assert outcome.validation is not None
    assert outcome.validation.ok is True


def test_cache_hit_with_sidecar_preserves_warnings(tmp_path: Path):
    """Warnings round-trip through the sidecar."""
    cache = LayerCache(tmp_path)
    fixed_key = "warnkey"
    cache.put(fixed_key, _png_rgba_bytes())
    cache.put_report(fixed_key, {
        "ok": True,
        "warnings": [
            {"kind": "coverage_drift", "message": "x", "detail": {"a": 1}},
        ],
        "coverage_actual": 0.1,
        "position_iou": 0.2,
        "schema_version": 1,
    })

    prov = MagicMock()
    prov.generate = AsyncMock(side_effect=AssertionError("no"))
    prov.id = "fake"
    prov.model = "v1"

    with patch("vulca.layers.layered_generate.build_cache_key", return_value=fixed_key), \
         patch("vulca.layers.layered_generate.validate_layer_alpha") as mock_validate:
        outcome = asyncio.run(generate_one_layer(**_kwargs(prov, tmp_path, cache)))

    mock_validate.assert_not_called()
    assert outcome.ok is True
    assert outcome.validation is not None
    assert len(outcome.validation.warnings) == 1
    w = outcome.validation.warnings[0]
    assert isinstance(w, ValidationWarning)
    assert w.kind == "coverage_drift"
    assert w.detail == {"a": 1}


def test_cache_hit_without_sidecar_revalidates_and_writes_sidecar(tmp_path: Path):
    """Legacy cache entry (no sidecar) auto-migrates."""
    cache = LayerCache(tmp_path)
    legacy_key = "legacykey"
    cache.put(legacy_key, _png_rgba_bytes())
    assert cache.get_report(legacy_key) is None

    prov = MagicMock()
    prov.generate = AsyncMock(side_effect=AssertionError("provider must NOT be called"))
    prov.id = "fake"
    prov.model = "v1"

    fake_report = ValidationReport(ok=True)
    with patch("vulca.layers.layered_generate.build_cache_key", return_value=legacy_key), \
         patch("vulca.layers.layered_generate.validate_layer_alpha", return_value=fake_report) as mock_validate:
        outcome = asyncio.run(generate_one_layer(**_kwargs(prov, tmp_path, cache)))

    mock_validate.assert_called_once()
    assert outcome.ok is True
    assert cache.get_report(legacy_key) is not None


def test_fresh_generate_writes_sidecar(tmp_path: Path):
    """Cache miss -> generate -> validate -> write PNG + sidecar both."""
    cache = LayerCache(tmp_path)

    class _R:
        def __init__(self, b):
            self.image_b64 = base64.b64encode(b).decode()

    class _Prov:
        id = "fake"
        model = "v1"
        async def generate(self, *, prompt, raw_prompt=False, **kwargs):
            return _R(_png_rgb_bytes())

    fixed_key = "freshkey"
    fake_report = ValidationReport(ok=True)
    with patch("vulca.layers.layered_generate.build_cache_key", return_value=fixed_key), \
         patch("vulca.layers.layered_generate.validate_layer_alpha", return_value=fake_report):
        outcome = asyncio.run(generate_one_layer(**_kwargs(_Prov(), tmp_path, cache)))

    assert outcome.ok is True
    assert outcome.cache_hit is False
    assert cache.get_report(fixed_key) is not None


def test_fresh_generate_cache_put_failure_skips_sidecar(tmp_path: Path):
    """G4 review fix 1: orphan sidecar guard.

    If cache.put raises (best-effort), cache.put_report must NOT run —
    otherwise we'd leave a .report.json with no corresponding PNG body,
    violating the invariant "sidecar presence implies cache body presence".
    """
    cache = LayerCache(tmp_path)

    class _R:
        def __init__(self, b):
            self.image_b64 = base64.b64encode(b).decode()

    class _Prov:
        id = "fake"
        model = "v1"
        async def generate(self, *, prompt, raw_prompt=False, **kwargs):
            return _R(_png_rgb_bytes())

    fixed_key = "orphanguard"
    fake_report = ValidationReport(ok=True)

    put_report_calls: list = []
    real_put_report = cache.put_report

    def tracking_put_report(key, report):
        put_report_calls.append(key)
        real_put_report(key, report)

    cache.put_report = tracking_put_report  # type: ignore[method-assign]

    def boom_put(key, data):
        raise RuntimeError("disk full")

    cache.put = boom_put  # type: ignore[method-assign]

    with patch("vulca.layers.layered_generate.build_cache_key", return_value=fixed_key), \
         patch("vulca.layers.layered_generate.validate_layer_alpha", return_value=fake_report):
        outcome = asyncio.run(generate_one_layer(**_kwargs(_Prov(), tmp_path, cache)))

    assert outcome.ok is True
    # Invariant: no sidecar write when body write failed.
    assert put_report_calls == []
    sidecar = tmp_path / ".layered_cache" / f"{fixed_key}.report.json"
    assert not sidecar.exists()


def test_cache_hit_with_stale_schema_version_revalidates(tmp_path: Path):
    """G4 review fix 2: sidecar schema_version mismatch forces re-validate."""
    cache = LayerCache(tmp_path)
    fixed_key = "stalever"
    cache.put(fixed_key, _png_rgba_bytes())
    # Sidecar from a hypothetical future/older schema version.
    cache.put_report(fixed_key, {
        "ok": True, "warnings": [], "coverage_actual": 0.5,
        "position_iou": 0.8, "schema_version": 999,
    })

    prov = MagicMock()
    prov.generate = AsyncMock(side_effect=AssertionError("provider must NOT be called"))
    prov.id = "fake"
    prov.model = "v1"

    fake_report = ValidationReport(ok=True)
    with patch("vulca.layers.layered_generate.build_cache_key", return_value=fixed_key), \
         patch("vulca.layers.layered_generate.validate_layer_alpha", return_value=fake_report) as mock_validate:
        outcome = asyncio.run(generate_one_layer(**_kwargs(prov, tmp_path, cache)))

    # Stale sidecar -> re-validate (fall-through like missing sidecar).
    mock_validate.assert_called_once()
    assert outcome.ok is True
    # Sidecar rewritten with current schema_version.
    loaded = cache.get_report(fixed_key)
    assert loaded is not None
    assert loaded.get("schema_version") == 1
