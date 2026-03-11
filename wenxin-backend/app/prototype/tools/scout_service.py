"""ScoutService — aggregates SampleMatcher + TerminologyLoader + TabooRuleEngine.

Phase B addition: optional FAISS semantic search via ``search_mode`` parameter,
plus ``compute_evidence_coverage()`` for LayerState integration.

Layer 1a addition: ``build_evidence_pack()`` constructs a structured EvidencePack
from gathered evidence, enabling Draft to build precise prompts.

Layer 1c addition: ``gather_supplementary()`` performs targeted re-retrieval
based on Critic feedback (NeedMoreEvidence).
"""

from __future__ import annotations

import copy
import json
import logging
from pathlib import Path

from app.prototype.tools.evidence_pack import (
    CompositionReference,
    EvidencePack,
    StyleConstraint,
    TabooConstraint,
    TerminologyAnchor,
)
from app.prototype.tools.sample_matcher import SampleMatcher
from app.prototype.tools.scout_types import ScoutEvidence
from app.prototype.tools.taboo_rule_engine import TabooRuleEngine
from app.prototype.tools.terminology_loader import TerminologyLoader

logger = logging.getLogger(__name__)


class ScoutService:
    """Gather evidence from all Scout tools and return a unified ScoutEvidence.

    Parameters
    ----------
    search_mode : str
        ``"auto"`` (default) — use FAISS if available, else keyword/string.
        ``"jaccard"`` — force keyword-only (sample) + string-only (term).
        ``"semantic"`` — force FAISS (raises if unavailable).
    """

    def __init__(self, search_mode: str = "auto") -> None:
        self._search_mode = search_mode
        self._faiss_service = None

        # Attempt to create FaissIndexService if mode allows
        if search_mode in ("auto", "semantic"):
            try:
                from app.prototype.tools.faiss_index_service import FaissIndexService
                svc = FaissIndexService()
                if svc.available:
                    self._faiss_service = svc
                    logger.info("ScoutService: FAISS semantic search enabled")
                elif search_mode == "semantic":
                    raise ImportError("FAISS or sentence-transformers not installed")
            except ImportError:
                if search_mode == "semantic":
                    raise
                logger.info("ScoutService: FAISS unavailable, using keyword/string fallback")

        # Determine effective modes for sub-components
        if self._faiss_service is not None:
            sample_mode = "auto"
            term_mode = "auto"
        else:
            sample_mode = "jaccard"
            term_mode = "string"
        self._sample_mode = sample_mode
        self._term_mode = term_mode

        self._sample_matcher = SampleMatcher(faiss_service=self._faiss_service)
        self._terminology_loader = TerminologyLoader(faiss_service=self._faiss_service)
        self._taboo_engine = TabooRuleEngine()

        # Instance-level evidence cache: "subject::tradition" -> ScoutEvidence
        self._evidence_cache: dict[str, ScoutEvidence] = {}

    def gather_evidence(
        self,
        subject: str,
        cultural_tradition: str,
    ) -> ScoutEvidence:
        cache_key = f"{subject}::{cultural_tradition}"
        if cache_key in self._evidence_cache:
            logger.debug("Scout cache HIT: %s", cache_key)
            return copy.deepcopy(self._evidence_cache[cache_key])

        # Load evolved scout insight (zero regression on failure)
        scout_notes: list[str] = []
        try:
            from app.prototype.cultural_pipelines.cultural_weights import get_agent_insight
            scout_insight = get_agent_insight("scout")
            if scout_insight:
                # Cap at 200 chars for evidence brevity
                scout_notes.append(f"[Scout insight] {scout_insight[:200]}")
                logger.debug("Scout evolved insight loaded (%d chars)", len(scout_insight))
        except Exception:
            pass  # Zero regression

        sample_matches = self._sample_matcher.match(
            subject=subject,
            cultural_tradition=cultural_tradition,
            top_k=3,
            mode=self._sample_mode,
        )
        terminology_hits = self._terminology_loader.match(
            text=subject,
            cultural_tradition=cultural_tradition,
            mode=self._term_mode,
        )
        taboo_violations = self._taboo_engine.check(
            text=subject,
            cultural_tradition=cultural_tradition,
        )
        evidence = ScoutEvidence(
            sample_matches=sample_matches,
            terminology_hits=terminology_hits,
            taboo_violations=taboo_violations,
            notes=scout_notes,
        )
        self._evidence_cache[cache_key] = evidence
        logger.debug("Scout cache MISS, stored: %s", cache_key)
        return copy.deepcopy(evidence)

    def clear_cache(self) -> None:
        """Clear the evidence cache."""
        self._evidence_cache.clear()

    def search_visual_references(
        self,
        subject: str,
        cultural_tradition: str,
        top_k: int = 5,
    ) -> list[dict]:
        """Search for visually similar samples using CLIP cross-modal search.

        Returns list of dicts with {doc_id, similarity, tradition, text_snippet}.
        Falls back to empty list if CLIP is unavailable.
        """
        if self._faiss_service is None:
            return []
        if not self._faiss_service.clip_available:
            return []

        hits = self._faiss_service.search_by_visual(
            query_text=subject,
            tradition=cultural_tradition,
            top_k=top_k,
        )
        return [
            {
                "doc_id": h.doc_id,
                "similarity": h.similarity,
                "tradition": h.tradition,
                "text_snippet": h.text_snippet,
            }
            for h in hits
        ]

    def compute_evidence_coverage(self, evidence: ScoutEvidence) -> float:
        """Compute evidence coverage score for LayerState integration.

        Formula::

            coverage = 0.5 * best_sample_similarity
                     + 0.4 * avg_term_confidence
                     + 0.1 * has_any_evidence
                     - min(0.5, 0.2 * taboo_count)
            clamped to [0, 1]
        """
        # Best sample similarity
        best_sample_sim = 0.0
        if evidence.sample_matches:
            best_sample_sim = max(m.similarity for m in evidence.sample_matches)

        # Average term confidence
        avg_term_conf = 0.0
        if evidence.terminology_hits:
            avg_term_conf = sum(h.confidence for h in evidence.terminology_hits) / len(
                evidence.terminology_hits
            )

        # Has any evidence at all
        has_any = 1.0 if (evidence.sample_matches or evidence.terminology_hits) else 0.0

        # Taboo penalty
        taboo_count = len(evidence.taboo_violations)
        taboo_penalty = min(0.5, 0.2 * taboo_count)

        coverage = 0.5 * best_sample_sim + 0.4 * avg_term_conf + 0.1 * has_any - taboo_penalty
        return max(0.0, min(1.0, coverage))

    # ------------------------------------------------------------------
    # Layer 1a: EvidencePack construction
    # ------------------------------------------------------------------

    def build_evidence_pack(
        self,
        subject: str,
        tradition: str,
        evidence: ScoutEvidence,
    ) -> EvidencePack:
        """Build a structured EvidencePack from gathered evidence.

        Enriches raw terminology hits with definitions, usage hints,
        and tradition-specific composition/style/taboo data.
        """
        coverage = self.compute_evidence_coverage(evidence)

        # Build terminology anchors with definitions and usage hints
        anchors: list[TerminologyAnchor] = []
        for hit in evidence.terminology_hits:
            entry = self._terminology_loader.get_term_entry(hit.term, tradition)
            definition = entry.get("definition", "") if entry else ""
            l_levels = entry.get("l_levels", []) if entry else []
            category = entry.get("category", "") if entry else ""
            usage_hint = _category_to_usage_hint(category) if category else ""
            anchors.append(TerminologyAnchor(
                term=hit.term,
                definition=definition,
                usage_hint=usage_hint,
                source=hit.dictionary_ref,
                confidence=hit.confidence,
                l_levels=l_levels,
            ))

        # Build composition references from tradition mapping
        compositions = _get_composition_references(tradition)

        # Build style constraints from tradition mapping
        styles = _get_style_constraints(tradition)

        # Build taboo constraints
        taboos = [
            TabooConstraint(
                description=v.description,
                severity=v.severity,
                tradition_source=tradition,
            )
            for v in evidence.taboo_violations
        ]

        return EvidencePack(
            subject=subject,
            tradition=tradition,
            anchors=anchors,
            compositions=compositions,
            styles=styles,
            taboos=taboos,
            coverage=coverage,
        )

    # ------------------------------------------------------------------
    # Layer 1c: Supplementary evidence retrieval
    # ------------------------------------------------------------------

    def gather_supplementary(
        self,
        need: "NeedMoreEvidence",
        existing_pack: EvidencePack,
    ) -> EvidencePack:
        """Perform supplementary retrieval to fill evidence gaps.

        Uses suggested_queries from NeedMoreEvidence to do additional
        FAISS semantic search, then merges results into the existing pack.

        Parameters
        ----------
        need : NeedMoreEvidence
            Critic's request for more evidence.
        existing_pack : EvidencePack
            The current evidence pack to supplement.

        Returns
        -------
        EvidencePack
            Updated pack with additional anchors and recalculated coverage.
        """
        from app.prototype.agents.need_more_evidence import NeedMoreEvidence

        existing_terms = {a.term.lower() for a in existing_pack.anchors}
        new_anchors: list[TerminologyAnchor] = []

        for query in need.suggested_queries:
            # Try FAISS semantic search if available
            if self._faiss_service is not None and self._faiss_service.available:
                hits = self._faiss_service.search_terms(
                    query=query,
                    tradition=existing_pack.tradition,
                    top_k=3,
                )
                for hit in hits:
                    entry = self._terminology_loader.get_term_entry_by_id(hit.doc_id)
                    if entry is None:
                        continue
                    term_text = entry.get("term_en", entry.get("term_zh", hit.doc_id))
                    if term_text.lower() in existing_terms:
                        continue
                    existing_terms.add(term_text.lower())
                    category = entry.get("category", "")
                    new_anchors.append(TerminologyAnchor(
                        term=term_text,
                        definition=entry.get("definition", ""),
                        usage_hint=_category_to_usage_hint(category),
                        source=f"supplementary_{existing_pack.tradition}",
                        confidence=round(hit.similarity * 0.8, 4),
                        l_levels=entry.get("l_levels", []),
                    ))

        # Merge new anchors into the pack
        updated_anchors = existing_pack.anchors + new_anchors
        n_total = max(len(updated_anchors), 1)
        avg_conf = sum(a.confidence for a in updated_anchors) / n_total
        new_coverage = min(1.0, existing_pack.coverage + 0.1 * len(new_anchors))

        return EvidencePack(
            subject=existing_pack.subject,
            tradition=existing_pack.tradition,
            anchors=updated_anchors,
            compositions=existing_pack.compositions,
            styles=existing_pack.styles,
            taboos=existing_pack.taboos,
            coverage=new_coverage,
            timestamp=existing_pack.timestamp,
        )


# ---------------------------------------------------------------------------
# Tradition-specific mappings for EvidencePack construction
# ---------------------------------------------------------------------------

_LEGACY_COMPOSITION_MAP: dict[str, list[dict]] = {
    "chinese_xieyi": [
        {"description": "留白 — intentional empty space for qi flow",
         "spatial_strategy": "asymmetric_balance",
         "example_prompt_fragment": "sparse composition with empty space, asymmetric balance"},
    ],
    "chinese_gongbi": [
        {"description": "工笔重色 — dense layered mineral pigments",
         "spatial_strategy": "centre_focus",
         "example_prompt_fragment": "centered subject, meticulous detail, layered mineral pigments"},
    ],
    "western_academic": [
        {"description": "Albertian perspective with vanishing point",
         "spatial_strategy": "rule_of_thirds",
         "example_prompt_fragment": "classical perspective, rule of thirds, vanishing point composition"},
    ],
    "islamic_geometric": [
        {"description": "Infinite tessellation radiating from centre",
         "spatial_strategy": "radial_symmetry",
         "example_prompt_fragment": "radial geometric pattern, infinite tessellation, sacred geometry"},
    ],
    "african_traditional": [
        {"description": "Bold rhythmic patterns with symbolic forms",
         "spatial_strategy": "layered_depth",
         "example_prompt_fragment": "bold symbolic patterns, rhythmic repetition, carved forms"},
    ],
    "south_asian": [
        {"description": "Narrative registers with flat perspective",
         "spatial_strategy": "register_composition",
         "example_prompt_fragment": "detailed miniature, narrative scene, flat perspective with registers"},
    ],
}

_LEGACY_SCOUT_STYLE_MAP: dict[str, list[dict]] = {
    "chinese_xieyi": [
        {"attribute": "brush_texture", "value": "dry brush with visible fiber strokes on rice paper"},
        {"attribute": "color_palette", "value": "monochrome ink wash with subtle grey gradations"},
    ],
    "chinese_gongbi": [
        {"attribute": "brush_texture", "value": "fine hairline brushstrokes, smooth mineral pigments"},
        {"attribute": "color_palette", "value": "rich mineral pigments: azurite, malachite, cinnabar"},
    ],
    "western_academic": [
        {"attribute": "lighting", "value": "chiaroscuro dramatic lighting, warm tonal range"},
        {"attribute": "medium", "value": "oil on canvas texture, visible impasto in highlights"},
    ],
    "islamic_geometric": [
        {"attribute": "pattern", "value": "mathematical precision, perfect symmetry, interlocking forms"},
        {"attribute": "color_palette", "value": "cobalt blue, gold leaf, turquoise, deep red"},
    ],
    "african_traditional": [
        {"attribute": "form", "value": "stylized carved forms, strong silhouettes"},
        {"attribute": "pattern", "value": "bold geometric patterns, earth tone palette"},
    ],
    "south_asian": [
        {"attribute": "detail", "value": "intricate miniature details, jewel-like colors"},
        {"attribute": "gold", "value": "gold leaf accents, ornamental borders"},
    ],
}


def _get_composition_dynamic(tradition: str) -> list[dict]:
    """Dynamic composition lookup with 2-tier fallback: YAML → Legacy."""
    try:
        from app.prototype.cultural_pipelines.tradition_loader import get_tradition
        tc = get_tradition(tradition)
        if tc and tc.terminology:
            comps = []
            for term in tc.terminology:
                if term.category in ("composition", "form"):
                    defn = term.definition if isinstance(term.definition, str) else str(term.definition)
                    comps.append({
                        "description": f"{term.term_zh or term.term} — {defn[:80]}",
                        "spatial_strategy": "dynamic",
                        "example_prompt_fragment": f"{term.term}, {defn[:60]}",
                    })
            if comps:
                return comps
    except Exception:
        pass
    return _LEGACY_COMPOSITION_MAP.get(tradition, [])


def _get_style_dynamic(tradition: str) -> list[dict]:
    """Dynamic style constraint lookup with 2-tier fallback: YAML → Legacy."""
    try:
        from app.prototype.cultural_pipelines.tradition_loader import get_tradition
        tc = get_tradition(tradition)
        if tc and tc.terminology:
            styles = []
            for term in tc.terminology:
                if term.category in ("technique", "material", "color"):
                    defn = term.definition if isinstance(term.definition, str) else str(term.definition)
                    styles.append({
                        "attribute": term.category,
                        "value": f"{term.term}: {defn[:80]}",
                    })
            if styles:
                return styles
    except Exception:
        pass
    return _LEGACY_SCOUT_STYLE_MAP.get(tradition, [])


def _get_composition_references(tradition: str) -> list[CompositionReference]:
    entries = _get_composition_dynamic(tradition)
    return [
        CompositionReference(
            description=e["description"],
            spatial_strategy=e["spatial_strategy"],
            example_prompt_fragment=e["example_prompt_fragment"],
        )
        for e in entries
    ]


def _get_style_constraints(tradition: str) -> list[StyleConstraint]:
    entries = _get_style_dynamic(tradition)
    return [
        StyleConstraint(
            attribute=e["attribute"],
            value=e["value"],
            tradition_source=tradition,
        )
        for e in entries
    ]


# ---------------------------------------------------------------------------
# Singleton factory — avoids re-initializing FAISS/terminology on each run
# ---------------------------------------------------------------------------
_singleton: ScoutService | None = None


def get_scout_service(search_mode: str = "auto") -> ScoutService:
    """Return a cached ScoutService singleton.

    The ScoutService loads FAISS indices and terminology dictionaries on init,
    which takes ~3-5s.  Reusing a singleton across pipeline rounds avoids this
    repeated cost.
    """
    global _singleton  # noqa: PLW0603
    if _singleton is None:
        _singleton = ScoutService(search_mode=search_mode)
    return _singleton


def _category_to_usage_hint(category: str) -> str:
    """Map a terminology category to a prompt usage hint."""
    hints = {
        "technique": "use for technique description in prompt",
        "material": "mention as medium/material",
        "composition": "use for spatial composition guidance",
        "concept": "use as thematic anchor",
        "motif": "include as visual motif element",
        "color": "include in color palette description",
        "form": "use for form/shape description",
    }
    return hints.get(category, "include as contextual reference")
