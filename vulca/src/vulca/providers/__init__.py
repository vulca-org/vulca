"""Pluggable provider interfaces for image generation and VLM scoring."""
from vulca.providers.base import ImageProvider, ImageResult, L1L5Scores, VLMProvider

__all__ = ["ImageProvider", "VLMProvider", "ImageResult", "L1L5Scores"]
