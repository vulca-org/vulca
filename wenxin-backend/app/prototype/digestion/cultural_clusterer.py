"""CulturalClusterer — cluster sessions by cultural features using cosine similarity.

Uses pure Python + math stdlib (no scipy/sklearn dependency).

Supports two clustering modes:
- **Intra-tradition** (Mode 1): clusters within each tradition to find sub-styles.
- **Cross-tradition** (Mode 2): clusters across all traditions to discover
  emergent cultural patterns that span multiple traditions.
"""

from __future__ import annotations

import logging
import math
from collections import defaultdict
from dataclasses import dataclass, field

logger = logging.getLogger("vulca")

# Minimum number of sessions required to attempt cross-tradition clustering.
_MIN_CROSS_SESSIONS = 4


@dataclass
class CulturalCluster:
    """A cluster of sessions with similar cultural features."""

    cluster_id: str = ""
    feature_centroid: dict[str, float] = field(default_factory=dict)
    session_ids: list[str] = field(default_factory=list)
    size: int = 0
    tradition: str = ""
    # --- Cross-tradition metadata ---
    source: str = "intra_tradition"  # "intra_tradition" | "cross_tradition"
    traditions: list[str] = field(default_factory=list)
    # --- Incremental centroid tracking (O(1) update instead of O(n) rescan) ---
    _feature_sums: dict[str, float] = field(default_factory=dict, repr=False)

    def add_session(self, sid: str, features: dict[str, float]) -> None:
        """Add a session and update centroid incrementally in O(d) time."""
        self.session_ids.append(sid)
        self.size += 1
        # Accumulate feature sums
        for k, v in features.items():
            self._feature_sums[k] = self._feature_sums.get(k, 0.0) + v
        # Recompute centroid from sums (O(d) where d = number of features)
        self.feature_centroid = {
            k: round(s / self.size, 4) for k, s in self._feature_sums.items()
        }

    def to_dict(self) -> dict:
        d = {
            "cluster_id": self.cluster_id,
            "feature_centroid": self.feature_centroid,
            "session_ids": self.session_ids,
            "size": self.size,
            "tradition": self.tradition,
            "source": self.source,
        }
        if self.traditions:
            d["traditions"] = self.traditions
        return d


def _cosine_similarity(a: dict[str, float], b: dict[str, float]) -> float:
    """Cosine similarity between two feature dicts."""
    keys = set(a.keys()) | set(b.keys())
    if not keys:
        return 0.0
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    norm_a = math.sqrt(sum(a.get(k, 0.0) ** 2 for k in keys))
    norm_b = math.sqrt(sum(b.get(k, 0.0) ** 2 for k in keys))
    if norm_a < 1e-8 or norm_b < 1e-8:
        return 0.0
    return dot / (norm_a * norm_b)


def _compute_centroid(features_list: list[dict[str, float]]) -> dict[str, float]:
    """Compute the centroid (mean) of a list of feature dicts."""
    if not features_list:
        return {}
    all_keys = set()
    for f in features_list:
        all_keys.update(f.keys())
    centroid: dict[str, float] = {}
    n = len(features_list)
    for k in all_keys:
        centroid[k] = round(sum(f.get(k, 0.0) for f in features_list) / n, 4)
    return centroid


def _numeric_features(features: dict) -> dict[str, float]:
    """Extract only numeric-valued keys from a features dict.

    Tier-2 LLM features (lists/strings) are excluded so clustering
    operates purely on the numeric Tier-1 feature space.
    """
    return {k: v for k, v in features.items() if isinstance(v, (int, float))}


class CulturalClusterer:
    """Cluster sessions by cultural features using greedy centroid-based clustering.

    Dual-mode clustering:
      * **Mode 1 (intra-tradition)** — groups sessions *within* each tradition
        to discover sub-styles (e.g., bold vs. subtle within *chinese_xieyi*).
      * **Mode 2 (cross-tradition)** — groups *all* sessions together,
        regardless of tradition label, to discover emergent cultural patterns
        that span multiple traditions (e.g., "minimalist expressionism" shared
        by *chinese_xieyi* and *japanese_wabi_sabi*).
    """

    def __init__(
        self,
        similarity_threshold: float = 0.72,
        min_cross_sessions: int = _MIN_CROSS_SESSIONS,
    ) -> None:
        self._threshold = similarity_threshold
        self._min_cross_sessions = min_cross_sessions

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def cluster(self, sessions: list[dict]) -> list[CulturalCluster]:
        """Cluster sessions by their cultural_features vectors.

        Parameters
        ----------
        sessions : list[dict]
            Session dicts (must have 'cultural_features' and 'session_id' keys).

        Returns
        -------
        list[CulturalCluster]
            Clusters from both intra- and cross-tradition modes.
        """
        # Filter sessions that have valid cultural features
        valid = [
            s for s in sessions
            if s.get("cultural_features") and isinstance(s["cultural_features"], dict)
        ]
        if not valid:
            return []

        results: list[CulturalCluster] = []

        # --- Mode 1: intra-tradition clustering ---
        groups: dict[str, list[dict]] = defaultdict(list)
        for s in valid:
            groups[s.get("tradition", "default")].append(s)

        intra_counter = 0
        for tradition, group_sessions in groups.items():
            intra_clusters = self._cluster_by_features(
                group_sessions,
                id_prefix=f"intra-{intra_counter:03d}",
            )
            for c in intra_clusters:
                c.source = "intra_tradition"
                c.tradition = tradition
            intra_counter += len(intra_clusters)
            results.extend(intra_clusters)

        # --- Mode 2: cross-tradition clustering ---
        if len(valid) >= self._min_cross_sessions:
            cross_clusters = self._cluster_by_features(
                valid,
                id_prefix="cross",
            )
            for c in cross_clusters:
                # Determine which traditions are represented in this cluster
                sid_set = set(c.session_ids)
                traditions_in_cluster = sorted({
                    s.get("tradition", "default")
                    for s in valid
                    if s.get("session_id", "") in sid_set
                })
                # Only keep clusters that span >= 2 traditions
                if len(traditions_in_cluster) >= 2:
                    c.source = "cross_tradition"
                    c.traditions = traditions_in_cluster
                    c.tradition = "+".join(traditions_in_cluster)
                    results.append(c)

        logger.info(
            "CulturalClusterer: %d sessions → %d clusters "
            "(intra=%d, cross=%d)",
            len(valid),
            len(results),
            sum(1 for c in results if c.source == "intra_tradition"),
            sum(1 for c in results if c.source == "cross_tradition"),
        )
        return results

    # ------------------------------------------------------------------
    # Internal: greedy centroid-based clustering on feature vectors
    # ------------------------------------------------------------------

    def _cluster_by_features(
        self,
        sessions: list[dict],
        *,
        id_prefix: str = "cluster",
    ) -> list[CulturalCluster]:
        """Greedy centroid-based clustering on numeric cultural feature vectors.

        Parameters
        ----------
        sessions : list[dict]
            Sessions to cluster (must have 'cultural_features').
        id_prefix : str
            Prefix for generated cluster IDs.

        Returns
        -------
        list[CulturalCluster]
            Resulting clusters (source/tradition filled by caller).
        """
        clusters: list[CulturalCluster] = []
        assigned: set[str] = set()

        for session in sessions:
            sid = session.get("session_id", "")
            if sid in assigned:
                continue

            features = _numeric_features(session["cultural_features"])
            if not features:
                continue

            # Try to join an existing cluster
            best_cluster: CulturalCluster | None = None
            best_sim = -1.0
            for cluster in clusters:
                sim = _cosine_similarity(features, cluster.feature_centroid)
                if sim > self._threshold and sim > best_sim:
                    best_cluster = cluster
                    best_sim = sim

            if best_cluster is not None:
                # O(d) incremental centroid update instead of O(n) full rescan
                best_cluster.add_session(sid, features)
            else:
                cluster_id = f"{id_prefix}-{len(clusters):03d}"
                clusters.append(CulturalCluster(
                    cluster_id=cluster_id,
                    feature_centroid=dict(features),
                    session_ids=[sid],
                    size=1,
                    tradition=session.get("tradition", "default"),
                    _feature_sums=dict(features),
                ))
            assigned.add(sid)

        return clusters
