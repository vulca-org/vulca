"""DraftConfig with budget guardrails for the Draft Agent."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "DraftConfig",
]


@dataclass
class DraftConfig:
    """Generation configuration with budget guardrails.

    Guardrails:
    - n_candidates is clamped to [1, max_candidates].
    - steps is clamped to [1, 50].
    - width and height are rounded up to the nearest multiple of 64.
    """

    width: int = 512
    height: int = 512
    steps: int = 20
    sampler: str = "euler_a"
    n_candidates: int = 4
    max_candidates: int = 6
    timeout_seconds: int = 120
    max_retries: int = 2
    seed_base: int = 42
    provider: str = "mock"  # "mock" | "nb2" | "diffusers" | "koala"
    api_key: str = ""  # Provider API key (e.g. GOOGLE_API_KEY)
    provider_model: str = ""  # Model ID override (e.g. "black-forest-labs/FLUX.1-schnell")

    # IP-Adapter (Draft-Style)
    ip_adapter_enabled: bool = False
    ip_adapter_scale: float = 0.6
    ip_adapter_reference_path: str = ""  # Path to reference style image

    # ControlNet (Draft-Refine)
    controlnet_enabled: bool = False
    controlnet_type: str = "canny"  # "canny" | "depth"

    # NB2 full evidence injection
    # When True, DraftAgent passes the complete EvidencePack to build_full_evidence_prompt()
    # instead of compressing to a 512-token FLUX-compatible prompt.
    # Only effective when provider="nb2"; ignored for FLUX/SD providers.
    enable_full_evidence_injection: bool = False

    def __post_init__(self) -> None:
        self._apply_guardrails()

    def _apply_guardrails(self) -> None:
        # max_candidates must always be positive.
        if self.max_candidates < 1:
            self.max_candidates = 1

        # n_candidates: clamp to [1, max_candidates]
        if self.n_candidates < 1:
            self.n_candidates = 1
        if self.n_candidates > self.max_candidates:
            self.n_candidates = self.max_candidates

        # steps: clamp to [1, 50]
        if self.steps < 1:
            self.steps = 1
        if self.steps > 50:
            self.steps = 50

        # Retry / timeout guardrails.
        if self.max_retries < 0:
            self.max_retries = 0
        if self.timeout_seconds < 1:
            self.timeout_seconds = 1

        # width/height: round up to multiple of 64
        self.width = _round_up_64(self.width)
        self.height = _round_up_64(self.height)

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "steps": self.steps,
            "sampler": self.sampler,
            "n_candidates": self.n_candidates,
            "max_candidates": self.max_candidates,
            "timeout_seconds": self.timeout_seconds,
            "max_retries": self.max_retries,
            "seed_base": self.seed_base,
            "provider": self.provider,
            "api_key": "***" if self.api_key else "",
            "provider_model": self.provider_model,
            "ip_adapter_enabled": self.ip_adapter_enabled,
            "ip_adapter_scale": self.ip_adapter_scale,
            "controlnet_enabled": self.controlnet_enabled,
            "controlnet_type": self.controlnet_type,
            "enable_full_evidence_injection": self.enable_full_evidence_injection,
        }


def _round_up_64(value: int) -> int:
    """Round *value* up to the nearest positive multiple of 64."""
    if value < 64:
        return 64
    remainder = value % 64
    if remainder == 0:
        return value
    return value + (64 - remainder)
