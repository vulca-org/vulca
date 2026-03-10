"""PromptDistiller — extract prompt patterns from high-scoring sessions.

Two modes:
- **LLM mode** (API key available): Uses Gemini to analyze session clusters
  and produce rich archetypes with insights, evaluation guidance, and
  anti-patterns.  This is the MemRL core — "frozen model + evolving context".
- **Keyword mode** (fallback): Simple keyword frequency counting.
  Always available, no external dependencies.

The ``distill()`` method auto-selects the best available mode.
"""

from __future__ import annotations

import json
import logging
import re
from collections import Counter
from dataclasses import dataclass, field

logger = logging.getLogger("vulca")

_SCORE_THRESHOLD = 0.70  # Only learn from sessions scoring above this
_LLM_TIMEOUT_S = 60


@dataclass
class PromptArchetype:
    """A distilled prompt pattern from high-scoring sessions."""

    pattern: str
    avg_score: float = 0.0
    count: int = 0
    traditions: list[str] = field(default_factory=list)
    example_prompts: list[str] = field(default_factory=list)
    # LLM-enriched fields (empty when using keyword fallback)
    insights: str = ""
    evaluation_guidance: dict[str, str] = field(default_factory=dict)  # L1-L5 → guidance
    anti_patterns: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d: dict = {
            "pattern": self.pattern,
            "avg_score": round(self.avg_score, 4),
            "count": self.count,
            "traditions": self.traditions,
            "example_prompts": self.example_prompts[:3],
        }
        if self.insights:
            d["insights"] = self.insights
        if self.evaluation_guidance:
            d["evaluation_guidance"] = self.evaluation_guidance
        if self.anti_patterns:
            d["anti_patterns"] = self.anti_patterns
        return d


# ---------------------------------------------------------------------------
# LLM analysis prompt
# ---------------------------------------------------------------------------

_DISTILL_SYSTEM = """\
You are a cultural art analysis expert for the VULCA evaluation system.
Analyze high-scoring art creation sessions and distill reusable prompt archetypes.

For each archetype you identify, provide:
1. **pattern**: A concise thematic label (e.g. "ink wash landscape", "zen minimalism")
2. **insights**: What makes this pattern successful — cultural resonance, technique, composition
3. **evaluation_guidance**: Per-dimension (L1-L5) guidance for evaluating works in this pattern
   - L1 (visual_perception): What visual qualities to look for
   - L2 (technical_analysis): What technical elements matter
   - L3 (cultural_context): What cultural references are important
   - L4 (critical_interpretation): What interpretive depth to expect
   - L5 (philosophical_aesthetic): What philosophical dimensions are relevant
4. **anti_patterns**: Common mistakes or pitfalls to avoid

Return valid JSON: an array of archetype objects. Maximum 10 archetypes.
Each object must have: pattern (str), insights (str), evaluation_guidance (dict with L1-L5 keys), anti_patterns (list[str]).
Output ONLY the JSON array, no markdown fences or explanation."""

_DISTILL_USER = """\
Tradition: {tradition}
High-scoring sessions ({count} total, avg score {avg_score:.2f}):

{session_summaries}

Identify the most significant prompt archetypes from these sessions.\
"""


class PromptDistiller:
    """Extract prompt archetypes from high-scoring sessions.

    Auto-selects LLM-powered analysis when an API key is available,
    falling back to keyword frequency counting otherwise.
    """

    def __init__(self, score_threshold: float = _SCORE_THRESHOLD) -> None:
        self._threshold = score_threshold

    def distill(self, sessions: list[dict]) -> list[PromptArchetype]:
        """Analyze sessions and extract common prompt patterns.

        Auto-selects LLM or keyword mode based on API key availability.

        Parameters
        ----------
        sessions : list[dict]
            Session dicts with 'intent', 'final_weighted_total', 'tradition'.

        Returns
        -------
        list[PromptArchetype]
            Distilled prompt patterns sorted by relevance.
        """
        high_scoring = [
            s for s in sessions
            if s.get("final_weighted_total", 0) >= self._threshold
            and s.get("intent")
        ]
        if not high_scoring:
            return []

        # Try LLM mode first
        if self._has_api_key():
            try:
                archetypes = self._distill_llm(high_scoring)
                if archetypes:
                    logger.info(
                        "PromptDistiller(LLM): %d high-scoring sessions → %d archetypes",
                        len(high_scoring), len(archetypes),
                    )
                    return archetypes
            except Exception as exc:
                logger.warning("PromptDistiller: LLM analysis failed (%s), falling back to keywords", exc)

        # Keyword fallback
        return self._distill_keywords(high_scoring)

    # ------------------------------------------------------------------
    # LLM-powered distillation
    # ------------------------------------------------------------------

    @staticmethod
    def _has_api_key() -> bool:
        """Check if an LLM API key is available."""
        from app.prototype.digestion.llm_utils import has_llm_api_key

        return has_llm_api_key()

    def _distill_llm(self, high_scoring: list[dict]) -> list[PromptArchetype]:
        """Use LLM to analyze high-scoring sessions and produce rich archetypes."""
        import litellm
        from app.prototype.agents.model_router import MODEL_FAST

        # Group sessions by tradition for focused analysis
        by_tradition: dict[str, list[dict]] = {}
        for s in high_scoring:
            t = s.get("tradition", "default")
            by_tradition.setdefault(t, []).append(s)

        all_archetypes: list[PromptArchetype] = []

        for tradition, sess_list in by_tradition.items():
            # Build session summary for the LLM
            summaries: list[str] = []
            for s in sess_list[:15]:  # Cap at 15 to fit context
                intent = s.get("intent", "")
                score = s.get("final_weighted_total", 0)
                scores = s.get("final_scores", {})
                scores_str = ", ".join(f"{k}={v:.2f}" for k, v in scores.items()) if scores else "N/A"
                summaries.append(f"- Intent: \"{intent}\" | Score: {score:.2f} | Dimensions: {scores_str}")

            avg_score = sum(s.get("final_weighted_total", 0) for s in sess_list) / len(sess_list)
            user_msg = _DISTILL_USER.format(
                tradition=tradition.replace("_", " "),
                count=len(sess_list),
                avg_score=avg_score,
                session_summaries="\n".join(summaries),
            )

            try:
                response = litellm.completion(
                    model=MODEL_FAST,
                    messages=[
                        {"role": "system", "content": _DISTILL_SYSTEM},
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=0.3,
                    max_tokens=4096,
                    timeout=_LLM_TIMEOUT_S,
                )

                content = response.choices[0].message.content or ""
                archetypes = self._parse_llm_response(content, tradition, sess_list)
                all_archetypes.extend(archetypes)
            except Exception as exc:
                logger.debug("PromptDistiller: LLM failed for tradition %s: %s", tradition, exc)

        # Sort by avg_score descending
        all_archetypes.sort(key=lambda a: a.avg_score, reverse=True)
        return all_archetypes[:20]

    def _parse_llm_response(
        self,
        content: str,
        tradition: str,
        sess_list: list[dict],
    ) -> list[PromptArchetype]:
        """Parse LLM JSON response into PromptArchetype objects."""
        from app.prototype.digestion.llm_utils import strip_markdown_fences

        text = strip_markdown_fences(content)

        try:
            items = json.loads(text)
        except json.JSONDecodeError:
            logger.debug("PromptDistiller: failed to parse LLM JSON: %s", text[:200])
            return []

        if not isinstance(items, list):
            return []

        avg_score = sum(s.get("final_weighted_total", 0) for s in sess_list) / max(len(sess_list), 1)
        examples = [s.get("intent", "") for s in sess_list[:3]]

        archetypes: list[PromptArchetype] = []
        for item in items[:10]:
            if not isinstance(item, dict):
                continue
            pattern = item.get("pattern", "").strip()
            if not pattern:
                continue

            # Normalize evaluation_guidance keys
            guidance_raw = item.get("evaluation_guidance", {})
            guidance: dict[str, str] = {}
            if isinstance(guidance_raw, dict):
                for k, v in guidance_raw.items():
                    if isinstance(v, str) and v.strip():
                        guidance[k] = v.strip()

            anti_patterns = item.get("anti_patterns", [])
            if not isinstance(anti_patterns, list):
                anti_patterns = []
            anti_patterns = [str(a) for a in anti_patterns if a]

            archetypes.append(PromptArchetype(
                pattern=pattern,
                avg_score=avg_score,
                count=len(sess_list),
                traditions=[tradition],
                example_prompts=examples,
                insights=str(item.get("insights", "")).strip(),
                evaluation_guidance=guidance,
                anti_patterns=anti_patterns[:5],
            ))

        return archetypes

    # ------------------------------------------------------------------
    # Keyword-based fallback (original implementation)
    # ------------------------------------------------------------------

    def _distill_keywords(self, high_scoring: list[dict]) -> list[PromptArchetype]:
        """Fallback: extract archetypes from keyword frequency analysis."""
        keyword_sessions: dict[str, list[dict]] = {}
        for s in high_scoring:
            intent = s.get("intent", "")
            keywords = self._extract_keywords(intent)
            for kw in keywords:
                keyword_sessions.setdefault(kw, []).append(s)

        archetypes: list[PromptArchetype] = []
        for kw, sess_list in keyword_sessions.items():
            if len(sess_list) < 2:
                continue  # Need at least 2 occurrences

            avg_score = sum(s.get("final_weighted_total", 0) for s in sess_list) / len(sess_list)
            traditions = list({s.get("tradition", "default") for s in sess_list})
            examples = [s.get("intent", "") for s in sess_list[:3]]

            archetypes.append(PromptArchetype(
                pattern=kw,
                avg_score=avg_score,
                count=len(sess_list),
                traditions=traditions,
                example_prompts=examples,
            ))

        archetypes.sort(key=lambda a: a.count, reverse=True)
        logger.info("PromptDistiller(keywords): %d high-scoring sessions → %d archetypes", len(high_scoring), len(archetypes))
        return archetypes[:20]

    @staticmethod
    def _extract_keywords(text: str) -> list[str]:
        """Extract meaningful keywords from intent text (English + Chinese)."""
        stop_words = {
            "a", "an", "the", "in", "on", "at", "to", "for", "of", "with",
            "and", "or", "but", "is", "are", "was", "were", "be", "been",
            "this", "that", "it", "its", "my", "your", "his", "her",
        }
        # English words
        en_words = re.findall(r'[a-z]+', text.lower())
        en_words = [w for w in en_words if len(w) >= 3 and w not in stop_words]
        # Chinese bigrams/trigrams (CJK Unified Ideographs)
        zh_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
        return (en_words + zh_words)[:20]
