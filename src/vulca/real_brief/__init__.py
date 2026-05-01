"""Real creative brief benchmark harness."""
from __future__ import annotations

from vulca.real_brief.fixtures import (
    build_real_brief_fixtures,
    get_real_brief_fixture,
)
from vulca.real_brief.conditions import (
    brief_digest,
    build_real_brief_conditions,
)
from vulca.real_brief.artifacts import write_real_brief_dry_run
from vulca.real_brief.types import (
    CONDITION_IDS,
    REVIEW_DIMENSIONS,
    Deliverable,
    RealBriefFixture,
    SourceInfo,
    safe_slug,
)

__all__ = [
    "CONDITION_IDS",
    "REVIEW_DIMENSIONS",
    "brief_digest",
    "build_real_brief_conditions",
    "build_real_brief_fixtures",
    "Deliverable",
    "get_real_brief_fixture",
    "RealBriefFixture",
    "SourceInfo",
    "safe_slug",
    "write_real_brief_dry_run",
]
