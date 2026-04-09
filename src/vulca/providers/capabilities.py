"""Coarse provider-kind capability lookup (by provider name).

Distinct from ImageProvider.capabilities — that Protocol attribute is
scoped to image-runtime details (raw_rgba, streaming, ...). This module
answers the coarser question "what kinds of work does a provider named X
do at all", needed by pipeline nodes that only hold a string name.

Design: inverted default — unknown names get FULL capabilities, matching
the pre-v0.13.3 behavior where every non-mock provider went through real
code paths and was cost-charged. Only "mock" (and future explicitly-
limited providers) opt out.
"""
from __future__ import annotations

VLM_SCORING = "vlm_scoring"
LLM_TEXT = "llm_text"
COST_TRACKED = "cost_tracked"

_DEFAULT_CAPABILITIES = frozenset({VLM_SCORING, LLM_TEXT, COST_TRACKED})

_PROVIDER_CAPABILITIES: dict[str, frozenset[str]] = {
    "mock": frozenset(),
    # Future explicitly-limited providers declare reduced caps here.
    # e.g. "sd_local": frozenset() — image-only, free, no VLM/LLM.
}


def provider_capabilities(name: str | None) -> frozenset[str]:
    """Return coarse capabilities for a provider name.

    Unknown/unregistered names return the FULL capability set — preserves
    pre-v0.13.3 behavior where every non-mock provider went through real
    code paths and was cost-charged via _COST_PER_IMAGE.get(name, 0.067).

    None/empty → frozenset() (same as mock — no real work).
    """
    if not name:
        return frozenset()
    return _PROVIDER_CAPABILITIES.get(name, _DEFAULT_CAPABILITIES)
