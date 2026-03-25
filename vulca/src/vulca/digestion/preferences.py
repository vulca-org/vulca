"""SessionPreferences — Layer 1 real-time preference accumulation.

Accumulates per-action signals during a session into a preference profile
that can be injected into generation/evaluation prompts.
"""
from __future__ import annotations

from typing import Any

# L-dimension labels for prompt hints
_L_LABELS = {
    "L1": "Visual Perception (composition, layout, color harmony)",
    "L2": "Technical Execution (rendering quality, detail, craftsmanship)",
    "L3": "Cultural/Style Context (tradition fidelity, motifs)",
    "L4": "Interpretation & Constraints (narrative, symbols)",
    "L5": "Philosophical & Emotional Aesthetics (mood, atmosphere)",
}


class SessionPreferences:
    """In-memory preference accumulator for a single session.

    Updated by per-action signals. Influences prompt construction.
    """

    def __init__(self) -> None:
        self.preferences: dict[str, Any] = {}
        self.confidence: dict[str, float] = {}

    def get(self, key: str, default: Any = None) -> Any:
        return self.preferences.get(key, default)

    def update_from_signal(self, signal: dict[str, Any]) -> None:
        """Update preferences from a single action signal."""
        action = signal.get("action", "")

        if action == "concept_select":
            idx = signal.get("concept_index", -1)
            total = signal.get("total_candidates", 0)
            if total > 0 and idx >= 0:
                self._set("concept_position_preference", round(idx / max(total - 1, 1), 2))
            self._set("prefers_notes", signal.get("had_notes", False))

        elif action == "evaluate":
            if signal.get("weakest"):
                self._set("weak_dimension", signal["weakest"])
            if signal.get("strongest"):
                self._set("strong_dimension", signal["strongest"])

        elif action == "nl_update":
            fields = signal.get("fields_changed", [])
            freq = self.preferences.get("frequently_changed", {})
            for f in fields:
                freq[f] = freq.get(f, 0) + 1
            self.preferences["frequently_changed"] = freq

    def _set(self, key: str, value: Any) -> None:
        """Set a preference and bump its confidence."""
        self.preferences[key] = value
        self.confidence[key] = min(1.0, self.confidence.get(key, 0.0) + 0.3)

    def to_prompt_hints(self) -> list[str]:
        """Generate prompt hints from accumulated preferences."""
        hints: list[str] = []

        weak = self.preferences.get("weak_dimension")
        if weak and weak in _L_LABELS:
            hints.append(
                f"Pay special attention to {weak} ({_L_LABELS[weak]}) — "
                f"this dimension has been consistently weak."
            )

        strong = self.preferences.get("strong_dimension")
        if strong and strong in _L_LABELS:
            hints.append(f"Maintain strength in {strong} ({_L_LABELS[strong]}).")

        freq = self.preferences.get("frequently_changed", {})
        if freq:
            most_changed = max(freq, key=freq.get)
            hints.append(f"User frequently adjusts '{most_changed}' — ensure this aspect is prominent.")

        return hints
