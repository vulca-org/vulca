"""Tests for NB2Provider (Nano Banana 2 / gemini-3.1-flash-image-preview).

Covers:
- Initialization & graceful degradation (no API key)
- generate() with mocked google.genai.Client
- Thinking budget config validation
- Multi-image output parsing (last image wins)
- model_router routing validation
- build_full_evidence_prompt utility
"""
from __future__ import annotations

import io
import struct
import zlib
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_solid_png_bytes(w: int = 4, h: int = 4) -> bytes:
    """Create minimal valid PNG bytes for testing."""
    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        length = struct.pack(">I", len(data))
        crc = struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
        return length + chunk_type + data + crc

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    ihdr = _chunk(b"IHDR", ihdr_data)
    row = bytes([0]) + bytes([128, 64, 32]) * w
    raw = row * h
    compressed = zlib.compress(raw)
    idat = _chunk(b"IDAT", compressed)
    iend = _chunk(b"IEND", b"")
    return signature + ihdr + idat + iend


@dataclass
class _FakeAnchor:
    term: str = "sumi"
    definition: str = "Traditional ink wash"
    usage_hint: str = "Use for calligraphic strokes"
    l_levels: list[str] = field(default_factory=lambda: ["L3", "L4"])


@dataclass
class _FakeComposition:
    description: str = "Asymmetric balance"
    spatial_strategy: str = "rule_of_thirds"
    example_prompt_fragment: str = "off-center focal point"


@dataclass
class _FakeStyle:
    attribute: str = "brushwork"
    value: str = "wet-on-wet"
    tradition_source: str = "chinese_xieyi"


@dataclass
class _FakeTaboo:
    description: str = "Do not use red for mourning"
    severity: str = "critical"
    tradition_source: str = "chinese_xieyi"


@dataclass
class _FakeEvidencePack:
    anchors: list = field(default_factory=lambda: [_FakeAnchor()])
    compositions: list = field(default_factory=lambda: [_FakeComposition()])
    styles: list = field(default_factory=lambda: [_FakeStyle()])
    taboos: list = field(default_factory=lambda: [_FakeTaboo()])
    coverage: float = 0.75


# ---------------------------------------------------------------------------
# 1. Initialization tests
# ---------------------------------------------------------------------------

class TestNB2ProviderInit:
    """NB2Provider initialization and graceful degradation."""

    def test_init_with_explicit_api_key(self) -> None:
        from app.prototype.agents.nb2_provider import NB2Provider

        provider = NB2Provider(api_key="test-key-123")
        assert provider._api_key == "test-key-123"
        assert provider._thinking_level == "High"
        assert provider._timeout == 120
        assert provider._client is None
        assert provider._call_log == []

    def test_init_from_env_var(self) -> None:
        from app.prototype.agents.nb2_provider import NB2Provider

        with patch.dict("os.environ", {"GOOGLE_API_KEY": "env-key-456"}):
            provider = NB2Provider()
            assert provider._api_key == "env-key-456"

    def test_init_raises_without_api_key(self) -> None:
        """Graceful degradation: raises ValueError when no key available."""
        from app.prototype.agents.nb2_provider import NB2Provider

        with patch.dict("os.environ", {}, clear=True):
            # Also clear GOOGLE_API_KEY specifically
            import os
            env = {k: v for k, v in os.environ.items() if k != "GOOGLE_API_KEY"}
            with patch.dict("os.environ", env, clear=True):
                with pytest.raises(ValueError, match="GOOGLE_API_KEY not set"):
                    NB2Provider()

    def test_model_ref(self) -> None:
        from app.prototype.agents.nb2_provider import NB2Provider

        provider = NB2Provider(api_key="k")
        assert provider.model_ref == "nb2:gemini-3.1-flash-image-preview"

    def test_custom_thinking_level_and_timeout(self) -> None:
        from app.prototype.agents.nb2_provider import NB2Provider

        provider = NB2Provider(api_key="k", thinking_level="minimal", timeout=60)
        assert provider._thinking_level == "minimal"
        assert provider._timeout == 60


# ---------------------------------------------------------------------------
# 2. generate() with mocked google.genai.Client
# ---------------------------------------------------------------------------

class TestNB2Generate:
    """Test generate() by mocking the google.genai SDK."""

    def _build_mock_response(
        self,
        image_bytes: bytes,
        text: str = "thinking about the artwork...",
        num_images: int = 1,
    ) -> MagicMock:
        """Build a fake genai response with text + image parts."""
        parts = []

        # Text part
        text_part = MagicMock()
        text_part.text = text
        parts.append(text_part)

        # Image parts (last one should be the "final" image)
        for i in range(num_images):
            img_part = MagicMock()
            img_part.text = None  # Not a text part

            # Mock as_image() to return a PIL-like Image
            pil_img = MagicMock()
            buf = io.BytesIO()
            buf.write(image_bytes)
            buf.seek(0)

            def _save(buf_out, format="PNG", _data=image_bytes):
                buf_out.write(_data)

            pil_img.save = _save
            img_part.as_image.return_value = pil_img
            parts.append(img_part)

        content = MagicMock()
        content.parts = parts

        candidate = MagicMock()
        candidate.content = content

        response = MagicMock()
        response.candidates = [candidate]

        return response

    @patch("app.prototype.agents.nb2_provider.genai", create=True)
    @patch("app.prototype.agents.nb2_provider.types", create=True)
    def test_generate_success(self, mock_types, mock_genai, tmp_path) -> None:
        """generate() calls API, saves PNG, returns path."""
        from app.prototype.agents.nb2_provider import NB2Provider

        png_bytes = _make_solid_png_bytes()
        mock_response = self._build_mock_response(png_bytes)

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response

        # Patch the lazy import inside _call_api
        fake_genai_module = MagicMock()
        fake_genai_module.Client.return_value = mock_client

        fake_types_module = MagicMock()
        fake_types_module.GenerateContentConfig.return_value = MagicMock()
        fake_types_module.ThinkingConfig.return_value = MagicMock()

        provider = NB2Provider(api_key="test-key")

        output_path = str(tmp_path / "output.png")

        with patch.dict(
            "sys.modules",
            {
                "google": MagicMock(),
                "google.genai": fake_genai_module,
                "google.genai.types": fake_types_module,
            },
        ):
            # Inject the mock client directly
            provider._client = mock_client

            # We need to mock the imports inside _call_api
            with patch(
                "app.prototype.agents.nb2_provider.NB2Provider._call_api",
                return_value=(png_bytes, "thinking text"),
            ):
                result = provider.generate(
                    prompt="bamboo in mist",
                    negative_prompt="photorealistic",
                    seed=42,
                    width=1024,
                    height=1024,
                    steps=20,
                    sampler="euler_a",
                    output_path=output_path,
                )

        assert result.endswith(".png")
        # Verify file was written
        from pathlib import Path
        assert Path(result).exists()
        assert Path(result).read_bytes() == png_bytes

    def test_generate_logs_call(self, tmp_path) -> None:
        """generate() appends to call_log on success."""
        from app.prototype.agents.nb2_provider import NB2Provider

        png_bytes = _make_solid_png_bytes()
        provider = NB2Provider(api_key="test-key")
        output_path = str(tmp_path / "out.png")

        with patch.object(
            provider,
            "_call_api",
            return_value=(png_bytes, "thinking about colors"),
        ):
            provider.generate(
                prompt="test", negative_prompt="", seed=1,
                width=512, height=512, steps=10, sampler="",
                output_path=output_path,
            )

        assert len(provider.call_log) == 1
        log_entry = provider.call_log[0]
        assert log_entry["model"] == "gemini-3.1-flash-image-preview"
        assert log_entry["error"] is None
        assert log_entry["latency_ms"] >= 0
        assert log_entry["thinking_chars"] == len("thinking about colors")

    def test_generate_api_error_raises_oserror(self, tmp_path) -> None:
        """API errors are re-raised as OSError for FallbackProvider."""
        from app.prototype.agents.nb2_provider import NB2Provider

        provider = NB2Provider(api_key="test-key")
        output_path = str(tmp_path / "out.png")

        with patch.object(
            provider, "_call_api",
            side_effect=RuntimeError("API returned 500"),
        ):
            with pytest.raises(OSError, match="NB2 API error"):
                provider.generate(
                    prompt="test", negative_prompt="", seed=1,
                    width=512, height=512, steps=10, sampler="",
                    output_path=output_path,
                )

    def test_generate_timeout_raises_timeout_error(self, tmp_path) -> None:
        """Timeout errors are properly classified."""
        from app.prototype.agents.nb2_provider import NB2Provider

        provider = NB2Provider(api_key="test-key")
        output_path = str(tmp_path / "out.png")

        with patch.object(
            provider, "_call_api",
            side_effect=RuntimeError("request timeout exceeded"),
        ):
            with pytest.raises(TimeoutError, match="NB2 timeout"):
                provider.generate(
                    prompt="test", negative_prompt="", seed=1,
                    width=512, height=512, steps=10, sampler="",
                    output_path=output_path,
                )

    def test_generate_connection_error(self, tmp_path) -> None:
        """Connection errors are properly classified."""
        from app.prototype.agents.nb2_provider import NB2Provider

        provider = NB2Provider(api_key="test-key")
        output_path = str(tmp_path / "out.png")

        with patch.object(
            provider, "_call_api",
            side_effect=RuntimeError("connection refused"),
        ):
            with pytest.raises(ConnectionError, match="NB2 connection"):
                provider.generate(
                    prompt="test", negative_prompt="", seed=1,
                    width=512, height=512, steps=10, sampler="",
                    output_path=output_path,
                )


# ---------------------------------------------------------------------------
# 3. Thinking budget config validation
# ---------------------------------------------------------------------------

class TestThinkingBudget:
    """Validate thinking budget defaults and config generation."""

    def test_default_thinking_budget_is_1024(self) -> None:
        """The _call_api method sets thinking_budget=1024 by default.

        We verify by inspecting the source code of _call_api, since mocking
        the lazy `from google import genai` inside the method is fragile
        due to Python's import caching.
        """
        import inspect
        from app.prototype.agents.nb2_provider import NB2Provider

        source = inspect.getsource(NB2Provider._call_api)
        # Verify the thinking_budget constant is 1024
        assert "thinking_budget=1024" in source
        assert "include_thoughts=True" in source

    def test_thinking_config_in_generate_content_config(self) -> None:
        """Verify that GenerateContentConfig includes thinking_config and IMAGE modality."""
        import inspect
        from app.prototype.agents.nb2_provider import NB2Provider

        source = inspect.getsource(NB2Provider._call_api)
        assert "response_modalities=" in source
        assert '"IMAGE"' in source
        assert "ThinkingConfig" in source


# ---------------------------------------------------------------------------
# 4. Multi-image output parsing
# ---------------------------------------------------------------------------

class TestMultiImageParsing:
    """Verify that multi-image responses keep the LAST image (final result)."""

    def test_last_image_wins(self) -> None:
        """When response has multiple image parts, the last one is returned."""
        from app.prototype.agents.nb2_provider import NB2Provider

        provider = NB2Provider(api_key="test-key")

        # Create two different "images" (different byte content)
        img1_bytes = b"FIRST_IMAGE_DATA"
        img2_bytes = _make_solid_png_bytes()  # The "final" image

        # Build parts: text, img1 (intermediate), img2 (final)
        text_part = MagicMock()
        text_part.text = "Reviewing composition..."

        img_part_1 = MagicMock()
        img_part_1.text = None
        # as_image returns a PIL image that saves img1_bytes
        pil1 = MagicMock()
        pil1.save = lambda buf, format="PNG": buf.write(img1_bytes)
        img_part_1.as_image.return_value = pil1

        img_part_2 = MagicMock()
        img_part_2.text = None
        pil2 = MagicMock()
        pil2.save = lambda buf, format="PNG": buf.write(img2_bytes)
        img_part_2.as_image.return_value = pil2

        content = MagicMock()
        content.parts = [text_part, img_part_1, img_part_2]
        candidate = MagicMock()
        candidate.content = content
        response = MagicMock()
        response.candidates = [candidate]

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = response

        fake_genai = MagicMock()
        fake_genai.Client.return_value = mock_client
        fake_types = MagicMock()
        fake_types.GenerateContentConfig.return_value = MagicMock()
        fake_types.ThinkingConfig.return_value = MagicMock()

        import sys
        with patch.dict(sys.modules, {
            "google": MagicMock(),
            "google.genai": fake_genai,
            "google.genai.types": fake_types,
        }):
            provider._client = mock_client
            img_bytes, thinking = provider._call_api("test", "1K", "1:1")

        # Last image should win
        assert img_bytes == img2_bytes
        assert "Reviewing" in thinking

    def test_inline_data_fallback(self) -> None:
        """When as_image() fails, fall back to inline_data.data."""
        from app.prototype.agents.nb2_provider import NB2Provider

        provider = NB2Provider(api_key="test-key")

        raw_bytes = _make_solid_png_bytes()

        text_part = MagicMock()
        text_part.text = "thought"

        img_part = MagicMock()
        img_part.text = None
        img_part.as_image.return_value = None  # as_image returns None
        img_part.inline_data = MagicMock()
        img_part.inline_data.data = raw_bytes

        content = MagicMock()
        content.parts = [text_part, img_part]
        candidate = MagicMock()
        candidate.content = content
        response = MagicMock()
        response.candidates = [candidate]

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = response

        fake_genai = MagicMock()
        fake_genai.Client.return_value = mock_client
        fake_types = MagicMock()
        fake_types.GenerateContentConfig.return_value = MagicMock()
        fake_types.ThinkingConfig.return_value = MagicMock()

        import sys
        with patch.dict(sys.modules, {
            "google": MagicMock(),
            "google.genai": fake_genai,
            "google.genai.types": fake_types,
        }):
            provider._client = mock_client
            img_bytes, thinking = provider._call_api("test", "1K", "1:1")

        assert img_bytes == raw_bytes

    def test_no_image_raises_oserror(self) -> None:
        """Response with no image parts raises OSError."""
        from app.prototype.agents.nb2_provider import NB2Provider

        provider = NB2Provider(api_key="test-key")

        text_part = MagicMock()
        text_part.text = "I can't generate an image right now"

        content = MagicMock()
        content.parts = [text_part]
        candidate = MagicMock()
        candidate.content = content
        response = MagicMock()
        response.candidates = [candidate]

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = response

        fake_genai = MagicMock()
        fake_genai.Client.return_value = mock_client
        fake_types = MagicMock()
        fake_types.GenerateContentConfig.return_value = MagicMock()
        fake_types.ThinkingConfig.return_value = MagicMock()

        import sys
        with patch.dict(sys.modules, {
            "google": MagicMock(),
            "google.genai": fake_genai,
            "google.genai.types": fake_types,
        }):
            provider._client = mock_client
            with pytest.raises(OSError, match="no image"):
                provider._call_api("test", "1K", "1:1")


# ---------------------------------------------------------------------------
# 5. model_router routing validation
# ---------------------------------------------------------------------------

class TestModelRouter:
    """Validate ModelRouter selects correct model per layer/tradition."""

    def test_default_layer_models_all_gemini(self) -> None:
        """All 5 layers default to gemini_direct."""
        from app.prototype.agents.model_router import DEFAULT_LAYER_MODELS

        expected_layers = {
            "visual_perception",
            "technical_analysis",
            "cultural_context",
            "critical_interpretation",
            "philosophical_aesthetic",
        }
        assert set(DEFAULT_LAYER_MODELS.keys()) == expected_layers
        for layer, model_key in DEFAULT_LAYER_MODELS.items():
            assert model_key == "gemini_direct", (
                f"Layer '{layer}' mapped to '{model_key}', expected 'gemini_direct'"
            )

    def test_select_model_returns_spec(self) -> None:
        """select_model returns a valid ModelSpec for known layers."""
        from app.prototype.agents.model_router import ModelRouter

        router = ModelRouter()
        spec = router.select_model("visual_perception", requires_vlm=True)
        assert spec is not None
        assert "gemini" in spec.litellm_id.lower()
        assert spec.supports_vlm is True

    def test_select_model_budget_exhausted(self) -> None:
        """Returns None when budget is exhausted."""
        from app.prototype.agents.model_router import ModelRouter

        router = ModelRouter(budget_remaining_usd=0.0)
        spec = router.select_model("visual_perception")
        assert spec is None

    def test_record_cost_deducts(self) -> None:
        """record_cost reduces budget_remaining_usd."""
        from app.prototype.agents.model_router import ModelRouter

        router = ModelRouter(budget_remaining_usd=1.0)
        router.record_cost(0.3)
        assert abs(router.budget_remaining_usd - 0.7) < 1e-6

    def test_record_cost_floors_at_zero(self) -> None:
        """Budget cannot go negative."""
        from app.prototype.agents.model_router import ModelRouter

        router = ModelRouter(budget_remaining_usd=0.1)
        router.record_cost(999.0)
        assert router.budget_remaining_usd == 0.0

    def test_to_dict(self) -> None:
        """to_dict returns serializable representation."""
        from app.prototype.agents.model_router import ModelRouter

        router = ModelRouter()
        d = router.to_dict()
        assert "layer_models" in d
        assert "budget_remaining_usd" in d
        assert isinstance(d["budget_remaining_usd"], float)

    def test_fallback_chain_is_empty_for_gemini(self) -> None:
        """Single-vendor setup has empty fallback chains."""
        from app.prototype.agents.model_router import FALLBACK_CHAINS

        assert FALLBACK_CHAINS.get("gemini_direct") == []


# ---------------------------------------------------------------------------
# 6. _resolve_image_size and _build_nb2_prompt
# ---------------------------------------------------------------------------

class TestImageSizeResolution:
    """Test the _resolve_image_size helper."""

    def test_square_1024(self) -> None:
        from app.prototype.agents.nb2_provider import _resolve_image_size

        size, aspect = _resolve_image_size(1024, 1024)
        assert size == "1K"
        assert aspect == "1:1"

    def test_small_512(self) -> None:
        from app.prototype.agents.nb2_provider import _resolve_image_size

        size, aspect = _resolve_image_size(512, 512)
        assert size == "0.5K"
        assert aspect == "1:1"

    def test_landscape_16_9(self) -> None:
        from app.prototype.agents.nb2_provider import _resolve_image_size

        size, aspect = _resolve_image_size(1920, 1080)
        assert aspect == "16:9"
        assert size == "2K"

    def test_portrait_9_16(self) -> None:
        from app.prototype.agents.nb2_provider import _resolve_image_size

        size, aspect = _resolve_image_size(1080, 1920)
        assert aspect == "9:16"
        assert size == "2K"

    def test_4_3_aspect(self) -> None:
        from app.prototype.agents.nb2_provider import _resolve_image_size

        size, aspect = _resolve_image_size(1024, 768)
        assert aspect == "4:3"

    def test_3_4_aspect(self) -> None:
        from app.prototype.agents.nb2_provider import _resolve_image_size

        size, aspect = _resolve_image_size(768, 1024)
        assert aspect == "3:4"

    def test_very_large_maps_to_4k(self) -> None:
        from app.prototype.agents.nb2_provider import _resolve_image_size

        size, aspect = _resolve_image_size(3840, 3840)
        assert size == "4K"


class TestBuildNB2Prompt:
    """Test _build_nb2_prompt negative prompt merging."""

    def test_no_negative(self) -> None:
        from app.prototype.agents.nb2_provider import _build_nb2_prompt

        result = _build_nb2_prompt("bamboo painting", "")
        assert result == "bamboo painting"

    def test_with_negative(self) -> None:
        from app.prototype.agents.nb2_provider import _build_nb2_prompt

        result = _build_nb2_prompt("bamboo painting", "photorealistic, 3D render")
        assert "AVOID" in result
        assert "photorealistic" in result
        assert "bamboo painting" in result


# ---------------------------------------------------------------------------
# 7. build_full_evidence_prompt
# ---------------------------------------------------------------------------

class TestBuildFullEvidencePrompt:
    """Test the full evidence prompt builder for NB2's 32K context."""

    def test_basic_output(self) -> None:
        from app.prototype.agents.nb2_provider import build_full_evidence_prompt

        pack = _FakeEvidencePack()
        positive, negative = build_full_evidence_prompt(
            subject="bamboo in mist",
            tradition="chinese_xieyi",
            evidence_pack=pack,
        )

        assert "bamboo in mist" in positive
        assert "chinese xieyi" in positive
        assert "STYLE REQUIREMENTS" in positive
        assert "brushwork" in positive
        assert "CULTURAL TERMS" in positive
        assert "sumi" in positive
        assert "COMPOSITION GUIDANCE" in positive
        assert "CRITICAL TABOOS" in positive
        assert "Do not use red for mourning" in negative

    def test_empty_evidence_pack(self) -> None:
        from app.prototype.agents.nb2_provider import build_full_evidence_prompt

        @dataclass
        class EmptyPack:
            anchors: list = field(default_factory=list)
            compositions: list = field(default_factory=list)
            styles: list = field(default_factory=list)
            taboos: list = field(default_factory=list)
            coverage: float = 0.0

        positive, negative = build_full_evidence_prompt(
            subject="lotus", tradition="default", evidence_pack=EmptyPack(),
        )
        assert "lotus" in positive
        assert negative == ""
        # Low coverage note should appear
        assert "coverage is low" in positive

    def test_malformed_evidence_pack_graceful(self) -> None:
        """Malformed evidence pack returns minimal prompt, not crash."""
        from app.prototype.agents.nb2_provider import build_full_evidence_prompt

        positive, negative = build_full_evidence_prompt(
            subject="test", tradition="western_academic", evidence_pack=None,
        )
        assert "test" in positive
        assert "western academic" in positive

    def test_coverage_display(self) -> None:
        from app.prototype.agents.nb2_provider import build_full_evidence_prompt

        pack = _FakeEvidencePack(coverage=0.85)
        positive, _ = build_full_evidence_prompt(
            subject="crane", tradition="japanese_traditional", evidence_pack=pack,
        )
        assert "85%" in positive

    def test_non_critical_taboos(self) -> None:
        """Non-critical taboos appear in AVOID section, not CRITICAL."""
        from app.prototype.agents.nb2_provider import build_full_evidence_prompt

        @dataclass
        class MixedTabooPack:
            anchors: list = field(default_factory=list)
            compositions: list = field(default_factory=list)
            styles: list = field(default_factory=list)
            taboos: list = field(default_factory=lambda: [
                _FakeTaboo(description="No gold leaf", severity="medium"),
                _FakeTaboo(description="No religious symbols", severity="critical"),
            ])
            coverage: float = 0.5

        positive, negative = build_full_evidence_prompt(
            subject="abstract", tradition="islamic_geometric",
            evidence_pack=MixedTabooPack(),
        )
        assert "CRITICAL TABOOS" in positive
        assert "No religious symbols" in positive
        assert "AVOID in this tradition" in positive
        assert "No gold leaf" in positive
        assert "No gold leaf" in negative
        assert "No religious symbols" in negative
