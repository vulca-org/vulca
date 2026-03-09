"""Layer 3: ContextEvolver — safely update evolved_context.json.

Safety guardrails:
- Single adjustment ≤ ±0.05
- Weights always sum to 1.0
- Minimum 10 sessions before evolving
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from app.prototype.digestion.aggregator import DigestAggregator
from app.prototype.digestion.pattern_detector import Pattern, PatternDetector
from app.prototype.digestion.preference_learner import PreferenceLearner
from app.prototype.session.store import SessionStore

logger = logging.getLogger("vulca")

_MAX_DELTA = 0.05
_MIN_SESSIONS_TO_EVOLVE = 5

# Seed sessions use L1-L5 shorthand; weights use full dimension names.
_DIM_ALIASES: dict[str, str] = {
    "L1": "visual_perception",
    "L2": "technical_analysis",
    "L3": "cultural_context",
    "L4": "critical_interpretation",
    "L5": "philosophical_aesthetic",
}
_DEFAULT_CONTEXT_PATH = os.path.join(
    os.path.dirname(__file__), os.pardir, "data", "evolved_context.json"
)


@dataclass
class EvolutionAction:
    """A single weight adjustment action."""

    tradition: str
    dimension: str
    old_value: float
    new_value: float
    reason: str

    def to_dict(self) -> dict:
        return {
            "tradition": self.tradition,
            "dimension": self.dimension,
            "old_value": round(self.old_value, 4),
            "new_value": round(self.new_value, 4),
            "delta": round(self.new_value - self.old_value, 4),
            "reason": self.reason,
        }


@dataclass
class EvolutionResult:
    """Result of a context evolution run."""

    actions: list[EvolutionAction] = field(default_factory=list)
    patterns_found: int = 0
    sessions_analyzed: int = 0
    skipped_reason: str = ""

    def to_dict(self) -> dict:
        return {
            "actions": [a.to_dict() for a in self.actions],
            "patterns_found": self.patterns_found,
            "sessions_analyzed": self.sessions_analyzed,
            "skipped_reason": self.skipped_reason,
        }


class ContextEvolver:
    """Read digestion results and safely evolve context weights."""

    def __init__(
        self,
        store: SessionStore | None = None,
        context_path: str | None = None,
    ) -> None:
        self._store = store or SessionStore.get()
        self._context_path = Path(context_path or _DEFAULT_CONTEXT_PATH).resolve()
        self._detector = PatternDetector(DigestAggregator(self._store))
        self._learner = PreferenceLearner(self._store)

    def evolve(self) -> EvolutionResult:
        """Run full evolution cycle: detect → learn → adjust → save."""
        session_count = self._store.count()

        if session_count < _MIN_SESSIONS_TO_EVOLVE:
            return EvolutionResult(
                sessions_analyzed=session_count,
                skipped_reason=f"Need {_MIN_SESSIONS_TO_EVOLVE} sessions, have {session_count}",
            )

        # Detect patterns
        patterns = self._detector.detect()

        # Load current context
        context = self._load_context()

        # Initialize empty tradition_weights from cultural_weights fallback
        if not context.get("tradition_weights"):
            try:
                from app.prototype.cultural_pipelines.cultural_weights import get_all_weight_tables
                context["tradition_weights"] = get_all_weight_tables()
                logger.info("ContextEvolver: initialized tradition_weights from cultural_weights (%d traditions)",
                            len(context["tradition_weights"]))
            except Exception:
                logger.warning("ContextEvolver: could not initialize tradition_weights from cultural_weights")

        # Generate evolution actions from patterns
        actions: list[EvolutionAction] = []
        for pattern in patterns:
            if pattern.pattern_type == "systematically_low" and pattern.dimension != "feedback":
                action = self._boost_dimension(context, pattern)
                if action:
                    actions.append(action)
            elif pattern.pattern_type == "negative_feedback_dominant":
                # Don't auto-adjust for feedback patterns; log only
                logger.info("Feedback pattern detected for %s: %s", pattern.tradition, pattern.description)

        # Consume preference learner output (WU-10)
        try:
            preferences = self._learner.learn()
            for tradition, profile in preferences.items():
                weights = context.get("tradition_weights", {}).get(tradition)
                if not weights:
                    continue
                # Boost preferred dimensions slightly (within ±0.05 guardrail)
                for dim in profile.preferred_dimensions:
                    if dim in weights:
                        old_val = weights[dim]
                        delta = min(_MAX_DELTA * 0.5, 0.025)  # Half of max delta for preferences
                        new_val = min(1.0, old_val + delta)
                        if new_val != old_val:
                            weights[dim] = new_val
                            actions.append(EvolutionAction(
                                tradition=tradition,
                                dimension=dim,
                                old_value=old_val,
                                new_value=new_val,
                                reason=f"preference_boost ({profile.total_positive} positive signals)",
                            ))
                # Normalize after preference adjustments
                total = sum(weights.values())
                if total > 0 and abs(total - 1.0) > 0.001:
                    for d in weights:
                        weights[d] = weights[d] / total
        except Exception as exc:
            logger.debug("Preference learning skipped: %s", exc)

        # Consume avoided dimensions from preference learner (C3)
        try:
            for tradition, profile in preferences.items():
                weights = context.get("tradition_weights", {}).get(tradition)
                if not weights:
                    continue
                for dim in profile.avoided_dimensions:
                    if dim in weights:
                        old_val = weights[dim]
                        delta = min(_MAX_DELTA * 0.5, 0.025)
                        new_val = max(0.05, old_val - delta)
                        if new_val != old_val:
                            weights[dim] = new_val
                            actions.append(EvolutionAction(
                                tradition=tradition,
                                dimension=dim,
                                old_value=old_val,
                                new_value=new_val,
                                reason=f"preference_reduce ({profile.total_negative} negative signals)",
                            ))
                # Re-normalize after avoided adjustments
                total = sum(weights.values())
                if total > 0 and abs(total - 1.0) > 0.001:
                    for d in weights:
                        weights[d] = weights[d] / total
        except Exception:
            pass  # preferences may not be defined if learner failed

        # --- Phase 1.4: Layer focus generation from session scores ---
        all_sessions = [s for s in (self._store.get_all() if hasattr(self._store, 'get_all') else [])]
        try:
            layer_focus = self._extract_layer_focus(all_sessions)
            if layer_focus:
                context["layer_focus"] = layer_focus
        except Exception as exc:
            logger.debug("Layer focus extraction skipped: %s", exc)

        # Catabolic: Cultural clustering
        try:
            from app.prototype.digestion.cultural_clusterer import CulturalClusterer
            clusterer = CulturalClusterer()
            clusters = clusterer.cluster(all_sessions)
            if clusters:
                context.setdefault("feature_space", {})["clusters"] = [c.to_dict() for c in clusters]
        except Exception as exc:
            logger.debug("Cultural clustering skipped: %s", exc)
            clusters = []

        # Anabolic: Prompt distillation
        try:
            from app.prototype.digestion.prompt_distiller import PromptDistiller
            distiller = PromptDistiller()
            archetypes = distiller.distill(all_sessions)
            if archetypes:
                context.setdefault("prompt_contexts", {})["archetypes"] = [a.to_dict() for a in archetypes]
        except Exception as exc:
            logger.debug("Prompt distillation skipped: %s", exc)

        # Growth: Concept crystallization
        try:
            from app.prototype.digestion.concept_crystallizer import ConceptCrystallizer
            crystallizer = ConceptCrystallizer()
            concepts = crystallizer.crystallize(clusters, all_sessions)
            if concepts:
                for concept in concepts:
                    context.setdefault("cultures", {})[concept.name] = concept.to_dict()
        except Exception as exc:
            logger.debug("Concept crystallization skipped: %s", exc)

        # Save if any actions or new data was added (C2: unified save point)
        has_new_data = bool(
            context.get("feature_space", {}).get("clusters")
            or context.get("prompt_contexts", {}).get("archetypes")
            or context.get("cultures")
        )
        if actions or has_new_data:
            self._save_context(context)

        result = EvolutionResult(
            actions=actions,
            patterns_found=len(patterns),
            sessions_analyzed=session_count,
        )

        # Audit log
        if actions:
            self._log_evolution(result)

        return result

    def _boost_dimension(self, context: dict, pattern: Pattern) -> EvolutionAction | None:
        """Boost a systematically low dimension's weight, keeping sum=1.0."""
        tradition = pattern.tradition
        dim = _DIM_ALIASES.get(pattern.dimension, pattern.dimension)

        weights = context.get("tradition_weights", {}).get(tradition, {})
        if not weights or dim not in weights:
            return None

        old_val = weights[dim]
        delta = min(_MAX_DELTA, (0.60 - pattern.avg_score) * 0.1)
        delta = max(0.0, delta)  # Only boost, don't reduce

        if delta < 0.005:
            return None  # Too small to matter

        new_val = min(1.0, old_val + delta)

        # Redistribute: reduce other dims proportionally to keep sum=1.0
        other_dims = [d for d in weights if d != dim]
        reduction_total = new_val - old_val
        other_total = sum(weights[d] for d in other_dims)
        if other_total > 0:
            for d in other_dims:
                share = weights[d] / other_total
                weights[d] = max(0.05, weights[d] - reduction_total * share)

        weights[dim] = new_val

        # Normalize to exactly 1.0
        total = sum(weights.values())
        if total > 0:
            for d in weights:
                weights[d] = weights[d] / total

        context.setdefault("tradition_weights", {})[tradition] = weights

        return EvolutionAction(
            tradition=tradition,
            dimension=dim,
            old_value=old_val,
            new_value=weights[dim],
            reason=pattern.description,
        )

    def _load_context(self) -> dict:
        """Load evolved context or return default v2 structure."""
        if self._context_path.exists():
            try:
                with open(self._context_path, "r", encoding="utf-8") as f:
                    context = json.load(f)
                # v1 → v2 auto-upgrade
                if "cultures" not in context:
                    context["cultures"] = {}
                if "prompt_contexts" not in context:
                    context["prompt_contexts"] = {}
                if "feature_space" not in context:
                    context["feature_space"] = {}
                if context.get("version", 1) < 2:
                    context["version"] = 2
                return context
            except (json.JSONDecodeError, ValueError):
                pass
        return {
            "tradition_weights": {},
            "cultures": {},
            "prompt_contexts": {},
            "feature_space": {},
            "version": 2,
            "evolutions": 0,
        }

    def _save_context(self, context: dict) -> None:
        """Atomically save evolved context to avoid corruption on crash."""
        context["evolutions"] = context.get("evolutions", 0) + 1
        self._context_path.parent.mkdir(parents=True, exist_ok=True)
        dir_name = str(self._context_path.parent)
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(context, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, str(self._context_path))  # atomic on POSIX
        except BaseException:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
        logger.info("ContextEvolver: saved evolved context (evolution #%d)", context["evolutions"])

    def generate_report(self) -> dict:
        """Generate a summary report of the current evolved context.

        Replaces the old AdminAgent weekly report with a simpler,
        digestion-native summary.

        Returns
        -------
        dict with keys: traditions_count, total_sessions, last_evolution,
        evolutions_count, top_patterns.
        """
        context = self._load_context()
        traditions_count = len(context.get("tradition_weights", {}))
        evolutions_count = context.get("evolutions", 0)

        # Determine last evolution timestamp from audit log
        log_path = self._context_path.parent / "evolution_log.jsonl"
        last_evolution: float | None = None
        if log_path.exists():
            try:
                last_line = ""
                with open(log_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            last_line = line
                if last_line:
                    entry = json.loads(last_line)
                    last_evolution = entry.get("timestamp")
            except (json.JSONDecodeError, OSError):
                pass

        # Detect current patterns
        top_patterns: list[dict] = []
        try:
            patterns = self._detector.detect()
            top_patterns = [p.to_dict() for p in patterns[:10]]
        except Exception:
            pass

        return {
            "traditions_count": traditions_count,
            "total_sessions": self._store.count(),
            "last_evolution": last_evolution,
            "evolutions_count": evolutions_count,
            "top_patterns": top_patterns,
        }

    def _log_evolution(self, result: EvolutionResult) -> None:
        """Append evolution result to evolution_log.jsonl for audit trail."""
        import time as _time

        log_path = self._context_path.parent / "evolution_log.jsonl"
        entry = {
            "timestamp": _time.time(),
            "sessions_analyzed": result.sessions_analyzed,
            "patterns_found": result.patterns_found,
            "actions": [a.to_dict() for a in result.actions],
        }
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError as exc:
            logger.warning("ContextEvolver: failed to write audit log: %s", exc)

    # ------------------------------------------------------------------
    # Phase 1.4: Layer-specific focus point extraction
    # ------------------------------------------------------------------

    _DIMENSIONS = [
        "visual_perception", "technical_analysis", "cultural_context",
        "critical_interpretation", "philosophical_aesthetic",
    ]

    # Map tradition → layer → what matters (seeded from domain knowledge)
    _SEED_FOCUS: dict[str, dict[str, list[str]]] = {
        "chinese_xieyi": {
            "visual_perception": ["ink wash gradients", "negative space (留白)", "brush rhythm"],
            "technical_analysis": ["brushstroke spontaneity", "ink consistency", "rice paper texture"],
            "cultural_context": ["literati painting tradition", "Daoist nature philosophy", "poem-painting unity"],
            "critical_interpretation": ["qi yun (气韵生动)", "xie yi spirit over form", "scholar aesthetics"],
            "philosophical_aesthetic": ["Dao in brushwork", "emptiness as presence", "nature-human unity"],
        },
        "chinese_gongbi": {
            "visual_perception": ["line precision", "color layering", "fine detail rendering"],
            "technical_analysis": ["silk/paper preparation", "mineral pigment application", "outline control"],
            "cultural_context": ["court painting tradition", "Tang-Song conventions", "decorative symbolism"],
        },
        "islamic_geometric": {
            "visual_perception": ["geometric symmetry", "tessellation precision", "color harmony"],
            "technical_analysis": ["compass-ruler construction", "pattern repetition accuracy", "gilding quality"],
            "cultural_context": ["aniconism principles", "mathematical beauty", "spiritual geometry"],
        },
    }

    def _extract_layer_focus(self, sessions: list) -> dict:
        """Extract per-tradition, per-layer focus points from session data.

        Returns dict of {tradition: {layer_id: {focus_points, anti_focus}}}.
        Combines seed knowledge with learned patterns from high-scoring sessions.
        """
        from collections import defaultdict

        # Collect per-tradition, per-dimension scores
        tradition_dim_scores: dict[str, dict[str, list[float]]] = defaultdict(
            lambda: defaultdict(list)
        )

        for s in sessions:
            tradition = getattr(s, "tradition", "") or ""
            scores = getattr(s, "final_scores", {}) or {}
            if not tradition or not scores:
                continue
            for dim, score in scores.items():
                full_dim = _DIM_ALIASES.get(dim, dim)
                if full_dim in self._DIMENSIONS and isinstance(score, (int, float)):
                    tradition_dim_scores[tradition][full_dim].append(score)

        result: dict[str, dict[str, dict]] = {}

        for tradition in set(list(tradition_dim_scores.keys()) + list(self._SEED_FOCUS.keys())):
            dim_data = tradition_dim_scores.get(tradition, {})
            seed = self._SEED_FOCUS.get(tradition, {})
            layers: dict[str, dict] = {}

            for dim in self._DIMENSIONS:
                scores = dim_data.get(dim, [])
                focus_points = list(seed.get(dim, []))  # start with seed

                # Learn from patterns: if a dimension scores consistently high,
                # the focus points for that tradition are working
                if scores:
                    avg = sum(scores) / len(scores)
                    if avg >= 0.7 and not focus_points:
                        focus_points.append(f"historically strong ({avg:.2f} avg)")

                anti_focus: list[str] = []
                if scores:
                    avg = sum(scores) / len(scores)
                    if avg >= 0.8:
                        # This dimension doesn't need extra attention
                        anti_focus.append("already well-captured")

                if focus_points:
                    layers[dim] = {
                        "focus_points": focus_points,
                        "anti_focus": anti_focus,
                        "session_count": len(scores),
                    }

            if layers:
                result[tradition] = layers

        return result
