"""Model Router — selects the optimal LLM for each layer and task.

Routes requests through LiteLLM for unified API access. Supports:
- Per-layer model assignment (L1-L5 all Gemini)
- Budget-aware fallback chains
- Confidence-based escalation

M0 Gemini migration: single-vendor stack via ``gemini/`` LiteLLM prefix.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "DEFAULT_LAYER_MODELS",
    "FALLBACK_CHAINS",
    "MODEL_DECISION",
    "MODEL_FAST",
    "MODEL_VLM",
    "MODELS",
    "ModelRouter",
    "ModelSpec",
]

# === Semantic model constants ===
# Change these to switch all agents to a different model
MODEL_VLM = "gemini/gemini-2.5-flash"       # Vision-capable (for image analysis)
MODEL_FAST = "gemini/gemini-2.0-flash"       # Fast text-only (for generation, crystallization)
MODEL_DECISION = "gemini/gemini-2.5-flash"   # Decision-making (for routing, queen)


def _google_api_key() -> str:
    """Get the Google API key for Gemini direct access."""
    from app.core.config import settings as _settings
    return (
        os.environ.get("GOOGLE_API_KEY")
        or os.environ.get("GEMINI_API_KEY")
        or _settings.GOOGLE_API_KEY
        or _settings.GEMINI_API_KEY
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
            return os.environ.get(self.api_key_env) or _google_api_key() or None
        return _google_api_key() or None


# Pre-defined model catalog — Gemini single-vendor (M0)
MODELS = {
    "gemini_direct": ModelSpec(
        litellm_id=MODEL_VLM,
        display_name="Gemini 2.5 Flash",
        cost_per_call_usd=0.001,
        supports_fc=True,
        supports_vlm=True,
        temperature=0.3,
        api_key_env="GOOGLE_API_KEY",
    ),
}


# ---------------------------------------------------------------------------
# Default layer → model mapping
# ---------------------------------------------------------------------------

DEFAULT_LAYER_MODELS: dict[str, str] = {
    "visual_perception": "gemini_direct",      # L1: VLM
    "technical_analysis": "gemini_direct",      # L2: VLM
    "cultural_context": "gemini_direct",        # L3: text + VLM
    "critical_interpretation": "gemini_direct",  # L4: text + VLM
    "philosophical_aesthetic": "gemini_direct",  # L5: text + VLM
}

# Fallback chain — single vendor, no alternative providers
FALLBACK_CHAINS: dict[str, list[str]] = {
    "gemini_direct": [],
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
        model_key = self.layer_models.get(layer_id, "gemini_direct")

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
