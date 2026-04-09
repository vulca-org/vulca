"""v0.13.2 P2: providers expose capabilities frozenset."""
from __future__ import annotations

from vulca.providers.gemini import GeminiImageProvider
from vulca.providers.mock import MockImageProvider
from vulca.providers.openai_provider import OpenAIImageProvider
from vulca.providers.comfyui import ComfyUIImageProvider


def test_mock_has_no_raw_rgba():
    assert "raw_rgba" not in getattr(MockImageProvider, "capabilities", frozenset())


def test_gemini_declares_raw_rgba():
    assert "raw_rgba" in GeminiImageProvider.capabilities


def test_openai_declares_raw_rgba():
    assert "raw_rgba" in OpenAIImageProvider.capabilities


def test_comfyui_declares_raw_rgba():
    assert "raw_rgba" in ComfyUIImageProvider.capabilities


def test_capabilities_are_frozensets():
    for cls in (MockImageProvider, GeminiImageProvider, OpenAIImageProvider, ComfyUIImageProvider):
        assert isinstance(cls.capabilities, frozenset), cls


def test_protocol_capabilities_has_default():
    """ImageProvider.capabilities should have a default frozenset()
    so providers that omit it still satisfy the Protocol."""
    from vulca.providers.base import ImageProvider
    assert hasattr(ImageProvider, "capabilities")
    assert ImageProvider.capabilities == frozenset()
