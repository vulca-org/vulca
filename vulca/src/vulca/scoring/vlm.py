"""VLM Critic -- re-export from top-level _vlm module.

The simple VLM scoring path (Gemini Vision L1-L5) lives in vulca._vlm
for backward compatibility with the SDK evaluate() path.
This module provides the same interface under the scoring namespace.
"""

from vulca._vlm import score_image, _TRADITION_GUIDANCE, _SYSTEM_PROMPT

__all__ = ["score_image", "_TRADITION_GUIDANCE", "_SYSTEM_PROMPT"]
