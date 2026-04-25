"""v0.17.14 — layers_redraw recontract tests.

Patch 2 contract: opt-in non-destructive output, configurable background
strategy (cream/white/sample_median/transparent), preserve_alpha,
provider-aware api_key wiring, aspect-preserving fit (no LANCZOS warp on
non-square canvases).
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from PIL import Image

from vulca.layers.manifest import write_manifest, load_manifest
from vulca.layers.types import LayerInfo


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _setup_one_layer(tmp_path: Path, *, size=(100, 100), color=(180, 64, 32, 200)) -> Path:
    Image.new("RGBA", size, color).save(str(tmp_path / "fg.png"))
    Image.new("RGB", size, (100, 100, 100)).save(str(tmp_path / "source.png"))

    fg = LayerInfo(
        name="fg", description="foreground", z_index=1, content_type="subject"
    )
    write_manifest(
        [fg],
        output_dir=str(tmp_path),
        width=size[0],
        height=size[1],
        source_image="source.png",
    )
    return tmp_path


# ---------------------------------------------------------------------------
# Non-destructive output
# ---------------------------------------------------------------------------

class TestNonDestructiveOutput:
    def test_default_inplace_for_backcompat(self, tmp_path):
        """Default (no output_layer_name) writes back to <layer>.png."""
        from vulca.layers.redraw import redraw_layer

        _setup_one_layer(tmp_path)
        artwork = load_manifest(str(tmp_path))
        before_other_files = set(p.name for p in tmp_path.iterdir())

        _run(
            redraw_layer(
                artwork, layer_name="fg", instruction="brighter",
                provider="mock", artwork_dir=str(tmp_path),
            )
        )
        after = set(p.name for p in tmp_path.iterdir())
        # No new layer file created
        assert after == before_other_files
        # fg.png still exists (in-place rewrite)
        assert (tmp_path / "fg.png").exists()

    def test_custom_output_name_creates_new_file(self, tmp_path):
        """output_layer_name='foo' writes foo.png and leaves fg.png alone."""
        from vulca.layers.redraw import redraw_layer

        _setup_one_layer(tmp_path)
        before_fg_bytes = (tmp_path / "fg.png").read_bytes()
        artwork = load_manifest(str(tmp_path))

        result = _run(
            redraw_layer(
                artwork, layer_name="fg", instruction="brighter",
                provider="mock", artwork_dir=str(tmp_path),
                output_layer_name="fg_redrawn",
            )
        )
        # New file present
        assert (tmp_path / "fg_redrawn.png").exists()
        # Old file untouched
        assert (tmp_path / "fg.png").read_bytes() == before_fg_bytes
        # Returned LayerResult points at new file
        assert result.info.name == "fg_redrawn"
        assert result.image_path == str(tmp_path / "fg_redrawn.png")

    def test_custom_output_appends_manifest_entry(self, tmp_path):
        """Manifest gets a new layer entry for output_layer_name."""
        from vulca.layers.redraw import redraw_layer

        _setup_one_layer(tmp_path)
        artwork = load_manifest(str(tmp_path))

        _run(
            redraw_layer(
                artwork, layer_name="fg", instruction="brighter",
                provider="mock", artwork_dir=str(tmp_path),
                output_layer_name="fg_redrawn",
            )
        )
        new_artwork = load_manifest(str(tmp_path))
        names = {lr.info.name for lr in new_artwork.layers}
        assert "fg" in names
        assert "fg_redrawn" in names


# ---------------------------------------------------------------------------
# Background strategy
# ---------------------------------------------------------------------------

class TestBackgroundStrategy:
    def test_cream_bg_no_hallucination_marker(self, tmp_path):
        """Cream BG strategy adds canvas-guard prompt line.

        We can't observe pixel hallucination with a mock provider, so we
        verify the prompt-construction path injects the canvas-guard.
        """
        from vulca.layers.redraw import _build_redraw_prompt

        prompt = _build_redraw_prompt(
            "redraw lanterns",
            ["cinnabar paper lanterns"],
            background_strategy="cream",
        )
        assert "do NOT introduce new objects" in prompt

    def test_transparent_bg_omits_canvas_guard(self):
        """Legacy transparent strategy keeps the legacy prompt unchanged."""
        from vulca.layers.redraw import _build_redraw_prompt

        prompt = _build_redraw_prompt(
            "redraw lanterns",
            ["cinnabar paper lanterns"],
            background_strategy="transparent",
        )
        assert "do NOT introduce new objects" not in prompt

    def test_unknown_background_strategy_raises(self, tmp_path):
        """Unrecognized background strategy fails loud."""
        from vulca.layers.redraw import redraw_layer

        _setup_one_layer(tmp_path)
        artwork = load_manifest(str(tmp_path))

        with pytest.raises(ValueError, match="background_strategy"):
            _run(
                redraw_layer(
                    artwork, layer_name="fg", instruction="x",
                    provider="mock", artwork_dir=str(tmp_path),
                    background_strategy="rainbow",
                )
            )

    def test_sample_median_picks_visible_pixel(self, tmp_path):
        """sample_median bg samples from non-transparent layer pixels."""
        from vulca.layers.redraw import _sample_median_bg

        # Layer with two opaque colors and transparent corners
        img = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
        for y in range(2, 8):
            for x in range(2, 8):
                img.putpixel((x, y), (200, 100, 50, 255))
        bg = _sample_median_bg(img)
        assert bg == (200, 100, 50)

    def test_sample_median_falls_back_when_all_transparent(self):
        """sample_median on fully-transparent layer falls back to cream."""
        from vulca.layers.redraw import _sample_median_bg, CREAM_BG_RGB

        img = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
        bg = _sample_median_bg(img)
        assert bg == CREAM_BG_RGB


# ---------------------------------------------------------------------------
# preserve_alpha
# ---------------------------------------------------------------------------

class TestPreserveAlpha:
    def test_preserve_alpha_true_matches_source_alpha(self, tmp_path):
        """preserve_alpha=True → output alpha matches source alpha."""
        from vulca.layers.redraw import redraw_layer

        _setup_one_layer(tmp_path, color=(180, 64, 32, 100))
        src_alpha = Image.open(str(tmp_path / "fg.png")).split()[-1]
        artwork = load_manifest(str(tmp_path))

        _run(
            redraw_layer(
                artwork, layer_name="fg", instruction="x",
                provider="mock", artwork_dir=str(tmp_path),
                preserve_alpha=True,
            )
        )
        out_alpha = Image.open(str(tmp_path / "fg.png")).split()[-1]
        # Compare alpha channels
        assert list(out_alpha.getdata()) == list(src_alpha.getdata())

    def test_preserve_alpha_false_default_unchanged(self, tmp_path):
        """preserve_alpha=False (default) — output is opaque RGBA."""
        from vulca.layers.redraw import redraw_layer

        _setup_one_layer(tmp_path)
        artwork = load_manifest(str(tmp_path))

        _run(
            redraw_layer(
                artwork, layer_name="fg", instruction="x",
                provider="mock", artwork_dir=str(tmp_path),
                preserve_alpha=False,
            )
        )
        # Mock provider returns opaque (alpha=255 across canvas)
        out = Image.open(str(tmp_path / "fg.png"))
        alphas = set(out.split()[-1].getdata())
        # Allow some room — mock canvas is single solid color → all alphas equal
        assert max(alphas) == 255


# ---------------------------------------------------------------------------
# Provider-aware api_key wiring
# ---------------------------------------------------------------------------

class TestProviderApiKeyWiring:
    def test_openai_does_not_receive_google_api_key(
        self, tmp_path, monkeypatch
    ):
        """Bug fix: OPENAI provider must self-resolve OPENAI_API_KEY,
        not be force-fed GOOGLE_API_KEY by the redraw helper."""
        captured: dict = {}

        # Stub get_image_provider on its source module — redraw.py
        # imports it lazily, so we patch the canonical home.
        from vulca.providers.mock import MockImageProvider
        import vulca.providers as providers_mod

        def stub_get_image_provider(name, **kwargs):
            captured["name"] = name
            captured["api_key"] = kwargs.get("api_key", "")
            return MockImageProvider(**kwargs)

        monkeypatch.setattr(
            providers_mod, "get_image_provider", stub_get_image_provider,
        )
        monkeypatch.setenv("GOOGLE_API_KEY", "google-secret-do-not-leak")
        monkeypatch.setenv("OPENAI_API_KEY", "openai-key")

        _setup_one_layer(tmp_path)
        from vulca.layers.redraw import redraw_layer
        artwork = load_manifest(str(tmp_path))
        _run(
            redraw_layer(
                artwork, layer_name="fg", instruction="x",
                provider="openai", artwork_dir=str(tmp_path),
            )
        )
        assert captured["name"] == "openai"
        # The redraw helper no longer pre-resolves GOOGLE_API_KEY for
        # non-gemini providers — let the provider self-resolve.
        assert "google" not in captured["api_key"].lower()


# ---------------------------------------------------------------------------
# Aspect preservation
# ---------------------------------------------------------------------------

class TestAspectPreservation:
    def test_fit_preserves_aspect_letterbox(self):
        """1024x1536 source target → 1024x1024 provider output centered."""
        from vulca.layers.redraw import _fit_into_canvas

        src = Image.new("RGB", (1024, 1024), (200, 100, 50))
        out = _fit_into_canvas(src, (1024, 1536), bg_rgb=(252, 248, 240))
        assert out.size == (1024, 1536)
        # Top center should be cream (letterbox), middle should be subject
        top = out.getpixel((512, 10))
        middle = out.getpixel((512, 768))
        assert top[:3] == (252, 248, 240), f"expected cream top, got {top}"
        assert middle[:3] == (200, 100, 50), f"expected subject middle, got {middle}"

    def test_fit_no_resize_when_match(self):
        """Identity case: source size matches target — return as-is."""
        from vulca.layers.redraw import _fit_into_canvas

        src = Image.new("RGB", (100, 100), (50, 50, 50))
        out = _fit_into_canvas(src, (100, 100), bg_rgb=(0, 0, 0))
        assert out.size == (100, 100)
