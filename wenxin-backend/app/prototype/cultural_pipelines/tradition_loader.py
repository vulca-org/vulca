"""TRADITION.yaml loader — loads cultural traditions from YAML files.

Replaces hardcoded Python dicts with community-contributable YAML configs.
Each tradition is a single YAML file in data/traditions/.

Public API (backward-compatible with cultural_weights.py):
    get_weights(tradition) -> dict[str, float]
    get_all_weight_tables() -> dict[str, dict[str, float]]
    KNOWN_TRADITIONS: list[str]

Additional API:
    get_tradition(name) -> TraditionConfig | None
    get_all_traditions() -> dict[str, TraditionConfig]
    reload_traditions() -> None  # hot-reload for dev
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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

# Default traditions directory
_TRADITIONS_DIR = Path(__file__).resolve().parent.parent / "data" / "traditions"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TermEntry:
    term: str
    term_zh: str
    definition: str | dict[str, str]
    category: str
    l_levels: list[str]
    aliases: list[str] = field(default_factory=list)
    source: str = ""


@dataclass
class TabooEntry:
    rule: str
    severity: str
    l_levels: list[str] = field(default_factory=list)
    trigger_patterns: list[str] = field(default_factory=list)
    explanation: str = ""


@dataclass
class PipelineConfig:
    variant: str = "default"
    overrides: dict[str, Any] = field(default_factory=dict)


@dataclass
class TraditionConfig:
    """A fully loaded tradition definition."""

    name: str
    display_name: dict[str, str]
    weights_l: dict[str, float]  # {"L1": 0.15, "L2": 0.20, ...}
    terminology: list[TermEntry]
    taboos: list[TabooEntry]
    pipeline: PipelineConfig
    examples: list[dict[str, str]] = field(default_factory=list)

    @property
    def weights_dim(self) -> dict[str, float]:
        """Return weights keyed by dimension ID (visual_perception, etc.)."""
        return {_L_TO_DIM[k]: v for k, v in self.weights_l.items() if k in _L_TO_DIM}


# ---------------------------------------------------------------------------
# Registry (module-level singleton)
# ---------------------------------------------------------------------------

_registry: dict[str, TraditionConfig] = {}
_loaded: bool = False


def _parse_tradition(data: dict[str, Any]) -> TraditionConfig:
    """Parse a raw YAML dict into a TraditionConfig."""
    terms = []
    for t in data.get("terminology", []):
        defn = t.get("definition", "")
        if isinstance(defn, dict):
            defn_val = defn
        else:
            defn_val = str(defn)
        terms.append(TermEntry(
            term=t["term"],
            term_zh=t.get("term_zh", ""),
            definition=defn_val,
            category=t.get("category", "technique"),
            l_levels=t.get("l_levels", []),
            aliases=t.get("aliases", []),
            source=t.get("source", ""),
        ))

    taboos = []
    for tb in data.get("taboos", []):
        taboos.append(TabooEntry(
            rule=tb["rule"],
            severity=tb.get("severity", "medium"),
            l_levels=tb.get("l_levels", []),
            trigger_patterns=tb.get("trigger_patterns", []),
            explanation=tb.get("explanation", ""),
        ))

    pipe_raw = data.get("pipeline", {})
    pipeline = PipelineConfig(
        variant=pipe_raw.get("variant", "default"),
        overrides=pipe_raw.get("overrides", {}),
    )

    return TraditionConfig(
        name=data["name"],
        display_name=data.get("display_name", {"en": data["name"]}),
        weights_l=data.get("weights", {"L1": 0.20, "L2": 0.20, "L3": 0.20, "L4": 0.20, "L5": 0.20}),
        terminology=terms,
        taboos=taboos,
        pipeline=pipeline,
        examples=data.get("examples", []),
    )


def _load_all(traditions_dir: Path | None = None) -> dict[str, TraditionConfig]:
    """Load all .yaml files from the traditions directory."""
    try:
        import yaml  # noqa: F811
    except ImportError:
        logger.warning("PyYAML not installed — tradition YAML loading disabled, using empty registry")
        return {}

    directory = traditions_dir or _TRADITIONS_DIR
    if not directory.is_dir():
        logger.warning("Traditions directory not found: %s", directory)
        return {}

    result: dict[str, TraditionConfig] = {}
    for path in sorted(directory.glob("*.yaml")):
        if path.name.startswith("_"):
            continue  # skip _template.yaml
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not data or "name" not in data:
                logger.warning("Skipping invalid tradition file: %s", path.name)
                continue
            tc = _parse_tradition(data)
            # Validate weights sum
            w_sum = sum(tc.weights_l.values())
            if abs(w_sum - 1.0) > 0.01:
                logger.warning(
                    "Tradition %s weights sum to %.3f (expected 1.0), normalizing",
                    tc.name, w_sum,
                )
                tc.weights_l = {k: v / w_sum for k, v in tc.weights_l.items()}
            result[tc.name] = tc
            logger.debug("Loaded tradition: %s (%d terms, %d taboos)",
                         tc.name, len(tc.terminology), len(tc.taboos))
        except Exception as e:
            logger.error("Failed to load tradition %s: %s", path.name, e)

    logger.info("Loaded %d traditions from %s", len(result), directory)
    return result


def _ensure_loaded() -> None:
    """Lazy-load traditions on first access."""
    global _loaded, _registry
    if not _loaded:
        _registry = _load_all()
        _loaded = True


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_tradition(name: str) -> TraditionConfig | None:
    """Get a tradition by name, or None if not found."""
    _ensure_loaded()
    return _registry.get(name)


def get_all_traditions() -> dict[str, TraditionConfig]:
    """Return all loaded traditions."""
    _ensure_loaded()
    return dict(_registry)


def get_weights(tradition: str) -> dict[str, float]:
    """Return L1-L5 weights keyed by dimension ID (backward-compatible).

    Falls back to 'default' tradition if not found.
    """
    _ensure_loaded()
    tc = _registry.get(tradition) or _registry.get("default")
    if tc:
        return dict(tc.weights_dim)
    # Ultimate fallback if no YAML loaded at all
    return {
        "visual_perception": 0.15,
        "technical_analysis": 0.20,
        "cultural_context": 0.25,
        "critical_interpretation": 0.20,
        "philosophical_aesthetic": 0.20,
    }


def get_all_weight_tables() -> dict[str, dict[str, float]]:
    """Return all weight tables keyed by tradition name (backward-compatible)."""
    _ensure_loaded()
    return {name: dict(tc.weights_dim) for name, tc in _registry.items()}


def get_known_traditions() -> list[str]:
    """Return sorted list of all loaded tradition names."""
    _ensure_loaded()
    return sorted(_registry.keys())


# Backward-compatible module-level constant (lazy property via descriptor trick)
class _KnownTraditionsDescriptor:
    """Lazy list that loads traditions on first access."""
    def __get__(self, obj: Any, objtype: Any = None) -> list[str]:
        return get_known_traditions()


# For direct attribute access: tradition_loader.KNOWN_TRADITIONS
KNOWN_TRADITIONS: list[str] = []  # type: ignore[assignment]


def reload_traditions(traditions_dir: Path | None = None) -> int:
    """Force reload all traditions (for dev hot-reload)."""
    global _loaded, _registry
    _registry = _load_all(traditions_dir)
    _loaded = True
    return len(_registry)


def validate_tradition_yaml(path: str | Path) -> list[str]:
    """Validate a tradition YAML file and return list of errors (empty = valid)."""
    try:
        import yaml
    except ImportError:
        return ["PyYAML not installed"]

    errors: list[str] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        return [f"YAML parse error: {e}"]

    if not isinstance(data, dict):
        return ["Root must be a mapping"]

    # Required fields
    for field_name in ("name", "display_name", "weights", "terminology", "taboos", "pipeline"):
        if field_name not in data:
            errors.append(f"Missing required field: {field_name}")

    # Name format
    name = data.get("name", "")
    if name and not all(c.isalnum() or c == "_" for c in name):
        errors.append(f"name must be snake_case: {name}")

    # Weights validation
    weights = data.get("weights", {})
    if weights:
        for lbl in ("L1", "L2", "L3", "L4", "L5"):
            if lbl not in weights:
                errors.append(f"Missing weight: {lbl}")
            elif not isinstance(weights[lbl], (int, float)):
                errors.append(f"Weight {lbl} must be a number")
        w_sum = sum(v for v in weights.values() if isinstance(v, (int, float)))
        if abs(w_sum - 1.0) > 0.02:
            errors.append(f"Weights sum to {w_sum:.3f}, expected 1.0")

    # Terminology
    terms = data.get("terminology", [])
    if isinstance(terms, list) and len(terms) < 1:
        errors.append("At least 1 terminology entry required")
    for i, t in enumerate(terms if isinstance(terms, list) else []):
        if not isinstance(t, dict):
            errors.append(f"terminology[{i}] must be a mapping")
            continue
        if "term" not in t:
            errors.append(f"terminology[{i}] missing 'term'")
        if "l_levels" not in t:
            errors.append(f"terminology[{i}] missing 'l_levels'")

    # Taboos
    taboos = data.get("taboos", [])
    for i, tb in enumerate(taboos if isinstance(taboos, list) else []):
        if not isinstance(tb, dict):
            errors.append(f"taboos[{i}] must be a mapping")
            continue
        if "rule" not in tb:
            errors.append(f"taboos[{i}] missing 'rule'")
        if "severity" not in tb:
            errors.append(f"taboos[{i}] missing 'severity'")

    return errors
