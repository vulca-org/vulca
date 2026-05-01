"""Real creative brief benchmark harness."""
from __future__ import annotations

from vulca.real_brief.fixtures import (
    build_real_brief_fixtures,
    get_real_brief_fixture,
)
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

_LAZY_EXPORTS = {
    "brief_digest": ("vulca.real_brief.conditions", "brief_digest"),
    "build_real_brief_conditions": (
        "vulca.real_brief.conditions",
        "build_real_brief_conditions",
    ),
    "write_real_brief_dry_run": (
        "vulca.real_brief.artifacts",
        "write_real_brief_dry_run",
    ),
}


def __getattr__(name: str):
    if name not in _LAZY_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module_name, attr_name = _LAZY_EXPORTS[name]
    from importlib import import_module

    value = getattr(import_module(module_name), attr_name)
    globals()[name] = value
    return value
