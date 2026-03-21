"""Pluggable provider interfaces for image generation and VLM scoring."""
from vulca.providers.base import ImageProvider, ImageResult, L1L5Scores, VLMProvider

_IMAGE_PROVIDERS: dict[str, type] = {}
_VLM_PROVIDERS: dict[str, type] = {}


def _lazy_load_providers():
    global _IMAGE_PROVIDERS, _VLM_PROVIDERS
    if _IMAGE_PROVIDERS:
        return
    from vulca.providers.mock import MockImageProvider, MockVLMProvider
    _IMAGE_PROVIDERS["mock"] = MockImageProvider
    _VLM_PROVIDERS["mock"] = MockVLMProvider
    try:
        from vulca.providers.gemini import GeminiImageProvider
        _IMAGE_PROVIDERS["gemini"] = GeminiImageProvider
        _IMAGE_PROVIDERS["nb2"] = GeminiImageProvider  # alias
    except ImportError:
        pass
    try:
        from vulca.providers.openai_provider import OpenAIImageProvider
        _IMAGE_PROVIDERS["openai"] = OpenAIImageProvider
    except ImportError:
        pass
    try:
        from vulca.providers.comfyui import ComfyUIImageProvider
        _IMAGE_PROVIDERS["comfyui"] = ComfyUIImageProvider
    except ImportError:
        pass
    try:
        from vulca.providers.vlm_litellm import LiteLLMVLMProvider
        _VLM_PROVIDERS["litellm"] = LiteLLMVLMProvider
    except ImportError:
        pass


def get_image_provider(name: str, **kwargs) -> ImageProvider:
    """Get an image provider by name."""
    _lazy_load_providers()
    cls = _IMAGE_PROVIDERS.get(name)
    if cls is None:
        raise ValueError(f"Unknown image provider: {name!r}. Available: {list(_IMAGE_PROVIDERS.keys())}")
    return cls(**kwargs)


def get_vlm_provider(name: str, **kwargs) -> VLMProvider:
    """Get a VLM provider by name."""
    _lazy_load_providers()
    cls = _VLM_PROVIDERS.get(name)
    if cls is None:
        raise ValueError(f"Unknown VLM provider: {name!r}. Available: {list(_VLM_PROVIDERS.keys())}")
    return cls(**kwargs)


__all__ = [
    "ImageProvider", "VLMProvider", "ImageResult", "L1L5Scores",
    "get_image_provider", "get_vlm_provider",
]
