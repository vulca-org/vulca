"""Risk tagging engine for the Critic Agent."""

from __future__ import annotations

from app.prototype.agents.critic_rules import _CULTURE_KEYWORDS

__all__ = [
    "RiskTagger",
]


class RiskTagger:
    """Deterministic risk tagger based on evidence and candidate metadata."""

    def tag(
        self,
        candidate: dict,
        evidence: dict,
        cultural_tradition: str,
    ) -> list[tuple[str, str]]:
        """Return list of (tag_name, severity) tuples."""
        tags: list[tuple[str, str]] = []
        prompt_lower = candidate.get("prompt", "").lower()

        taboo_violations = evidence.get("taboo_violations", [])
        term_hits = evidence.get("terminology_hits", [])
        sample_matches = evidence.get("sample_matches", [])

        # taboo_critical: evidence contains severity=critical taboo violation
        if any(v.get("severity") == "critical" for v in taboo_violations):
            tags.append(("taboo_critical", "critical"))

        # taboo_high: evidence contains severity=high taboo violation
        if any(v.get("severity") == "high" for v in taboo_violations):
            tags.append(("taboo_high", "high"))

        # low_evidence_coverage: no sample matches AND no terminology hits
        if len(sample_matches) == 0 and len(term_hits) == 0:
            tags.append(("low_evidence_coverage", "medium"))

        # no_terminology_match: no terminology hits
        if len(term_hits) == 0:
            tags.append(("no_terminology_match", "low"))

        # style_mismatch: prompt lacks tradition-specific style keywords
        style_keywords = _CULTURE_KEYWORDS.get(
            cultural_tradition, _CULTURE_KEYWORDS["default"]
        )
        if not any(kw in prompt_lower for kw in style_keywords):
            tags.append(("style_mismatch", "medium"))

        return tags
