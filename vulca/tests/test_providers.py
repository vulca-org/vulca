"""Tests for provider protocols and built-in implementations."""
import asyncio
import pytest
from vulca.providers.base import ImageProvider, VLMProvider, ImageResult, L1L5Scores


class TestImageResult:
    def test_defaults(self):
        r = ImageResult(image_b64="abc")
        assert r.image_b64 == "abc"
        assert r.mime == "image/png"
        assert r.metadata is None

    def test_custom(self):
        r = ImageResult(image_b64="x", mime="image/svg+xml", metadata={"w": 512})
        assert r.mime == "image/svg+xml"
        assert r.metadata["w"] == 512


class TestL1L5Scores:
    def test_defaults(self):
        s = L1L5Scores(L1=0.8, L2=0.7, L3=0.9, L4=0.75, L5=0.85)
        assert s.L1 == 0.8
        assert s.rationales is None

    def test_with_rationales(self):
        s = L1L5Scores(L1=0.8, L2=0.7, L3=0.9, L4=0.75, L5=0.85,
                       rationales={"L1": "Good composition"})
        assert s.rationales["L1"] == "Good composition"


class TestProtocolCompliance:
    def test_image_provider_protocol(self):
        class Custom:
            async def generate(self, prompt, **kwargs):
                return ImageResult(image_b64="test")
        assert isinstance(Custom(), ImageProvider)

    def test_vlm_provider_protocol(self):
        class Custom:
            async def score(self, image_b64, **kwargs):
                return L1L5Scores(L1=0.5, L2=0.5, L3=0.5, L4=0.5, L5=0.5)
        assert isinstance(Custom(), VLMProvider)


class TestMockImageProvider:
    def test_generates_svg(self):
        from vulca.providers.mock import MockImageProvider
        p = MockImageProvider()
        result = asyncio.run(p.generate("test prompt", tradition="chinese_xieyi"))
        assert result.mime == "image/svg+xml"
        assert len(result.image_b64) > 0
        assert result.metadata is not None
        assert "candidate_id" in result.metadata

    def test_protocol_compliance(self):
        from vulca.providers.mock import MockImageProvider
        assert isinstance(MockImageProvider(), ImageProvider)


class TestMockVLMProvider:
    def test_returns_scores(self):
        from vulca.providers.mock import MockVLMProvider
        p = MockVLMProvider()
        result = asyncio.run(p.score("base64data", tradition="chinese_xieyi"))
        assert 0 < result.L1 <= 1
        assert 0 < result.L5 <= 1
        assert result.rationales is not None
        assert "L1" in result.rationales

    def test_protocol_compliance(self):
        from vulca.providers.mock import MockVLMProvider
        assert isinstance(MockVLMProvider(), VLMProvider)


class TestGeminiImageProvider:
    def test_instantiation(self):
        from vulca.providers.gemini import GeminiImageProvider
        p = GeminiImageProvider(api_key="test-key")
        assert isinstance(p, ImageProvider)

    def test_no_key_raises(self):
        import os
        from vulca.providers.gemini import GeminiImageProvider
        old = os.environ.pop("GOOGLE_API_KEY", None)
        old2 = os.environ.pop("GEMINI_API_KEY", None)
        try:
            p = GeminiImageProvider(api_key="")
            with pytest.raises(ValueError, match="API key"):
                asyncio.run(p.generate("test"))
        finally:
            if old: os.environ["GOOGLE_API_KEY"] = old
            if old2: os.environ["GEMINI_API_KEY"] = old2


class TestOpenAIImageProvider:
    def test_instantiation(self):
        from vulca.providers.openai_provider import OpenAIImageProvider
        p = OpenAIImageProvider(api_key="test-key")
        assert isinstance(p, ImageProvider)


class TestComfyUIImageProvider:
    def test_instantiation(self):
        from vulca.providers.comfyui import ComfyUIImageProvider
        p = ComfyUIImageProvider(base_url="http://localhost:8188")
        assert isinstance(p, ImageProvider)


class TestLiteLLMVLMProvider:
    def test_instantiation(self):
        from vulca.providers.vlm_litellm import LiteLLMVLMProvider
        p = LiteLLMVLMProvider(model="gemini/gemini-2.5-flash")
        assert isinstance(p, VLMProvider)

    def test_parse_response(self):
        from vulca.providers.vlm_litellm import LiteLLMVLMProvider
        p = LiteLLMVLMProvider()
        text = '{"L1": 0.8, "L2": 0.7, "L3": 0.9, "L4": 0.75, "L5": 0.85, "L1_rationale": "Good", "L2_rationale": "OK"}'
        result = p._parse_response(text)
        assert result.L1 == 0.8
        assert result.L3 == 0.9
        assert result.rationales["L1"] == "Good"


class TestProviderRegistry:
    def test_get_mock_image(self):
        from vulca.providers import get_image_provider
        p = get_image_provider("mock")
        assert p is not None

    def test_get_mock_vlm(self):
        from vulca.providers import get_vlm_provider
        p = get_vlm_provider("mock")
        assert p is not None

    def test_unknown_raises(self):
        from vulca.providers import get_image_provider
        with pytest.raises(ValueError, match="Unknown"):
            get_image_provider("nonexistent")

    def test_registry_has_gemini(self):
        from vulca.providers import get_image_provider
        p = get_image_provider("gemini", api_key="test")
        assert p is not None

    def test_nb2_alias(self):
        from vulca.providers import get_image_provider
        p = get_image_provider("nb2", api_key="test")
        assert p is not None


class TestTraditionGuide:
    def test_returns_guide(self):
        from vulca.cultural.loader import get_tradition_guide
        guide = get_tradition_guide("chinese_xieyi")
        assert guide is not None
        assert guide["tradition"] == "chinese_xieyi"
        assert "weights" in guide
        assert "terminology" in guide
        assert "taboos" in guide
        assert isinstance(guide["terminology"], list)
        assert isinstance(guide["taboos"], list)
        assert "emphasis" in guide

    def test_has_weight_keys(self):
        from vulca.cultural.loader import get_tradition_guide
        guide = get_tradition_guide("chinese_xieyi")
        for key in ("L1", "L2", "L3", "L4", "L5"):
            assert key in guide["weights"]

    def test_unknown_tradition(self):
        from vulca.cultural.loader import get_tradition_guide
        guide = get_tradition_guide("nonexistent_tradition")
        assert guide is None

    def test_all_traditions_have_guides(self):
        from vulca.cultural.loader import get_known_traditions, get_tradition_guide
        for name in get_known_traditions():
            guide = get_tradition_guide(name)
            assert guide is not None, f"No guide for {name}"
            assert guide["tradition"] == name
