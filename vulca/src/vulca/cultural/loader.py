"""Tradition YAML loader -- loads cultural traditions from YAML files.

Public API (backward-compatible with hardcoded weights):
    get_tradition(name) -> TraditionConfig | None
    get_all_traditions() -> dict[str, TraditionConfig]
    get_weights(tradition) -> dict[str, float]
    get_all_weight_tables() -> dict[str, dict[str, float]]
    get_known_traditions() -> list[str]
    reload_traditions() -> int
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from vulca.cultural.types import PipelineConfig, TabooEntry, TermEntry, TraditionConfig

logger = logging.getLogger(__name__)

# L-level label to dimension ID mapping
_L_TO_DIM: dict[str, str] = {
    "L1": "visual_perception",
    "L2": "technical_analysis",
    "L3": "cultural_context",
    "L4": "critical_interpretation",
    "L5": "philosophical_aesthetic",
}

_DIM_TO_L: dict[str, str] = {v: k for k, v in _L_TO_DIM.items()}

# Default traditions directory (bundled with package)
_BUNDLED_DIR = Path(__file__).resolve().parent / "data" / "traditions"

# Default fallback weights
_DEFAULT_WEIGHTS: dict[str, float] = {
    "L1": 0.15, "L2": 0.20, "L3": 0.25, "L4": 0.20, "L5": 0.20,
}

# Cache
_traditions: dict[str, TraditionConfig] = {}
_loaded = False


def _get_traditions_dir() -> Path:
    """Get the traditions directory, preferring env override."""
    env_dir = os.environ.get("VULCA_TRADITIONS_DIR")
    if env_dir:
        p = Path(env_dir)
        if p.is_dir():
            return p
    return _BUNDLED_DIR


def _ensure_loaded() -> None:
    """Load traditions on first access."""
    global _loaded
    if not _loaded:
        reload_traditions()
        _loaded = True


def reload_traditions() -> int:
    """(Re)load all tradition YAML files. Returns count loaded."""
    global _traditions, _loaded

    try:
        import yaml
    except ImportError:
        logger.warning("PyYAML not installed, using hardcoded defaults only")
        _traditions = {}
        _loaded = True
        return 0

    traditions_dir = _get_traditions_dir()
    if not traditions_dir.is_dir():
        logger.warning("Traditions directory not found: %s", traditions_dir)
        _traditions = {}
        _loaded = True
        return 0

    new_traditions: dict[str, TraditionConfig] = {}
    count = 0

    for yaml_path in sorted(traditions_dir.glob("*.yaml")):
        if yaml_path.name.startswith("_"):
            continue
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict):
                continue

            name = data.get("name", yaml_path.stem)

            # Parse weights
            weights_raw = data.get("weights", {})
            weights_l: dict[str, float] = {}
            for key, val in weights_raw.items():
                l_key = key if key.startswith("L") else _DIM_TO_L.get(key, key)
                weights_l[l_key] = float(val)
            if not weights_l:
                weights_l = dict(_DEFAULT_WEIGHTS)

            # Parse terminology
            terms = []
            for t in data.get("terminology", []):
                if isinstance(t, dict):
                    terms.append(TermEntry(
                        term=t.get("term", ""),
                        term_zh=t.get("term_zh", ""),
                        definition=t.get("definition", ""),
                        category=t.get("category", ""),
                        l_levels=t.get("l_levels", []),
                        aliases=t.get("aliases", []),
                        source=t.get("source", ""),
                    ))

            # Parse taboos
            taboos = []
            for tb in data.get("taboos", []):
                if isinstance(tb, dict):
                    taboos.append(TabooEntry(
                        rule=tb.get("rule", ""),
                        severity=tb.get("severity", "medium"),
                        l_levels=tb.get("l_levels", []),
                        trigger_patterns=tb.get("trigger_patterns", []),
                        explanation=tb.get("explanation", ""),
                    ))

            # Parse pipeline config
            pipe_data = data.get("pipeline", {})
            pipeline = PipelineConfig(
                variant=pipe_data.get("variant", "default"),
                overrides=pipe_data.get("overrides", {}),
            )

            # Display name
            display_raw = data.get("display_name", {})
            if isinstance(display_raw, str):
                display_name = {"en": display_raw, "zh": ""}
            elif isinstance(display_raw, dict):
                display_name = {"en": display_raw.get("en", name), "zh": display_raw.get("zh", "")}
            else:
                display_name = {"en": name, "zh": ""}

            tc = TraditionConfig(
                name=name,
                display_name=display_name,
                weights_l=weights_l,
                terminology=terms,
                taboos=taboos,
                pipeline=pipeline,
                examples=data.get("examples", []),
            )
            new_traditions[name] = tc
            count += 1

        except Exception as exc:
            logger.warning("Failed to load tradition %s: %s", yaml_path.name, exc)

    _traditions = new_traditions
    _loaded = True
    logger.info("Loaded %d traditions from %s", count, traditions_dir)
    return count


def get_tradition(name: str) -> TraditionConfig | None:
    """Get a single tradition config by name."""
    _ensure_loaded()
    return _traditions.get(name)


def get_all_traditions() -> dict[str, TraditionConfig]:
    """Get all loaded tradition configs."""
    _ensure_loaded()
    return dict(_traditions)


def get_known_traditions() -> list[str]:
    """Get sorted list of known tradition names."""
    _ensure_loaded()
    if _traditions:
        return sorted(_traditions.keys())
    # Fallback to hardcoded list
    from vulca.cultural import TRADITIONS
    return list(TRADITIONS)


def get_weights(tradition: str) -> dict[str, float]:
    """Get L1-L5 weights for a tradition.

    Priority: YAML config > hardcoded TRADITION_WEIGHTS > default.
    """
    _ensure_loaded()
    tc = _traditions.get(tradition)
    if tc:
        return dict(tc.weights_l)
    # Fallback to hardcoded
    from vulca.cultural import TRADITION_WEIGHTS
    return dict(TRADITION_WEIGHTS.get(tradition, _DEFAULT_WEIGHTS))


def get_all_weight_tables() -> dict[str, dict[str, float]]:
    """Get weight tables for all traditions."""
    _ensure_loaded()
    if _traditions:
        return {name: dict(tc.weights_l) for name, tc in _traditions.items()}
    from vulca.cultural import TRADITION_WEIGHTS
    return dict(TRADITION_WEIGHTS)
