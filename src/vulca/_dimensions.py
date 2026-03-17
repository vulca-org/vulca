"""L1-L5 dimension name normalization and bidirectional mapping.

Provides canonical mapping between short names (L1-L5) and full descriptive names,
plus utilities for converting between various naming formats (snake_case, camelCase, spaced).
"""

from __future__ import annotations

# Canonical L1-L5 definitions
DIMENSION_NAMES: dict[str, str] = {
    "L1": "Visual Perception",
    "L2": "Technical Execution",
    "L3": "Cultural Context",
    "L4": "Critical Interpretation",
    "L5": "Philosophical Aesthetics",
}

# Reverse mapping: full name -> L-code
_FULL_TO_CODE: dict[str, str] = {v.lower(): k for k, v in DIMENSION_NAMES.items()}

# Snake case variants — includes both paper names and prototype names
_SNAKE_TO_CODE: dict[str, str] = {
    # Paper terminology (VULCA-Bench / EMNLP 2025)
    "visual_perception": "L1",
    "technical_execution": "L2",
    "cultural_context": "L3",
    "critical_interpretation": "L4",
    "philosophical_aesthetics": "L5",
    # Prototype terminology (wenxin-backend)
    "technical_analysis": "L2",
    "philosophical_aesthetic": "L5",
}


def to_code(name: str) -> str:
    """Convert any dimension name format to L-code (L1-L5).

    Accepts: "L1", "Visual Perception", "visual_perception", "VisualPerception"
    Returns: "L1" (or the original string if unrecognized)
    """
    # Already an L-code
    if name in DIMENSION_NAMES:
        return name

    # Full name match (case-insensitive)
    lower = name.lower().strip()
    if lower in _FULL_TO_CODE:
        return _FULL_TO_CODE[lower]

    # Snake case match
    if lower in _SNAKE_TO_CODE:
        return _SNAKE_TO_CODE[lower]

    # CamelCase -> spaced -> try again
    import re
    spaced = re.sub(r"([a-z])([A-Z])", r"\1 \2", name).lower()
    if spaced in _FULL_TO_CODE:
        return _FULL_TO_CODE[spaced]

    return name


def to_full_name(code: str) -> str:
    """Convert L-code to full descriptive name.

    "L1" -> "Visual Perception"
    """
    return DIMENSION_NAMES.get(code, code)


def to_snake(code: str) -> str:
    """Convert L-code to snake_case name.

    "L1" -> "visual_perception"
    """
    full = DIMENSION_NAMES.get(code, code)
    return full.lower().replace(" ", "_")


def all_codes() -> list[str]:
    """Return all L-codes: ["L1", "L2", "L3", "L4", "L5"]."""
    return list(DIMENSION_NAMES.keys())
