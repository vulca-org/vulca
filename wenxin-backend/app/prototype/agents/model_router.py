"""Model Router — selects the optimal LLM for each layer and task.

Routes requests through LiteLLM for unified API access. Supports:
- Per-layer model assignment (L1/L2 VLM, L3-L5 text LLM)
- Budget-aware fallback chains
- Confidence-based escalation

All API models route through globalai.vip proxy (OpenAI-compatible).
Set GLOBALAI_API_KEY env var or fall back to DEEPSEEK_API_KEY.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "DEFAULT_LAYER_MODELS",
    "FALLBACK_CHAINS",
    "MODELS",
    "ModelRouter",
    "ModelSpec",
]

# globalai.vip proxy — unified API gateway
_GLOBALAI_BASE = "https://globalai.vip/v1"


def _globalai_key() -> str:
    """Get the globalai.vip API key from environment or settings."""
    from app.core.config import settings as _settings
    return (
        os.environ.get("GLOBALAI_API_KEY")
        or os.environ.get("DEEPSEEK_API_KEY")
        or _settings.GLOBALAI_API_KEY
        or ""
    )


# ---------------------------------------------------------------------------
# Model definitions
# ---------------------------------------------------------------------------

@dataclass
class ModelSpec:
    """Specification for an LLM model."""

    litellm_id: str            # e.g. "openai/deepseek-chat"
    display_name: str          # e.g. "DeepSeek V3.2"
    cost_per_call_usd: float   # estimated cost per single Critic call
    supports_fc: bool = True   # function calling
    supports_vlm: bool = False # vision/multimodal
    max_tokens: int = 2048
    temperature: float = 0.3
    api_base: str = ""         # override base URL (globalai.vip proxy)
    api_key_env: str = ""      # env var name for API key

    def to_dict(self) -> dict:
        return {
            "litellm_id": self.litellm_id,
            "display_name": self.display_name,
            "cost_per_call_usd": self.cost_per_call_usd,
            "supports_fc": self.supports_fc,
            "supports_vlm": self.supports_vlm,
        }

    def get_api_base(self) -> str | None:
        return self.api_base or None

    def get_api_key(self) -> str | None:
        if self.api_key_env:
            return os.environ.get(self.api_key_env) or _globalai_key() or None
        return _globalai_key() or None


# Pre-defined model catalog — all routed through globalai.vip
MODELS = {
    "deepseek_v3": ModelSpec(
        litellm_id="openai/deepseek-chat",
        display_name="DeepSeek V3.2",
        cost_per_call_usd=0.002,
        supports_fc=True,
        supports_vlm=False,
        temperature=0.3,
        api_base=_GLOBALAI_BASE,
    ),
    "gemini_flash_lite": ModelSpec(
        litellm_id="openai/gemini-2.5-flash",
        display_name="Gemini 2.5 Flash",
        cost_per_call_usd=0.001,
        supports_fc=True,
        supports_vlm=True,
        temperature=0.3,
        api_base=_GLOBALAI_BASE,
    ),
    "qwen_72b": ModelSpec(
        litellm_id="openai/Qwen2.5-72B-Instruct",
        display_name="Qwen2.5-72B",
        cost_per_call_usd=0.0007,
        supports_fc=True,
        supports_vlm=False,
        temperature=0.3,
        api_base=_GLOBALAI_BASE,
    ),
    "gpt4o_mini": ModelSpec(
        litellm_id="openai/gpt-4o-mini",
        display_name="GPT-4o-mini",
        cost_per_call_usd=0.0009,
        supports_fc=True,
        supports_vlm=True,
        temperature=0.3,
        api_base=_GLOBALAI_BASE,
    ),
    "gallery_gpt": ModelSpec(
        litellm_id="local/gallery-gpt-7b",
        display_name="GalleryGPT-7B (local)",
        cost_per_call_usd=0.0,
        supports_fc=False,
        supports_vlm=True,
        temperature=0.3,
    ),
}


# ---------------------------------------------------------------------------
# Default layer → model mapping
# ---------------------------------------------------------------------------

DEFAULT_LAYER_MODELS: dict[str, str] = {
    "visual_perception": "gemini_flash_lite",      # L1: needs VLM
    "technical_analysis": "gemini_flash_lite",      # L2: needs VLM
    "cultural_context": "gemini_flash_lite",        # L3: was deepseek_v3, switched for reliability
    "critical_interpretation": "gemini_flash_lite",  # L4: was deepseek_v3, switched for reliability
    "philosophical_aesthetic": "gemini_flash_lite",  # L5: was deepseek_v3, switched for reliability
}

# Fallback chain per model tier
FALLBACK_CHAINS: dict[str, list[str]] = {
    "deepseek_v3": ["gpt4o_mini"],
    "gemini_flash_lite": ["gpt4o_mini"],
    "gpt4o_mini": [],
}


# ---------------------------------------------------------------------------
# ModelRouter
# ---------------------------------------------------------------------------

@dataclass
class ModelRouter:
    """Routes layer evaluation requests to the appropriate LLM.

    Supports budget constraints, VLM requirements, and fallback chains.
    """

    layer_models: dict[str, str] = field(
        default_factory=lambda: dict(DEFAULT_LAYER_MODELS)
    )
    budget_remaining_usd: float = 5.0

    def select_model(
        self,
        layer_id: str,
        requires_vlm: bool = False,
        budget_remaining: float | None = None,
    ) -> ModelSpec | None:
        """Select the best model for a given layer.

        Returns None if no model is affordable or suitable.
        """
        budget = budget_remaining if budget_remaining is not None else self.budget_remaining_usd
        model_key = self.layer_models.get(layer_id, "deepseek_v3")

        # Try primary model
        spec = MODELS.get(model_key)
        if spec and spec.cost_per_call_usd <= budget:
            if not requires_vlm or spec.supports_vlm:
                return spec

        # Try fallback chain
        fallbacks = FALLBACK_CHAINS.get(model_key, [])
        for fb_key in fallbacks:
            fb_spec = MODELS.get(fb_key)
            if fb_spec and fb_spec.cost_per_call_usd <= budget:
                if not requires_vlm or fb_spec.supports_vlm:
                    return fb_spec

        return None

    def record_cost(self, cost_usd: float) -> None:
        """Deduct cost from remaining budget."""
        self.budget_remaining_usd = max(0.0, self.budget_remaining_usd - cost_usd)

    def to_dict(self) -> dict:
        return {
            "layer_models": self.layer_models,
            "budget_remaining_usd": round(self.budget_remaining_usd, 6),
        }
