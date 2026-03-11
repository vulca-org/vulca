"""Scout tool output types — aligned with Intent Card evidence schema (D2)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SampleMatchResult:
    """A single VULCA-Bench sample match result."""

    sample_id: str       # "vulca-bench-NNNN"
    similarity: float    # [0, 1]
    source: str          # "VULCA-Bench-v1"

    def to_dict(self) -> dict:
        return {
            "sample_id": self.sample_id,
            "similarity": round(self.similarity, 4),
            "source": self.source,
        }


@dataclass
class TerminologyHitResult:
    """A single terminology dictionary match result."""

    term: str            # matched term text
    matched: bool        # True
    confidence: float    # [0, 1] — exact=1.0, alias=0.9, fuzzy=0.7
    dictionary_ref: str  # "terms_v1_<tradition>"

    def to_dict(self) -> dict:
        return {
            "term": self.term,
            "matched": self.matched,
            "confidence": round(self.confidence, 4),
            "dictionary_ref": self.dictionary_ref,
        }


@dataclass
class TabooViolationResult:
    """A single cultural taboo violation result."""

    rule_id: str         # "taboo-xxx-NNN"
    description: str     # rule description
    severity: str        # "low" | "medium" | "high" | "critical"

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "severity": self.severity,
        }


@dataclass
class ScoutEvidence:
    """Aggregated Scout evidence — maps directly to Intent Card `evidence` field."""

    sample_matches: list[SampleMatchResult] = field(default_factory=list)
    terminology_hits: list[TerminologyHitResult] = field(default_factory=list)
    taboo_violations: list[TabooViolationResult] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        result = {
            "sample_matches": [m.to_dict() for m in self.sample_matches],
            "terminology_hits": [h.to_dict() for h in self.terminology_hits],
            "taboo_violations": [v.to_dict() for v in self.taboo_violations],
        }
        if self.notes:
            result["notes"] = list(self.notes)
        return result
