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

# Canonical directory for evolved_context.json.
# Override via VULCA_DATA_DIR env, or monkeypatch _EVOLVED_CONTEXT_DIR for tests.
_EVOLVED_CONTEXT_DIR: Path | None = None

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
                extra_dimensions=data.get("extra_dimensions", []),
                layerability=data.get("layerability") or "split",
                canvas_color=data.get("canvas_color") or "#ffffff",
                canvas_description=data.get("canvas_description") or "",
                key_strategy=data.get("key_strategy") or "luminance",
                style_keywords=data.get("style_keywords") or "",
            )
            new_traditions[name] = tc
            count += 1

        except Exception as exc:
            logger.warning("Failed to load tradition %s: %s", yaml_path.name, exc)

    _traditions = new_traditions
    _loaded = True
    logger.info("Loaded %d traditions from %s", count, traditions_dir)
    return count


def _load_single_yaml(path: Path) -> TraditionConfig | None:
    """Load a single YAML tradition file (custom or built-in)."""
    try:
        import yaml
    except ImportError:
        logger.warning("PyYAML not installed, cannot load custom tradition file")
        return None

    if not path.is_file():
        logger.warning("Tradition file not found: %s", path)
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            return None

        name = data.get("name", path.stem)

        # Parse weights
        weights_raw = data.get("weights", {})
        weights_l: dict[str, float] = {}
        for key, val in weights_raw.items():
            l_key = key if key.startswith("L") else _DIM_TO_L.get(key, key)
            weights_l[l_key] = float(val)
        if not weights_l:
            # Check for parent tradition and inherit weights
            parent = data.get("parent", "")
            if parent:
                _ensure_loaded()
                parent_tc = _traditions.get(parent)
                if parent_tc:
                    weights_l = dict(parent_tc.weights_l)
            if not weights_l:
                weights_l = dict(_DEFAULT_WEIGHTS)

        # Apply override_weights on top
        override_raw = data.get("override_weights", {})
        for key, val in override_raw.items():
            l_key = key if key.startswith("L") else _DIM_TO_L.get(key, key)
            weights_l[l_key] = float(val)

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

        # Inherit parent terminology if specified
        parent_name = data.get("parent", "")
        if parent_name:
            _ensure_loaded()
            parent_tc = _traditions.get(parent_name)
            if parent_tc:
                terms = list(parent_tc.terminology) + terms

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

        # Inherit parent taboos, minus removals
        taboos_remove = set(data.get("taboos_remove", []))
        if parent_name:
            _ensure_loaded()
            parent_tc = _traditions.get(parent_name)
            if parent_tc:
                inherited_taboos = [
                    tb for tb in parent_tc.taboos
                    if tb.rule not in taboos_remove
                ]
                taboos = inherited_taboos + taboos

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

        return TraditionConfig(
            name=name,
            display_name=display_name,
            weights_l=weights_l,
            terminology=terms,
            taboos=taboos,
            pipeline=pipeline,
            examples=data.get("examples", []),
            extra_dimensions=data.get("extra_dimensions", []),
            layerability=data.get("layerability") or "split",
            canvas_color=data.get("canvas_color") or "#ffffff",
            canvas_description=data.get("canvas_description") or "",
            key_strategy=data.get("key_strategy") or "luminance",
            style_keywords=data.get("style_keywords") or "",
        )
    except Exception as exc:
        logger.warning("Failed to load custom tradition %s: %s", path, exc)
        return None


def get_tradition(name: str) -> TraditionConfig | None:
    """Get a single tradition config by name or file path.

    If *name* ends with ``.yaml`` or contains a path separator, it is
    treated as a file path to a custom tradition YAML.
    """
    # Custom YAML file path
    if name.endswith(".yaml") or name.endswith(".yml") or os.sep in name or "/" in name:
        return _load_single_yaml(Path(name))

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


def _get_evolved_context_dir() -> Path:
    """Resolve the canonical directory for evolved_context.json.

    Priority:
    1. Module-level ``_EVOLVED_CONTEXT_DIR`` (set via monkeypatch in tests)
    2. ``VULCA_DATA_DIR`` environment variable
    3. ``~/.vulca/data`` (default)
    """
    if _EVOLVED_CONTEXT_DIR is not None:
        return _EVOLVED_CONTEXT_DIR
    env_dir = os.environ.get("VULCA_DATA_DIR")
    if env_dir:
        return Path(env_dir)
    return Path.home() / ".vulca" / "data"


def _load_evolved_weights(tradition: str) -> dict[str, float] | None:
    """Try to load evolved weights from evolved_context.json.

    Returns L1-L5 keyed dict, or None if unavailable.
    The evolution system stores weights with full dimension names
    (visual_perception, etc.) -- convert to L1-L5 format.

    Reads from a single canonical path:
    ``_get_evolved_context_dir() / "evolved_context.json"``
    which can be overridden via VULCA_DATA_DIR env or VULCA_EVOLVED_CONTEXT env.
    """
    try:
        import json

        # Single canonical path (+ optional explicit override)
        env_explicit = os.environ.get("VULCA_EVOLVED_CONTEXT")
        if env_explicit:
            path = Path(env_explicit)
        else:
            path = _get_evolved_context_dir() / "evolved_context.json"

        if not path.is_file():
            return None

        with open(path, "r", encoding="utf-8") as f:
            ctx = json.load(f)
        tw = ctx.get("tradition_weights", {}).get(tradition)
        if not tw:
            return None
        # Convert full names -> L1-L5
        result: dict[str, float] = {}
        for full_name, val in tw.items():
            l_key = _DIM_TO_L.get(full_name)
            if l_key:
                result[l_key] = float(val)
        if len(result) == 5:
            return result
        return None
    except Exception:
        logger.debug("Failed to load evolved weights for %s", tradition)
        return None


def get_weights(tradition: str) -> dict[str, float]:
    """Get L1-L5 weights for a tradition.

    Priority: evolved_context.json > YAML config > hardcoded > default.
    """
    # 1. Evolved weights (from self-evolution system)
    evolved = _load_evolved_weights(tradition)
    if evolved:
        return evolved

    # 2. YAML config
    _ensure_loaded()
    tc = _traditions.get(tradition)
    if tc:
        return dict(tc.weights_l)

    # 3. Hardcoded fallback
    from vulca.cultural import TRADITION_WEIGHTS
    return dict(TRADITION_WEIGHTS.get(tradition, _DEFAULT_WEIGHTS))


def get_all_weight_tables() -> dict[str, dict[str, float]]:
    """Get weight tables for all traditions."""
    _ensure_loaded()
    if _traditions:
        return {name: dict(tc.weights_l) for name, tc in _traditions.items()}
    from vulca.cultural import TRADITION_WEIGHTS
    return dict(TRADITION_WEIGHTS)


def get_tradition_guide(tradition: str) -> dict | None:
    """Get full cultural guide for a tradition (for MCP/CLI).

    Returns dict with weights, evolved_weights, terminology, taboos, description.
    Returns None if tradition not found.
    """
    _ensure_loaded()
    tc = _traditions.get(tradition)
    if tc is None:
        return None

    evolved = _load_evolved_weights(tradition)

    # Count sessions from evolved context (unified path)
    sessions_count = 0
    try:
        import json as _json
        env_explicit = os.environ.get("VULCA_EVOLVED_CONTEXT")
        if env_explicit:
            ctx_path = Path(env_explicit)
        else:
            ctx_path = _get_evolved_context_dir() / "evolved_context.json"
        if ctx_path.is_file():
            with open(ctx_path, "r", encoding="utf-8") as f:
                ctx = _json.load(f)
            sessions_count = ctx.get("total_sessions", 0)
    except Exception:
        logger.debug("Failed to load sessions count for tradition guide")

    # Build terminology list
    terms = []
    for t in tc.terminology:
        entry: dict = {"term": t.term, "definition": t.definition}
        if t.term_zh:
            entry["translation"] = t.term_zh
        terms.append(entry)

    # Build taboos list
    taboos = [tb.rule for tb in tc.taboos if tb.rule]

    # Description from display name
    desc = tc.display_name.get("en", tradition.replace("_", " ").title())

    # Emphasis (highest weighted dimension)
    dim_names = {"L1": "Visual", "L2": "Technical", "L3": "Cultural", "L4": "Critical", "L5": "Philosophical"}
    emphasis_dim = max(tc.weights_l, key=tc.weights_l.get) if tc.weights_l else "L3"
    emphasis = dim_names.get(emphasis_dim, emphasis_dim)

    return {
        "tradition": tradition,
        "description": desc,
        "emphasis": emphasis,
        "weights": dict(tc.weights_l),
        "evolved_weights": evolved,
        "sessions_count": sessions_count,
        "terminology": terms,
        "taboos": taboos,
    }
