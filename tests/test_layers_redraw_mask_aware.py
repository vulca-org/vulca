"""v0.20 — layers_redraw mask-aware routing unit tests.

Spec: docs/superpowers/specs/2026-04-27-v0.20-mask-aware-redraw-routing-design.md

Coverage matrix (spec D1):
1. ``test_sparse_route_predicate`` — B1: live-alpha sparsity decision
   (single-region 3.3% → sparse via area_pct; multi-instance 6 blobs at
   8% → sparse via bbox_fill; 50% solid block → dense).
2. ``test_mask_polarity_*`` — B2: RGBA mode + correct edit/preserve
   polarity + hard binary {0,255} (pins the v2→v2.1 polarity bug).
3. ``test_capability_fallback_*`` — B6: auto/inpaint routes fall back
   to img2img on providers without ``inpaint_with_mask``.
4. ``test_dimension_resize_round_trip`` — B8: 4032×3024 layer →
   1024-class API call → upsampled back to original canvas → preserve_alpha
   uses ORIGINAL canvas alpha not resized.
5. ``test_redraw_merged_unchanged`` — B7 deferral pin: merged redraw
   never enters the inpaint path in v0.20.

These are pure-Python unit tests using mock providers; no real OpenAI
calls. The real-provider ship-gate lives in
``test_layers_redraw_real_provider_v020.py`` behind
``@pytest.mark.real_provider``.
"""
from __future__ import annotations

import asyncio
import base64
import io
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from vulca.layers.manifest import write_manifest
from vulca.layers.types import LayerInfo


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _png_b64(img: Image.Image) -> str:
    """Encode a PIL image to base64 PNG (matches provider response shape)."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


class _StubInpaintResult:
    """Mimics ImageResult for our stubbed inpaint provider."""
    def __init__(self, image_b64: str, mime: str = "image/png"):
        self.image_b64 = image_b64
        self.mime = mime
        self.metadata: dict = {}


class _CapableProvider:
    """Mock provider that DOES implement inpaint_with_mask.

    Captures the image+mask bytes seen for assertions; returns a
    deterministic 1024×1024 cream PNG. Lets unit tests verify the
    inpaint path is taken without burning real OpenAI budget.
    """
    capabilities = frozenset({"raw_rgba"})

    def __init__(self):
        self.inpaint_calls: list[dict] = []
        self.generate_calls: list[dict] = []

    async def generate(self, prompt: str, **kwargs):
        self.generate_calls.append({"prompt": prompt, **kwargs})
        # Return a small deterministic image so the legacy path completes.
        out = Image.new("RGB", (1024, 1024), (160, 200, 80))
        return _StubInpaintResult(_png_b64(out))

    async def inpaint_with_mask(
        self, *, image_path: str, mask_path: str, prompt: str,
        tradition: str = "default", size: str = "",
    ):
        with open(image_path, "rb") as fh_img, open(mask_path, "rb") as fh_mask:
            image_bytes = fh_img.read()
            mask_bytes = fh_mask.read()
        # Capture the bytes the redraw path uploaded for downstream asserts.
        self.inpaint_calls.append({
            "image_bytes": image_bytes,
            "mask_bytes": mask_bytes,
            "prompt": prompt,
            "tradition": tradition,
            "size": size,
        })
        # Return a deterministic cream-colored PNG at API size; downstream
        # _fit_into_canvas will resize back to canvas, then preserve_alpha
        # re-applies the source alpha — so the actual content is irrelevant
        # for routing/structural unit tests.
        api_w, api_h = (1024, 1024)
        with Image.open(io.BytesIO(image_bytes)) as probe:
            api_w, api_h = probe.size
        out = Image.new("RGB", (api_w, api_h), (200, 180, 120))
        return _StubInpaintResult(_png_b64(out))


class _IncapableProvider:
    """Mock provider WITHOUT inpaint_with_mask (mimics gemini/comfyui/mock)."""
    capabilities = frozenset({"raw_rgba"})

    def __init__(self):
        self.generate_calls: list[dict] = []

    async def generate(self, prompt: str, **kwargs):
        self.generate_calls.append({"prompt": prompt, **kwargs})
        out = Image.new("RGB", (1024, 1024), (130, 160, 110))
        return _StubInpaintResult(_png_b64(out))


def _setup_layer(
    tmp_path: Path,
    *,
    canvas_size: tuple[int, int] = (256, 256),
    alpha_factory=None,
    layer_name: str = "fg",
) -> Path:
    """Build a single-layer artwork dir with explicit alpha shape.

    ``alpha_factory(canvas_size) -> PIL.Image (mode L)`` controls the
    alpha pattern (sparse, dense, multi-instance, etc).
    """
    canvas_w, canvas_h = canvas_size
    if alpha_factory is None:
        # Default: 50% center block (dense, single region).
        alpha = Image.new("L", canvas_size, 0)
        center = Image.new("L", (canvas_w // 2, canvas_h // 2), 255)
        alpha.paste(center, (canvas_w // 4, canvas_h // 4))
    else:
        alpha = alpha_factory(canvas_size)
    rgb = Image.new("RGB", canvas_size, (180, 64, 32))
    rgba = Image.merge("RGBA", (*rgb.split(), alpha))
    rgba.save(str(tmp_path / f"{layer_name}.png"))
    Image.new("RGB", canvas_size, (100, 100, 100)).save(str(tmp_path / "source.png"))

    fg = LayerInfo(
        name=layer_name, description="foreground subject",
        z_index=1, content_type="subject",
    )
    write_manifest(
        [fg],
        output_dir=str(tmp_path),
        width=canvas_w, height=canvas_h,
        source_image="source.png",
    )
    return tmp_path


# ---------------------------------------------------------------------------
# 1. Sparsity predicate (spec B1)
# ---------------------------------------------------------------------------

class TestSparsityPredicate:
    def test_dense_solid_block_is_not_sparse(self):
        """50% solid block → dense (area_pct=50, bbox_fill=1.0)."""
        from vulca.layers.redraw import _compute_sparsity

        alpha = Image.new("L", (1000, 1000), 0)
        block = Image.new("L", (700, 700), 255)
        alpha.paste(block, (150, 150))
        sparse, area_pct, bbox_fill = _compute_sparsity(alpha)
        assert not sparse
        assert 49.0 <= area_pct <= 50.0
        assert bbox_fill == pytest.approx(1.0, abs=0.01)

    def test_small_single_region_is_sparse_via_area(self):
        """3.3% area_pct (IMG_6847 flower_cluster_c case) → sparse via area."""
        from vulca.layers.redraw import _compute_sparsity

        alpha = Image.new("L", (1000, 1000), 0)
        # 180×180 solid = 3.24% — within IMG_6847 range
        block = Image.new("L", (180, 180), 255)
        alpha.paste(block, (50, 50))
        sparse, area_pct, bbox_fill = _compute_sparsity(alpha)
        assert sparse
        assert 3.0 <= area_pct <= 3.5

    def test_multi_instance_fragmented_is_sparse_via_bbox_fill(self):
        """Six disconnected 1.5% blobs spread across canvas → sparse via bbox_fill.

        Mimics Scottish row-of-6-lanterns case: 8.05% total area but
        bbox_fill < 0.5 because the union bbox spans most of the canvas
        while each blob is tiny.
        """
        from vulca.layers.redraw import _compute_sparsity

        canvas = (1000, 1000)
        alpha = Image.new("L", canvas, 0)
        blob = Image.new("L", (115, 115), 255)
        # Spread 6 blobs across the canvas at corners + mid edges
        positions = [
            (50, 50), (435, 50), (835, 50),
            (50, 835), (435, 835), (835, 835),
        ]
        for (x, y) in positions:
            alpha.paste(blob, (x, y))
        sparse, area_pct, bbox_fill = _compute_sparsity(alpha)
        assert sparse, f"expected sparse; got area_pct={area_pct} bbox_fill={bbox_fill}"
        # Total area ≈ 6 × 1.32% = 7.93% — above the 5% area threshold,
        # so the predicate must catch it via bbox_fill < 0.5.
        assert area_pct > 5.0
        assert bbox_fill < 0.5

    def test_empty_alpha_returns_zero_metrics(self):
        from vulca.layers.redraw import _compute_sparsity

        alpha = Image.new("L", (100, 100), 0)
        sparse, area_pct, bbox_fill = _compute_sparsity(alpha)
        # All-zero alpha: sparse predicate returns False (degenerate path
        # raises ValueError upstream in redraw_layer; predicate itself
        # just reports the math).
        assert area_pct == 0.0
        assert bbox_fill == 0.0


# ---------------------------------------------------------------------------
# 2. Mask construction polarity + hard binary (spec B2 + D1.2)
# ---------------------------------------------------------------------------

class TestMaskConstruction:
    def test_mask_is_rgba_mode(self):
        from vulca.layers.redraw import _build_inpaint_mask

        alpha = Image.new("L", (200, 200), 0)
        alpha.paste(Image.new("L", (50, 50), 255), (75, 75))
        mask = _build_inpaint_mask(alpha)
        assert mask.mode == "RGBA"

    def test_mask_polarity_invariant_pins_v2_to_v2_1_bug(self):
        """Polarity invariant pinned by D1.2 unit test in spec.

        v2 codex spec set ``preserve_channel = subject`` which would
        produce mask alpha=255 over subject (PRESERVE) and alpha=0 over
        empty (EDIT) — the OPPOSITE of what redraw needs. v2.1 surgical
        patch corrected to ``ImageOps.invert(subject)``. This test pins
        the corrected polarity from regressing.
        """
        from vulca.layers.redraw import _build_inpaint_mask

        alpha = Image.new("L", (200, 200), 0)
        alpha.paste(Image.new("L", (50, 50), 255), (75, 75))
        mask = _build_inpaint_mask(alpha)
        mask_alpha = np.array(mask.split()[-1])
        src_alpha = np.array(alpha)

        # Subject pixels (src alpha > 0) → mask alpha == 0 (EDIT zone).
        assert np.all(mask_alpha[src_alpha > 0] == 0), (
            "polarity inverted: subject pixels must be EDIT zone "
            "(mask alpha=0) under OpenAI's edit/preserve convention"
        )
        # Empty pixels (src alpha == 0) → mask alpha == 255 (PRESERVE zone).
        assert np.all(mask_alpha[src_alpha == 0] == 255), (
            "polarity inverted: empty pixels must be PRESERVE zone "
            "(mask alpha=255)"
        )

    def test_mask_is_hard_binary_no_intermediate_values(self):
        """{0, 255} only — no GaussianBlur. Intermediate alpha values are
        undefined behavior under OpenAI's mask convention (spec B2)."""
        from vulca.layers.redraw import _build_inpaint_mask

        alpha = Image.new("L", (200, 200), 0)
        # Soft-edged source (anti-aliased disc) — output mask must STILL
        # be hard binary because B2 thresholds at v > 0 before inversion.
        from PIL import ImageDraw
        d = ImageDraw.Draw(alpha)
        d.ellipse((50, 50, 150, 150), fill=200)
        mask = _build_inpaint_mask(alpha)
        unique = np.unique(np.array(mask.split()[-1]))
        assert set(unique.tolist()) <= {0, 255}, (
            f"mask must be hard binary {{0, 255}}; got {unique.tolist()}"
        )


# ---------------------------------------------------------------------------
# 3. Capability gate fallback (spec B6)
# ---------------------------------------------------------------------------

class TestCapabilityFallback:
    def test_route_inpaint_falls_back_when_provider_incapable(
        self, tmp_path, monkeypatch, caplog
    ):
        """route='inpaint' on an incapable provider → warning + img2img fallback."""
        import logging

        from vulca.layers import redraw as redraw_module
        from vulca.layers.manifest import load_manifest

        # 30% center block (dense) — but route='inpaint' forces inpaint
        # consideration regardless of sparsity; capability gate should fire.
        def factory(size):
            w, h = size
            a = Image.new("L", size, 0)
            a.paste(Image.new("L", (int(w * 0.55), int(h * 0.55)), 255),
                    (int(w * 0.225), int(h * 0.225)))
            return a

        _setup_layer(tmp_path, canvas_size=(256, 256), alpha_factory=factory)
        artwork = load_manifest(str(tmp_path))

        incapable = _IncapableProvider()
        # `get_image_provider` is imported inside redraw_layer (lazy);
        # patch at the source module so the lazy import sees our stub.
        import vulca.providers as providers_mod
        monkeypatch.setattr(
            providers_mod, "get_image_provider",
            lambda name, api_key="": incapable,
        )

        with caplog.at_level(logging.WARNING, logger="vulca.layers"):
            _run(redraw_module.redraw_layer(
                artwork, layer_name="fg", instruction="brighter",
                provider="incapable_stub", artwork_dir=str(tmp_path),
                route="inpaint",
            ))

        assert len(incapable.generate_calls) == 1, (
            "explicit route='inpaint' on incapable provider should fall back to generate"
        )
        warned = any(
            "lacks inpaint_with_mask" in rec.message
            for rec in caplog.records
        )
        assert warned, "expected explicit warning when explicit inpaint route falls back"

    def test_route_auto_with_sparse_layer_uses_inpaint_when_capable(
        self, tmp_path, monkeypatch, caplog
    ):
        """route='auto' on a sparse layer + capable provider → inpaint path."""
        import logging

        from vulca.layers import redraw as redraw_module
        from vulca.layers.manifest import load_manifest

        # Sparse single-region — mimics IMG_6847 flower_cluster_c
        def factory(size):
            w, h = size
            a = Image.new("L", size, 0)
            a.paste(Image.new("L", (int(w * 0.18), int(h * 0.18)), 255),
                    (int(w * 0.4), int(h * 0.4)))
            return a

        _setup_layer(tmp_path, canvas_size=(256, 256), alpha_factory=factory)
        artwork = load_manifest(str(tmp_path))

        capable = _CapableProvider()
        import vulca.providers as providers_mod
        monkeypatch.setattr(
            providers_mod, "get_image_provider",
            lambda name, api_key="": capable,
        )

        with caplog.at_level(logging.INFO, logger="vulca.layers"):
            _run(redraw_module.redraw_layer(
                artwork, layer_name="fg", instruction="brighter",
                provider="capable_stub", artwork_dir=str(tmp_path),
                route="auto",
            ))

        assert len(capable.inpaint_calls) == 1, (
            "auto route on sparse layer with capable provider should use inpaint"
        )
        assert len(capable.generate_calls) == 0, "should NOT have hit generate"
        # Advisory log line present.
        assert any(
            "route_chosen=inpaint" in rec.message
            for rec in caplog.records
        ), "expected route_chosen=inpaint advisory log line"

    def test_route_auto_with_dense_layer_uses_img2img_even_when_capable(
        self, tmp_path, monkeypatch
    ):
        """route='auto' on a dense layer → img2img path (predicate gate)."""
        from vulca.layers import redraw as redraw_module
        from vulca.layers.manifest import load_manifest

        # Dense — 50% solid block
        _setup_layer(tmp_path, canvas_size=(256, 256))
        artwork = load_manifest(str(tmp_path))

        capable = _CapableProvider()
        import vulca.providers as providers_mod
        monkeypatch.setattr(
            providers_mod, "get_image_provider",
            lambda name, api_key="": capable,
        )

        _run(redraw_module.redraw_layer(
            artwork, layer_name="fg", instruction="brighter",
            provider="capable_stub", artwork_dir=str(tmp_path),
            route="auto",
        ))

        assert len(capable.generate_calls) == 1
        assert len(capable.inpaint_calls) == 0, (
            "dense layer should stay on img2img even when provider is capable"
        )

    def test_route_img2img_explicit_skips_inpaint_even_on_sparse(
        self, tmp_path, monkeypatch
    ):
        """route='img2img' is the legacy opt-out — sparse + capable should still img2img."""
        from vulca.layers import redraw as redraw_module
        from vulca.layers.manifest import load_manifest

        def factory(size):
            w, h = size
            a = Image.new("L", size, 0)
            a.paste(Image.new("L", (int(w * 0.18), int(h * 0.18)), 255),
                    (int(w * 0.4), int(h * 0.4)))
            return a

        _setup_layer(tmp_path, canvas_size=(256, 256), alpha_factory=factory)
        artwork = load_manifest(str(tmp_path))

        capable = _CapableProvider()
        import vulca.providers as providers_mod
        monkeypatch.setattr(
            providers_mod, "get_image_provider",
            lambda name, api_key="": capable,
        )

        _run(redraw_module.redraw_layer(
            artwork, layer_name="fg", instruction="brighter",
            provider="capable_stub", artwork_dir=str(tmp_path),
            route="img2img",
        ))

        assert len(capable.generate_calls) == 1
        assert len(capable.inpaint_calls) == 0


# ---------------------------------------------------------------------------
# 4. Dimension resize round-trip (spec B8)
# ---------------------------------------------------------------------------

class TestDimensionResize:
    def test_pick_inpaint_size_matches_aspect_ratio(self):
        from vulca.layers.redraw import _pick_inpaint_size

        # Landscape aspect (4032×3024 IMG_6847 case → 1.333:1)
        assert _pick_inpaint_size(4032, 3024) == (1536, 1024)
        # Portrait
        assert _pick_inpaint_size(3024, 4032) == (1024, 1536)
        # Square
        assert _pick_inpaint_size(1024, 1024) == (1024, 1024)
        # Edge: zero height degenerate
        assert _pick_inpaint_size(1000, 0) == (1024, 1024)

    def test_inpaint_path_returns_canvas_sized_output_with_original_alpha(
        self, tmp_path, monkeypatch
    ):
        """Spec B8 round-trip: 4032×3024 layer → 1536×1024 API → upsampled
        back → preserve_alpha re-applies ORIGINAL canvas alpha (not resized).
        """
        from vulca.layers import redraw as redraw_module
        from vulca.layers.manifest import load_manifest

        # Big canvas with a small sparse region — IMG_6847-class
        canvas = (4032, 3024)

        def factory(size):
            w, h = size
            a = Image.new("L", size, 0)
            # 200×200 spot — well under 5% area
            a.paste(Image.new("L", (200, 200), 255), (1500, 1100))
            return a

        _setup_layer(tmp_path, canvas_size=canvas, alpha_factory=factory)
        artwork = load_manifest(str(tmp_path))

        capable = _CapableProvider()
        import vulca.providers as providers_mod
        monkeypatch.setattr(
            providers_mod, "get_image_provider",
            lambda name, api_key="": capable,
        )

        result = _run(redraw_module.redraw_layer(
            artwork, layer_name="fg", instruction="cartoon",
            provider="capable_stub", artwork_dir=str(tmp_path),
            route="auto", preserve_alpha=True,
        ))

        # Output canvas dim must match ORIGINAL canvas, not the API size.
        out = Image.open(result.image_path)
        assert out.size == canvas, (
            f"expected {canvas} after upsample-back; got {out.size}"
        )
        # Output alpha must match the ORIGINAL canvas alpha bit-for-bit
        # (preserve_alpha re-applies the un-resized canvas alpha).
        out_alpha = np.array(out.convert("RGBA").split()[-1])
        src_alpha = np.array(
            Image.open(str(tmp_path / "fg.png")).convert("RGBA").split()[-1]
        )
        assert np.array_equal(out_alpha, src_alpha), (
            "preserve_alpha must use the ORIGINAL canvas alpha, not a "
            "round-trip-resized version"
        )

        # The provider should have received an upload at API size, not 4032×3024.
        assert len(capable.inpaint_calls) == 1
        with Image.open(io.BytesIO(capable.inpaint_calls[0]["image_bytes"])) as up_img:
            assert up_img.size == (1536, 1024), (
                f"upload should be at API size 1536x1024; got {up_img.size}"
            )


# ---------------------------------------------------------------------------
# 5. redraw_merged unchanged (spec B7 deferral)
# ---------------------------------------------------------------------------

class TestRedrawMergedDeferred:
    def test_redraw_merged_does_not_accept_route_kwarg(self):
        """redraw_merged keeps v0.18 signature in v0.20. Adding ``route``
        to it is v0.21 work (B7 deferral)."""
        import inspect

        from vulca.layers.redraw import redraw_merged

        sig = inspect.signature(redraw_merged)
        assert "route" not in sig.parameters, (
            "redraw_merged should NOT accept `route` in v0.20 — B7 deferred."
        )


# ---------------------------------------------------------------------------
# 6. Degenerate empty-layer guard (spec C7)
# ---------------------------------------------------------------------------

class TestEmptyLayerGuard:
    def test_redraw_layer_raises_on_all_zero_alpha(self, tmp_path):
        """A layer with no opaque pixels raises ValueError before any
        provider call — no point sending a fully-transparent layer to
        gpt-image-2 (mask would be 100% PRESERVE, no edit zone).

        Pins the spec C7 degenerate-case guard. Without this test, a
        regression that silently no-ops on empty layers would slip
        through (legacy v0.18.x silently produced cream output for
        empty layers — a wasted API call that v0.20 short-circuits).
        """
        from vulca.layers import redraw as redraw_module
        from vulca.layers.manifest import load_manifest

        # Stage a layer with all-zero alpha
        def factory(size):
            return Image.new("L", size, 0)

        _setup_layer(tmp_path, canvas_size=(200, 200), alpha_factory=factory)
        artwork = load_manifest(str(tmp_path))

        with pytest.raises(ValueError, match="no visible pixels"):
            _run(redraw_module.redraw_layer(
                artwork, layer_name="fg", instruction="anything",
                provider="mock", artwork_dir=str(tmp_path),
                route="auto",
            ))
