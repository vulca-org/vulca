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
