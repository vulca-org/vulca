"""Generic fallback chain configuration for pipeline providers.

This module provides a convenience factory to build a FallbackProvider
from a list of provider names.

Default Draft fallback chain: nb2 → koala → diffusers → mock
"""

from __future__ import annotations

import logging
import os

from app.prototype.agents.draft_provider import (
    AbstractProvider,
    DiffusersProvider,
    FallbackProvider,
    FaultInjectProvider,
    MockProvider,
)

logger = logging.getLogger(__name__)

_PROVIDER_REGISTRY: dict[str, type[AbstractProvider]] = {
    "mock": MockProvider,
    "diffusers": DiffusersProvider,
}

# Default Draft generation fallback order (M0: nb2 replaces together_flux)
DEFAULT_DRAFT_FALLBACK = ["nb2", "koala", "diffusers", "mock"]


def build_fallback_provider(
    provider_names: list[str] | None = None,
    max_retries: int = 2,
    backoff_base_ms: int = 0,
    api_key: str = "",
) -> FallbackProvider:
    """Build a FallbackProvider from a list of provider names.

    Unknown names are skipped. Always ensures MockProvider is the final fallback.
    If provider_names is None, uses DEFAULT_DRAFT_FALLBACK.
    """
    if provider_names is None:
        provider_names = list(DEFAULT_DRAFT_FALLBACK)

    providers: list[AbstractProvider] = []
    seen: set[str] = set()

    for name in provider_names:
        if name in seen:
            continue
        seen.add(name)
        if name == "together_flux":
            # M0 compat: redirect to nb2
            logger.warning("together_flux deprecated, skipping in fallback chain (use nb2)")
        elif name == "nb2":
            try:
                from app.prototype.agents.nb2_provider import NB2Provider
                from app.core.config import settings as _settings
                key = (
                    api_key
                    or os.environ.get("GOOGLE_API_KEY", "")
                    or os.environ.get("GEMINI_API_KEY", "")
                    or _settings.GOOGLE_API_KEY
                    or _settings.GEMINI_API_KEY
                )
                if key:
                    providers.append(NB2Provider(api_key=key))
            except ImportError:
                pass
        elif name == "koala":
            try:
                from app.prototype.agents.koala_provider import KoalaProvider
                kp = KoalaProvider()
                if kp.available:
                    from app.prototype.agents.draft_agent import _KoalaProviderAdapter
                    providers.append(_KoalaProviderAdapter(kp))
            except ImportError:
                pass
        elif name == "diffusers":
            try:
                providers.append(DiffusersProvider())
            except Exception:
                pass
        elif name == "mock":
            providers.append(MockProvider())

    # Ensure mock is always last fallback
    if "mock" not in seen:
        providers.append(MockProvider())

    return FallbackProvider(
        providers=providers,
        max_retries_per_provider=max_retries,
        backoff_base_ms=backoff_base_ms,
    )
