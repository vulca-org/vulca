"""Cultural tradition-specific L1-L5 weight tables.

Based on VULCA v2 plan §4 — each tradition has a unique weight profile
reflecting its evaluative priorities (e.g., Chinese xieyi emphasizes L5
philosophical aesthetics, Islamic geometric emphasizes L1+L2 visual precision).

Weight tables sum to 1.0 for each tradition.

Data source: traditions/*.yaml (loaded via tradition_loader.py).
Hardcoded fallback retained for environments without PyYAML.
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

from app.prototype.agents.critic_config import DIMENSIONS

logger = logging.getLogger(__name__)

# Path to the evolved context file produced by ContextEvolver
_EVOLVED_CONTEXT_PATH = os.path.join(
    os.path.dirname(__file__), os.pardir, "data", "evolved_context.json"
)

# ---------------------------------------------------------------------------
# Default weights (used when no tradition-specific weights available)
# ---------------------------------------------------------------------------

_DEFAULT_WEIGHTS: dict[str, float] = {
    "visual_perception": 0.15,
    "technical_analysis": 0.20,
    "cultural_context": 0.25,
    "critical_interpretation": 0.20,
    "philosophical_aesthetic": 0.20,
}

_fallback_weights_cache: dict[str, dict[str, float]] | None = None


def _get_fallback_weights() -> dict[str, dict[str, float]]:
    """Load fallback weights from YAML traditions, cache result.

    Loads all tradition weight tables from YAML files via TraditionLoader.
    Falls back to a hardcoded default-only dict if YAML is unavailable.

    Returns a cached dict keyed by tradition name -> dimension weights.
    """
    global _fallback_weights_cache
    if _fallback_weights_cache is not None:
        return _fallback_weights_cache

    weights: dict[str, dict[str, float]] = {"default": _DEFAULT_WEIGHTS.copy()}

    try:
        from app.prototype.cultural_pipelines.tradition_loader import (
            TraditionConfig,
            get_all_traditions,
        )
        traditions = get_all_traditions()
        for name, config in traditions.items():
            yaml_weights = _extract_weights_from_tradition(config)
            if yaml_weights:
                weights[name] = yaml_weights
    except Exception as exc:
        logger.debug(
            "cultural_weights: YAML tradition loading failed (%s), using default-only fallback",
            exc,
        )

    _fallback_weights_cache = weights
    return weights


def _extract_weights_from_tradition(config: object) -> dict[str, float] | None:
    """Extract dimension weights from a TraditionConfig.

    Reads ``weights_dim`` (dimension-keyed dict) from the TraditionConfig
    dataclass produced by tradition_loader. Returns None if extraction fails.
    """
    try:
        # TraditionConfig.weights_dim maps L-labels to dimension IDs
        if hasattr(config, "weights_dim"):
            dim_weights = config.weights_dim
            if isinstance(dim_weights, dict) and dim_weights:
                return dict(dim_weights)
        # Fallback: try weights_l with manual mapping
        if hasattr(config, "weights_l"):
            from app.prototype.cultural_pipelines.tradition_loader import _L_TO_DIM
            w = config.weights_l
            if isinstance(w, dict) and w:
                return {_L_TO_DIM[k]: v for k, v in w.items() if k in _L_TO_DIM}
    except Exception:
        pass
    return None


def _clear_fallback_cache() -> None:
    """Clear the fallback weights cache (for testing)."""
    global _fallback_weights_cache
    _fallback_weights_cache = None


# Backward compatibility alias — deprecated; use _get_fallback_weights()
_FALLBACK_WEIGHTS = _get_fallback_weights


# ---------------------------------------------------------------------------
# YAML-first loading with fallback
# ---------------------------------------------------------------------------

def _try_load_from_yaml() -> dict[str, dict[str, float]] | None:
    """Attempt to load weights from YAML traditions. Returns None on failure."""
    try:
        from app.prototype.cultural_pipelines.tradition_loader import get_all_weight_tables as _yaml_tables
        tables = _yaml_tables()
        if tables:
            logger.info("cultural_weights: loaded %d traditions from YAML", len(tables))
            return tables
    except Exception as e:
        logger.debug("cultural_weights: YAML loading unavailable (%s), using fallback", e)
    return None


def _try_load_from_evolved_context() -> dict[str, dict[str, float]] | None:
    """Attempt to load tradition weights from evolved_context.json.

    Only returns data if the file has the ``tradition_weights`` key
    (produced by ContextEvolver). Legacy formats are ignored.
    """
    try:
        if not os.path.exists(_EVOLVED_CONTEXT_PATH):
            return None
        with open(_EVOLVED_CONTEXT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        tw = data.get("tradition_weights")
        if not isinstance(tw, dict) or not tw:
            return None
        logger.info(
            "cultural_weights: loaded evolved weights for %d traditions (evolution #%d)",
            len(tw), data.get("evolutions", 0),
        )
        return tw
    except Exception as e:
        logger.debug("cultural_weights: evolved_context loading failed (%s)", e)
        return None


def _get_weight_tables() -> dict[str, dict[str, float]]:
    """Get weight tables: evolved_context > YAML > hardcoded fallback.

    Evolved context weights are merged on top of base tables so that
    traditions not yet evolved still have their base weights.
    """
    # Start with base tables (YAML or fallback)
    yaml_tables = _try_load_from_yaml()
    base = yaml_tables if yaml_tables else dict(_get_fallback_weights())

    # Overlay evolved weights if available
    evolved = _try_load_from_evolved_context()
    if evolved:
        for tradition, weights in evolved.items():
            if isinstance(weights, dict) and weights:
                base[tradition] = weights

    return base


# ---------------------------------------------------------------------------
# Dynamic tradition discovery
# ---------------------------------------------------------------------------

def get_known_traditions() -> list[str]:
    """Dynamically collect traditions from evolved_context + YAML + fallback.

    Merges tradition names from three sources (in priority order):
    1. evolved_context.json ``tradition_weights`` keys
    2. YAML tradition loader (``data/traditions/*.yaml``)
    3. ``_get_fallback_weights()`` keys (YAML-derived or default)

    Returns a sorted, deduplicated list of tradition identifiers.
    """
    traditions: set[str] = set(_get_fallback_weights().keys())

    # Add from evolved_context tradition_weights
    evolved = _try_load_from_evolved_context()
    if evolved:
        traditions.update(evolved.keys())

    # Add from YAML loader
    try:
        from app.prototype.cultural_pipelines.tradition_loader import get_all_traditions
        yaml_traditions = get_all_traditions()
        traditions.update(yaml_traditions.keys())
    except (ImportError, Exception):
        pass

    return sorted(traditions)


# Backward compatibility — deprecated; prefer get_known_traditions()
KNOWN_TRADITIONS: list[str] = sorted(_get_fallback_weights().keys())


def get_weights(tradition: str) -> dict[str, float]:
    """Return L1-L5 weights for a given cultural tradition.

    Falls back to ``"default"`` if the tradition is not recognized.
    Prefers YAML data; uses hardcoded fallback if YAML unavailable.
    """
    tables = _get_weight_tables()
    return dict(tables.get(tradition, tables.get("default", _DEFAULT_WEIGHTS)))


def get_all_weight_tables() -> dict[str, dict[str, float]]:
    """Return a copy of the full weight table registry."""
    tables = _get_weight_tables()
    return {k: dict(v) for k, v in tables.items()}


def get_prompt_archetypes(tradition: str, top_n: int = 5) -> list[dict]:
    """Return top-N prompt archetypes for a tradition from evolved_context.json.

    Reads the ``prompt_contexts.archetypes`` section written by
    :class:`~app.prototype.digestion.context_evolver.ContextEvolver` and
    filters entries whose ``traditions`` list includes *tradition*.

    Parameters
    ----------
    tradition:
        Cultural tradition key (e.g. ``"chinese_xieyi"``).
    top_n:
        Maximum number of archetypes to return (default 5).

    Returns
    -------
    list[dict]
        Each dict has at least ``pattern`` (str) and ``avg_score`` (float).
        Returns an empty list if the file is missing or has no matching data.
    """
    try:
        if not os.path.exists(_EVOLVED_CONTEXT_PATH):
            return []
        with open(_EVOLVED_CONTEXT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        archetypes = data.get("prompt_contexts", {}).get("archetypes")
        if not isinstance(archetypes, list) or not archetypes:
            return []

        # Filter by tradition — include archetypes whose traditions list
        # contains the requested tradition, or that have no traditions
        # (universal archetypes).
        filtered = [
            a for a in archetypes
            if tradition in a.get("traditions", [])
            or not a.get("traditions")
        ]

        # Sort by avg_score descending, take top N
        filtered.sort(key=lambda a: a.get("avg_score", 0), reverse=True)
        return filtered[:top_n]
    except Exception as exc:
        logger.debug("get_prompt_archetypes: failed to load (%s)", exc)
        return []


# ---------------------------------------------------------------------------
# Evolved prompt context injection
# ---------------------------------------------------------------------------

_evolved_prompt_cache: dict[str, tuple[float, str]] = {}
_CACHE_TTL = 300  # 5 minutes


def get_evolved_prompt_context(tradition: str = "default", max_tokens: int = 200) -> str:
    """Get evolved context block for system prompt injection.

    Returns a formatted string (approximate max_tokens words) with:
    - Archetypes (successful patterns)
    - Emerged cultural concepts
    - Weight/preference hints

    Returns ``""`` if no evolved data available (zero regression).
    """
    cache_key = f"{tradition}:{max_tokens}"
    now = time.time()
    if cache_key in _evolved_prompt_cache:
        cached_time, cached_val = _evolved_prompt_cache[cache_key]
        if now - cached_time < _CACHE_TTL:
            return cached_val

    result = _build_evolved_context(tradition, max_tokens)
    _evolved_prompt_cache[cache_key] = (now, result)
    return result


def _build_evolved_context(tradition: str, max_tokens: int) -> str:
    """Build the evolved context string from evolved_context.json."""
    ctx_path = Path(_EVOLVED_CONTEXT_PATH).resolve()
    if not ctx_path.exists():
        return ""

    try:
        ctx = json.loads(ctx_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""

    if ctx.get("evolutions", 0) == 0:
        return ""

    parts: list[str] = []

    # 1. Archetypes / successful patterns from prompt_contexts
    prompt_contexts = ctx.get("prompt_contexts", {})
    tradition_prompts = prompt_contexts.get(tradition, prompt_contexts.get("default", {}))
    if isinstance(tradition_prompts, dict):
        top_keywords = tradition_prompts.get("top_keywords", [])[:5]
        if top_keywords:
            parts.append(f"Successful patterns: {', '.join(top_keywords)}")

    # 2. Emerged cultural concepts
    cultures = ctx.get("cultures", {})
    if isinstance(cultures, dict):
        relevant = {k: v for k, v in cultures.items()
                    if isinstance(v, dict) and (v.get("tradition") == tradition or tradition == "default")}
        if relevant:
            concept_names = list(relevant.keys())[:3]
            parts.append(f"Emerged concepts: {', '.join(concept_names)}")
    elif isinstance(cultures, list):
        relevant = [c for c in cultures if isinstance(c, dict)
                    and (c.get("tradition") == tradition or tradition == "default")]
        if relevant:
            concept_names = [c.get("name", "unknown") for c in relevant[:3]]
            parts.append(f"Emerged concepts: {', '.join(concept_names)}")

    # 3. Weight hints from tradition_weights
    weights = ctx.get("tradition_weights", {}).get(tradition, {})
    if isinstance(weights, dict) and weights:
        top_dims = sorted(weights.items(), key=lambda x: x[1], reverse=True)[:3]
        hints = [f"{d}={v:.2f}" for d, v in top_dims]
        parts.append(f"Priority dimensions: {', '.join(hints)}")

    if not parts:
        return ""

    # Truncate to approximate max_tokens
    context = "\n".join(parts)
    words = context.split()
    if len(words) > max_tokens:
        context = " ".join(words[:max_tokens])

    return f"\n\n[Evolved Context]\n{context}"
