"""Structured real-brief benchmark data types."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any


_SAFE_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")

AI_POLICIES = {"allowed", "prohibited_for_submission", "unspecified"}
CONDITION_IDS = ("A", "B", "C", "D")
REVIEW_DIMENSIONS = (
    "brief_compliance",
    "audience_fit",
    "deliverable_fit",
    "constraint_handling",
    "cultural_taste_specificity",
    "structural_control",
    "editability_reusability",
    "production_realism",
    "risk_avoidance",
    "decision_usefulness",
)


def safe_slug(slug: str) -> str:
    if (
        not slug
        or slug in {".", ".."}
        or "/" in slug
        or "\\" in slug
        or ".." in slug
        or not _SAFE_SLUG_RE.match(slug)
    ):
        raise ValueError(
            "safe slug required: lowercase letters, digits, '.', '_' or '-' only"
        )
    return slug


@dataclass(frozen=True)
class SourceInfo:
    url: str
    retrieved_on: str
    usage_note: str = "Internal benchmark only"
    deadline: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class Deliverable:
    name: str
    format: str
    channel: str
    required: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RealBriefFixture:
    slug: str
    title: str
    source: SourceInfo
    client: str
    context: str
    audience: list[str]
    deliverables: list[Deliverable]
    constraints: list[str]
    budget: str
    timeline: str
    required_outputs: list[str]
    ai_policy: str
    simulation_only: bool
    risks: list[str]
    avoid: list[str]
    evaluation_dimensions: list[str]
    source_brief: str = ""
    domain: str = "brand_visual"
    tags: list[str] = field(default_factory=list)

    def validate(self) -> None:
        safe_slug(self.slug)
        if not self.title.strip():
            raise ValueError(f"{self.slug}: title is required")
        if not self.source.url.startswith(("https://", "http://")):
            raise ValueError(f"{self.slug}: source.url must be absolute http(s)")
        for field_name in (
            "client",
            "context",
            "budget",
            "timeline",
            "ai_policy",
            "domain",
        ):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"{self.slug}: {field_name} is required")
        if self.ai_policy not in AI_POLICIES:
            raise ValueError(f"{self.slug}: unsupported ai_policy {self.ai_policy!r}")
        list_fields = {
            "audience": self.audience,
            "deliverables": self.deliverables,
            "constraints": self.constraints,
            "required_outputs": self.required_outputs,
            "risks": self.risks,
            "avoid": self.avoid,
            "evaluation_dimensions": self.evaluation_dimensions,
        }
        for field_name, value in list_fields.items():
            if not value:
                raise ValueError(f"{self.slug}: {field_name} must not be empty")
        unknown_dimensions = [
            item for item in self.evaluation_dimensions if item not in REVIEW_DIMENSIONS
        ]
        if unknown_dimensions:
            joined = ", ".join(unknown_dimensions)
            raise ValueError(f"{self.slug}: unknown evaluation dimensions: {joined}")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema_version": "0.1",
            "slug": self.slug,
            "title": self.title,
            "source": self.source.to_dict(),
            "client": self.client,
            "context": self.context,
            "audience": list(self.audience),
            "deliverables": [item.to_dict() for item in self.deliverables],
            "constraints": list(self.constraints),
            "budget": self.budget,
            "timeline": self.timeline,
            "required_outputs": list(self.required_outputs),
            "ai_policy": self.ai_policy,
            "simulation_only": self.simulation_only,
            "risks": list(self.risks),
            "avoid": list(self.avoid),
            "evaluation_dimensions": list(self.evaluation_dimensions),
            "source_brief": self.source_brief,
            "domain": self.domain,
            "tags": list(self.tags),
        }
