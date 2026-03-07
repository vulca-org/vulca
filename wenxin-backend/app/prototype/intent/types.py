"""Data types for the Intent Layer."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class IntentResult:
    """Parsed intent from natural language input."""

    tradition: str
    context: str
    confidence: float
    raw_intent: str


@dataclass
class ResultCard:
    """Frontend-friendly evaluation result card."""

    score: float
    summary: str
    risk_level: str
    dimensions: dict[str, float]
    recommendations: list[str]
    tradition_used: str
