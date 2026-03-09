"""ConceptCrystallizer — crystallize emerged cultural concepts from clusters.

When a cluster reaches a size threshold, uses LLM to name and describe
the emerged cultural concept. Falls back to rule-based naming if LLM unavailable.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

from app.prototype.agents.model_router import MODEL_FAST

logger = logging.getLogger("vulca")

_MIN_CLUSTER_SIZE = 3  # Minimum sessions to crystallize a concept


@dataclass
class CulturalConcept:
    """A crystallized cultural concept that emerged from user sessions."""

    name: str
    description: str = ""
    key_principles: list[str] = field(default_factory=list)
    l_focus: dict[str, float] = field(default_factory=dict)  # L1-L5 emphasis
    weights: dict[str, float] = field(default_factory=dict)
    reference_sessions: list[str] = field(default_factory=list)
    emerged_at: float = field(default_factory=time.time)
    confidence: float = 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "key_principles": self.key_principles,
            "l_focus": self.l_focus,
            "weights": self.weights,
            "reference_sessions": self.reference_sessions[:10],
            "emerged_at": self.emerged_at,
            "confidence": round(self.confidence, 4),
        }


class ConceptCrystallizer:
    """Crystallize cultural concepts from large enough clusters."""

    def __init__(self, min_cluster_size: int = _MIN_CLUSTER_SIZE) -> None:
        self._min_size = min_cluster_size

    def crystallize(
        self,
        clusters: list,  # list[CulturalCluster]
        sessions: list[dict],
    ) -> list[CulturalConcept]:
        """Crystallize concepts from clusters that meet the size threshold.

        Parameters
        ----------
        clusters : list[CulturalCluster]
            Clusters from CulturalClusterer.
        sessions : list[dict]
            Full session data for enrichment.

        Returns
        -------
        list[CulturalConcept]
            Crystallized cultural concepts.
        """
        concepts: list[CulturalConcept] = []

        for cluster in clusters:
            if cluster.size < self._min_size:
                continue

            # Try LLM crystallization first, fall back to rule-based
            concept = self._try_llm_crystallize(cluster, sessions)
            if concept is None:
                concept = self._rule_based_crystallize(cluster, sessions)

            if concept is not None:
                concepts.append(concept)

        logger.info(
            "ConceptCrystallizer: %d clusters → %d concepts (threshold=%d)",
            len(clusters), len(concepts), self._min_size,
        )
        return concepts

    def _try_llm_crystallize(self, cluster, sessions: list[dict]) -> CulturalConcept | None:
        """Use LLM to name and describe the emerged concept."""
        try:
            import json
            import litellm

            # Build context from cluster
            cluster_sessions = [
                s for s in sessions
                if s.get("session_id") in set(cluster.session_ids)
            ]
            intents = [s.get("intent", "") for s in cluster_sessions[:5]]
            traditions = list({s.get("tradition", "") for s in cluster_sessions})

            prompt = (
                "Based on these art creation sessions, identify the emerged cultural concept:\n"
                f"- Tradition: {cluster.tradition}\n"
                f"- Related traditions: {', '.join(traditions)}\n"
                f"- Sample intents: {'; '.join(intents[:5])}\n"
                f"- Feature centroid: {cluster.feature_centroid}\n\n"
                "Respond ONLY with valid JSON:\n"
                '{"name": "concept_name_snake_case", "description": "brief description", '
                '"key_principles": ["principle1", "principle2"], '
                '"l_focus": {"L1": 0.X, "L3": 0.X, "L5": 0.X}}'
            )

            response = litellm.completion(
                model=MODEL_FAST,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3,
                timeout=15,
            )

            text = response.choices[0].message.content or ""
            # Parse JSON
            brace_start = text.find("{")
            brace_end = text.rfind("}")
            if brace_start != -1 and brace_end > brace_start:
                parsed = json.loads(text[brace_start:brace_end + 1])
                return CulturalConcept(
                    name=parsed.get("name", f"concept_{cluster.cluster_id}"),
                    description=parsed.get("description", ""),
                    key_principles=parsed.get("key_principles", []),
                    l_focus=parsed.get("l_focus", {}),
                    weights=dict(cluster.feature_centroid),
                    reference_sessions=cluster.session_ids[:10],
                    confidence=min(1.0, cluster.size / 20),
                )
        except Exception:
            logger.debug("LLM crystallization failed for cluster %s", cluster.cluster_id)
        return None

    def _rule_based_crystallize(self, cluster, sessions: list[dict]) -> CulturalConcept:
        """Rule-based fallback: name from tradition + dominant features."""
        # Derive name from tradition and dominant feature
        dominant_feature = ""
        max_val = 0.0
        for k, v in cluster.feature_centroid.items():
            if v > max_val:
                max_val = v
                dominant_feature = k

        name = f"{cluster.tradition}_{dominant_feature}" if dominant_feature else f"concept_{cluster.cluster_id}"

        return CulturalConcept(
            name=name,
            description=f"Emerged from {cluster.size} sessions in {cluster.tradition} tradition",
            key_principles=[f"High {dominant_feature}"] if dominant_feature else [],
            l_focus=dict(cluster.feature_centroid),
            weights=dict(cluster.feature_centroid),
            reference_sessions=cluster.session_ids[:10],
            confidence=min(1.0, cluster.size / 20),
        )
