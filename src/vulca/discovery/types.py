"""Structured data types for visual discovery artifacts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


KNOWN_PROVIDERS = {"mock", "gemini", "nb2", "openai", "comfyui"}


def _require_provider(provider: str) -> str:
    if provider not in KNOWN_PROVIDERS:
        raise ValueError(f"unknown provider: {provider!r}")
    return provider


@dataclass(frozen=True)
class ProviderTarget:
    provider: str
    model: str = ""

    def __post_init__(self) -> None:
        _require_provider(self.provider)

    def to_dict(self) -> dict[str, str]:
        payload = {"provider": self.provider}
        if self.model:
            payload["model"] = self.model
        return payload

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProviderTarget":
        return cls(
            provider=str(data.get("provider", "")),
            model=str(data.get("model", "")),
        )


@dataclass(frozen=True)
class VisualOps:
    composition: str = ""
    color: str = ""
    texture: str = ""
    lighting: str = ""
    camera: str = ""
    typography: str = ""
    symbol_strategy: str = ""
    avoid: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "composition": self.composition,
            "color": self.color,
            "texture": self.texture,
            "lighting": self.lighting,
            "camera": self.camera,
            "typography": self.typography,
            "symbol_strategy": self.symbol_strategy,
            "avoid": list(self.avoid),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VisualOps":
        return cls(
            composition=str(data.get("composition", "")),
            color=str(data.get("color", "")),
            texture=str(data.get("texture", "")),
            lighting=str(data.get("lighting", "")),
            camera=str(data.get("camera", "")),
            typography=str(data.get("typography", "")),
            symbol_strategy=str(data.get("symbol_strategy", "")),
            avoid=[str(item) for item in data.get("avoid", [])],
        )


@dataclass(frozen=True)
class EvaluationFocus:
    L1: str = ""
    L2: str = ""
    L3: str = ""
    L4: str = ""
    L5: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "L1": self.L1,
            "L2": self.L2,
            "L3": self.L3,
            "L4": self.L4,
            "L5": self.L5,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EvaluationFocus":
        return cls(
            L1=str(data.get("L1", "")),
            L2=str(data.get("L2", "")),
            L3=str(data.get("L3", "")),
            L4=str(data.get("L4", "")),
            L5=str(data.get("L5", "")),
        )


@dataclass(frozen=True)
class DirectionCard:
    id: str
    label: str
    summary: str
    culture_terms: list[str]
    visual_ops: VisualOps
    provider_hint: dict[str, ProviderTarget]
    evaluation_focus: EvaluationFocus
    risk: str = ""
    status: str = "candidate"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "summary": self.summary,
            "culture_terms": list(self.culture_terms),
            "visual_ops": self.visual_ops.to_dict(),
            "provider_hint": {
                key: value.to_dict() for key, value in self.provider_hint.items()
            },
            "evaluation_focus": self.evaluation_focus.to_dict(),
            "risk": self.risk,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DirectionCard":
        return cls(
            id=str(data["id"]),
            label=str(data["label"]),
            summary=str(data.get("summary", "")),
            culture_terms=[str(item) for item in data.get("culture_terms", [])],
            visual_ops=VisualOps.from_dict(data.get("visual_ops", {})),
            provider_hint={
                str(key): ProviderTarget.from_dict(value)
                for key, value in data.get("provider_hint", {}).items()
            },
            evaluation_focus=EvaluationFocus.from_dict(
                data.get("evaluation_focus", {})
            ),
            risk=str(data.get("risk", "")),
            status=str(data.get("status", "candidate")),
        )


@dataclass(frozen=True)
class TasteProfile:
    slug: str
    initial_intent: str
    domain_primary: str
    candidate_traditions: list[str]
    culture_terms: list[str]
    mood: list[str] = field(default_factory=list)
    confidence: str = "low"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "0.1",
            "slug": self.slug,
            "source": {
                "initial_intent": self.initial_intent,
                "reference_paths": [],
                "conversation_signals": [],
            },
            "domain": {
                "primary": self.domain_primary,
                "candidates": [],
                "confidence": self.confidence,
            },
            "culture": {
                "primary_tradition": (
                    self.candidate_traditions[0]
                    if self.candidate_traditions
                    else None
                ),
                "candidate_traditions": list(self.candidate_traditions),
                "terms": list(self.culture_terms),
                "avoid_cliches": [],
                "risk_flags": [],
            },
            "aesthetic": {
                "mood": list(self.mood),
                "composition": [],
                "color": [],
                "material": [],
                "typography": [],
                "symbol_strategy": "",
            },
            "commercial_context": {
                "audience": "",
                "channel": "",
                "conversion_pressure": "unknown",
                "brand_maturity": "unknown",
            },
            "selection_history": [],
            "confidence": {
                "overall": self.confidence,
                "needs_more_questions": self.confidence == "low",
            },
        }


@dataclass(frozen=True)
class SketchPrompt:
    card_id: str
    provider: str
    model: str
    prompt: str
    negative_prompt: str
    size: str
    purpose: str

    def __post_init__(self) -> None:
        _require_provider(self.provider)

    def to_dict(self) -> dict[str, str]:
        return {
            "card_id": self.card_id,
            "provider": self.provider,
            "model": self.model,
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "size": self.size,
            "purpose": self.purpose,
        }


@dataclass(frozen=True)
class PromptArtifact:
    provider: str
    model: str
    prompt: str
    negative_prompt: str
    source_card_id: str

    def __post_init__(self) -> None:
        _require_provider(self.provider)

    def to_dict(self) -> dict[str, str]:
        return {
            "provider": self.provider,
            "model": self.model,
            "prompt": self.prompt,
            "negative_prompt": self.negative_prompt,
            "source_card_id": self.source_card_id,
        }
