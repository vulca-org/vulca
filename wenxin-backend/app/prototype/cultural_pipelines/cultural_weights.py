"""Cultural tradition-specific L1-L5 weight tables.

Based on VULCA v2 plan §4 — each tradition has a unique weight profile
reflecting its evaluative priorities (e.g., Chinese xieyi emphasizes L5
philosophical aesthetics, Islamic geometric emphasizes L1+L2 visual precision).

Weight tables sum to 1.0 for each tradition.

Data source: traditions/*.yaml (loaded via tradition_loader.py).
Hardcoded fallback retained for environments without PyYAML.
"""

from __future__ import annotations

import logging

from app.prototype.agents.critic_config import DIMENSIONS

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Hardcoded fallback (used only if YAML loading fails)
# ---------------------------------------------------------------------------

_FALLBACK_WEIGHTS: dict[str, dict[str, float]] = {
    "default": {
        "visual_perception": 0.15,
        "technical_analysis": 0.20,
        "cultural_context": 0.25,
        "critical_interpretation": 0.20,
        "philosophical_aesthetic": 0.20,
    },
    "chinese_xieyi": {
        "visual_perception": 0.10,
        "technical_analysis": 0.15,
        "cultural_context": 0.25,
        "critical_interpretation": 0.20,
        "philosophical_aesthetic": 0.30,
    },
    "chinese_gongbi": {
        "visual_perception": 0.15,
        "technical_analysis": 0.30,
        "cultural_context": 0.25,
        "critical_interpretation": 0.15,
        "philosophical_aesthetic": 0.15,
    },
    "western_academic": {
        "visual_perception": 0.20,
        "technical_analysis": 0.25,
        "cultural_context": 0.15,
        "critical_interpretation": 0.25,
        "philosophical_aesthetic": 0.15,
    },
    "islamic_geometric": {
        "visual_perception": 0.25,
        "technical_analysis": 0.30,
        "cultural_context": 0.20,
        "critical_interpretation": 0.15,
        "philosophical_aesthetic": 0.10,
    },
    "japanese_traditional": {
        "visual_perception": 0.15,
        "technical_analysis": 0.20,
        "cultural_context": 0.20,
        "critical_interpretation": 0.20,
        "philosophical_aesthetic": 0.25,
    },
    "watercolor": {
        "visual_perception": 0.20,
        "technical_analysis": 0.25,
        "cultural_context": 0.15,
        "critical_interpretation": 0.20,
        "philosophical_aesthetic": 0.20,
    },
    "african_traditional": {
        "visual_perception": 0.15,
        "technical_analysis": 0.20,
        "cultural_context": 0.30,
        "critical_interpretation": 0.20,
        "philosophical_aesthetic": 0.15,
    },
    "south_asian": {
        "visual_perception": 0.15,
        "technical_analysis": 0.20,
        "cultural_context": 0.25,
        "critical_interpretation": 0.15,
        "philosophical_aesthetic": 0.25,
    },
}


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


def _get_weight_tables() -> dict[str, dict[str, float]]:
    """Get weight tables, preferring YAML over hardcoded fallback."""
    yaml_tables = _try_load_from_yaml()
    if yaml_tables:
        return yaml_tables
    return _FALLBACK_WEIGHTS


# All traditions that have weight tables
KNOWN_TRADITIONS: list[str] = sorted(_FALLBACK_WEIGHTS.keys())


def get_weights(tradition: str) -> dict[str, float]:
    """Return L1-L5 weights for a given cultural tradition.

    Falls back to ``"default"`` if the tradition is not recognized.
    Prefers YAML data; uses hardcoded fallback if YAML unavailable.
    """
    tables = _get_weight_tables()
    return dict(tables.get(tradition, tables.get("default", _FALLBACK_WEIGHTS["default"])))


def get_all_weight_tables() -> dict[str, dict[str, float]]:
    """Return a copy of the full weight table registry."""
    tables = _get_weight_tables()
    return {k: dict(v) for k, v in tables.items()}
