"""Layer 3: ContextEvolver — safely update evolved_context.json.

Two-phase evolution:
1. **Rule-based** (always runs): Weight adjustments with safety guardrails
   (single adjustment <= +/-0.05, weights sum to 1.0, minimum sessions).
2. **LLM-powered** (when API key available): Generates ``agent_insights``
   and ``tradition_insights`` — narrative guidance injected into agent
   system prompts.  This is the MemRL core: frozen model + evolving context.

Falls back to rule-only mode when no API key is configured.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from app.prototype.digestion.aggregator import DigestAggregator
from app.prototype.digestion.base import BaseDigester, DigestContext
from app.prototype.digestion.pattern_detector import Pattern, PatternDetector
from app.prototype.digestion.preference_learner import PreferenceLearner
from app.prototype.session.store import SessionStore

logger = logging.getLogger("vulca")

_MAX_DELTA = 0.05
_MIN_SESSIONS_TO_EVOLVE = 5
_MIN_HUMAN_FEEDBACK = 3  # Require at least 3 real human feedback sessions before evolving
_LLM_TIMEOUT_S = 60
_AGENT_ROLES = frozenset({"scout", "draft", "critic", "queen"})

# Seed sessions use L1-L5 shorthand; weights use full dimension names.
# This map normalises *any* known alias -> canonical full name so that both
# ``"L1"`` and ``"visual_perception"`` resolve to the same key.
_LAYER_NAME_MAP: dict[str, str] = {
    # Short labels (session data)
    "L1": "visual_perception",
    "L2": "technical_analysis",
    "L3": "cultural_context",
    "L4": "critical_interpretation",
    "L5": "philosophical_aesthetic",
    # Full canonical names (identity)
    "visual_perception": "visual_perception",
    "technical_analysis": "technical_analysis",
    "cultural_context": "cultural_context",
    "critical_interpretation": "critical_interpretation",
    "philosophical_aesthetic": "philosophical_aesthetic",
}

# Reverse: canonical full name -> L-label (e.g. for normalising weight keys)
_DIM_TO_LABEL: dict[str, str] = {v: k for k, v in _LAYER_NAME_MAP.items() if k.startswith("L")}

# Keep backward-compatible alias (several modules import _DIM_ALIASES)
_DIM_ALIASES = _LAYER_NAME_MAP
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

    def evolve(self) -> EvolutionResult:
        """Run full evolution cycle: detect -> learn -> adjust -> save.

        Uses the step adapter pipeline (``BaseDigester.get_ordered_digesters``)
        for pluggable digestion steps, with inline orchestration for weight
        adjustments and preference boosts that depend on cross-step data.

        **Guard**: Requires at least ``_MIN_HUMAN_FEEDBACK`` sessions with
        explicit human feedback (accepted/rejected) from non-seed sources.
        Without real human input, evolution would overfit to synthetic data.
        """
        session_count = self._store.count()

        if session_count < _MIN_SESSIONS_TO_EVOLVE:
            return EvolutionResult(
                sessions_analyzed=session_count,
                skipped_reason=f"Need {_MIN_SESSIONS_TO_EVOLVE} sessions, have {session_count}",
            )

        # Guard: require real human feedback before evolving weights.
        # Seed sessions (seed-*) and sessions without explicit feedback don't count.
        all_sessions = self._store.get_all()
        human_feedback_count = sum(
            1 for s in all_sessions
            if s.get("user_feedback") in ("accepted", "rejected")
            and not str(s.get("session_id", "")).startswith("seed-")
        )
        if human_feedback_count < _MIN_HUMAN_FEEDBACK:
            return EvolutionResult(
                sessions_analyzed=session_count,
                skipped_reason=(
                    f"Need {_MIN_HUMAN_FEEDBACK} sessions with real human feedback, "
                    f"have {human_feedback_count} (seed sessions excluded)"
                ),
            )

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

        # all_sessions already loaded in the human feedback guard above

        # Build shared DigestContext
        ctx = DigestContext(
            data=context,
            session_count=session_count,
            sessions=all_sessions,
            evolver=self,
        )

        # --- Run registered pipeline steps ---
        # Import steps module to trigger __init_subclass__ registration
        import app.prototype.digestion.steps  # noqa: F401

        for digester_cls in BaseDigester.get_ordered_digesters():
            step_name = digester_cls.STEP_NAME
            try:
                digester = digester_cls()
                ctx = digester.digest(all_sessions, ctx)
            except Exception as exc:
                logger.debug("Digestion step '%s' failed: %s", step_name, exc)

        # --- Inline orchestration: weight adjustments from patterns ---
        actions: list[EvolutionAction] = []
        patterns = ctx.patterns

        for pattern in patterns:
            if pattern.pattern_type == "systematically_low" and pattern.dimension != "feedback":
                action = self._boost_dimension(context, pattern)
                if action:
                    actions.append(action)
            elif pattern.pattern_type == "negative_feedback_dominant":
                # Don't auto-adjust for feedback patterns; log only
                logger.info("Feedback pattern detected for %s: %s", pattern.tradition, pattern.description)

        # --- Inline orchestration: preference boost/reduce ---
        preferences = ctx.data.pop("_preferences", {})
        try:
            for tradition, profile in preferences.items():
                weights = context.get("tradition_weights", {}).get(tradition)
                if not weights:
                    continue
                # Boost preferred dimensions slightly (within +/-0.05 guardrail)
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
            logger.debug("Preference boost skipped: %s", exc)

        # Consume avoided dimensions from preference learner (C3)
        # Scale delta by comment intensity: more/stronger complaints → larger adjustment
        try:
            for tradition, profile in preferences.items():
                weights = context.get("tradition_weights", {}).get(tradition)
                if not weights:
                    continue
                # Compute comment intensity multiplier (1.0 = baseline, up to 2.0)
                comment_boost = 1.0
                if profile.negative_comments:
                    strong = ["wrong", "broken", "terrible", "useless", "错误", "完全", "不可接受", "penalize", "unfair"]
                    strong_count = sum(
                        1 for c in profile.negative_comments
                        if any(kw in c.lower() for kw in strong)
                    )
                    comment_boost = min(2.0, 1.0 + strong_count * 0.3 + len(profile.negative_comments) * 0.1)
                for dim in profile.avoided_dimensions:
                    if dim in weights:
                        old_val = weights[dim]
                        delta = min(_MAX_DELTA * 0.5 * comment_boost, _MAX_DELTA)
                        new_val = max(0.05, old_val - delta)
                        if new_val != old_val:
                            weights[dim] = new_val
                            reason = f"preference_reduce ({profile.total_negative} negative"
                            if profile.negative_comments:
                                reason += f", {len(profile.negative_comments)} comments, intensity={comment_boost:.1f}"
                            reason += ")"
                            actions.append(EvolutionAction(
                                tradition=tradition,
                                dimension=dim,
                                old_value=old_val,
                                new_value=new_val,
                                reason=reason,
                            ))
                # Re-normalize after avoided adjustments
                total = sum(weights.values())
                if total > 0 and abs(total - 1.0) > 0.001:
                    for d in weights:
                        weights[d] = weights[d] / total
        except Exception:
            pass  # preferences may not be defined if learner failed

        # Store actions on ctx for potential use by later introspection
        ctx.actions = actions

        # Run InsightStep explicitly (ENABLED_BY_DEFAULT=False because it
        # depends on ctx.actions which is populated above, after the step loop).
        try:
            from app.prototype.digestion.steps.insight_step import InsightStep
            ctx = InsightStep().digest(all_sessions, ctx)
        except Exception as exc:
            logger.debug("InsightStep (post-actions) failed: %s", exc)

        # Save if any actions or new data was added (C2: unified save point)
        has_new_data = bool(
            context.get("feature_space", {}).get("clusters")
            or context.get("prompt_contexts", {}).get("archetypes")
            or context.get("cultures")
            or context.get("queen_strategy")
            or context.get("agent_insights")
            or context.get("tradition_insights")
            or context.get("trajectory_insights")
        )
        if actions or has_new_data:
            from datetime import datetime, timezone
            context["last_evolved_at"] = datetime.now(timezone.utc).isoformat()
            self._save_context(context)

        result = EvolutionResult(
            actions=actions,
            patterns_found=len(patterns),
            sessions_analyzed=session_count,
        )

        # Audit log — always log when context was saved (not just when actions exist)
        if actions or has_new_data:
            self._log_evolution(result)

        return result

    def _boost_dimension(self, context: dict, pattern: Pattern) -> EvolutionAction | None:
        """Boost a systematically low dimension's weight, keeping sum=1.0."""
        tradition = pattern.tradition
        dim = _LAYER_NAME_MAP.get(pattern.dimension, pattern.dimension)

        weights = context.get("tradition_weights", {}).get(tradition, {})
        if not weights:
            return None

        # Weights may use either L-labels or full names as keys.
        # Try full name first, then fall back to L-label.
        if dim not in weights:
            label = _DIM_TO_LABEL.get(dim)
            if label and label in weights:
                dim = label  # use the L-label key that's in weights
            else:
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
                # v1 -> v2 auto-upgrade
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
    # LLM-powered insights generation (MemRL phase)
    # ------------------------------------------------------------------

    _INSIGHTS_SYSTEM = """\
You are an expert cultural art evolution analyst for the VULCA system.
Analyze session patterns and generate actionable insights for AI agents.

Output valid JSON with two keys:
1. "agent_insights": dict mapping agent role -> guidance string
   - "scout": What the Scout agent should focus on when analyzing subjects
   - "draft": What the Draft agent should emphasize when generating images
   - "critic": What the Critic agent should prioritize when evaluating
   - "queen": What the Queen agent should consider when making final decisions
2. "tradition_insights": dict mapping tradition name -> narrative string
   Each narrative should describe what's working, what needs improvement,
   and specific guidance for creating better art in that tradition.

Keep each guidance string under 100 words. Be specific and actionable.
Output ONLY the JSON object, no markdown fences or explanation."""

    _INSIGHTS_USER = """\
Evolution context:
- Sessions analyzed: {session_count}
- Patterns detected: {pattern_summary}
- Weight adjustments made: {action_summary}
- Active traditions: {traditions}

Top session examples:
{session_examples}

Current weight distribution:
{weight_summary}

Generate agent insights and tradition-specific guidance based on this data."""

    @staticmethod
    def _has_api_key() -> bool:
        """Check if an LLM API key is available."""
        from app.prototype.digestion.llm_utils import has_llm_api_key

        return has_llm_api_key()

    def _generate_llm_insights(
        self,
        context: dict,
        patterns: list[Pattern],
        actions: list[EvolutionAction],
        sessions: list,
    ) -> dict | None:
        """Use LLM to generate agent_insights and tradition_insights.

        Returns dict with 'agent_insights' and 'tradition_insights' keys,
        or None if LLM is unavailable or fails.
        """
        if not self._has_api_key():
            return None

        import litellm
        from app.prototype.agents.model_router import MODEL_FAST

        # Build context summary for LLM
        pattern_summary = "; ".join(
            f"{p.pattern_type} in {p.tradition}/{p.dimension}" for p in patterns[:10]
        ) or "none detected"

        action_summary = "; ".join(
            f"{a.dimension} {a.old_value:.2f}->{a.new_value:.2f} ({a.reason})"
            for a in actions[:5]
        ) or "none"

        traditions = sorted(context.get("tradition_weights", {}).keys())

        # Session examples
        examples: list[str] = []
        for s in sessions[:10]:
            intent = getattr(s, "intent", "") or getattr(s, "subject", "") or ""
            tradition = getattr(s, "tradition", "") or ""
            score = getattr(s, "final_weighted_total", 0) or 0
            if intent:
                examples.append(f"- [{tradition}] \"{intent}\" (score: {score:.2f})")

        # Weight summary
        weight_lines: list[str] = []
        for t, w in list(context.get("tradition_weights", {}).items())[:5]:
            top_dims = sorted(w.items(), key=lambda x: x[1], reverse=True)[:3]
            dims_str = ", ".join(f"{d}={v:.2f}" for d, v in top_dims)
            weight_lines.append(f"- {t}: {dims_str}")

        user_msg = self._INSIGHTS_USER.format(
            session_count=len(sessions),
            pattern_summary=pattern_summary,
            action_summary=action_summary,
            traditions=", ".join(traditions[:10]),
            session_examples="\n".join(examples) or "none",
            weight_summary="\n".join(weight_lines) or "none",
        )

        response = litellm.completion(
            model=MODEL_FAST,
            messages=[
                {"role": "system", "content": self._INSIGHTS_SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.3,
            max_tokens=4096,
            timeout=_LLM_TIMEOUT_S,
        )

        from app.prototype.digestion.llm_utils import strip_markdown_fences

        raw = (response.choices[0].message.content or "").strip()
        content = strip_markdown_fences(raw)

        # Extract JSON object even if surrounded by extra text
        brace_start = content.find("{")
        brace_end = content.rfind("}")
        if brace_start != -1 and brace_end > brace_start:
            content = content[brace_start:brace_end + 1]

        result = json.loads(content)
        if not isinstance(result, dict):
            return None

        parsed: dict = {}

        agent_insights = result.get("agent_insights", {})
        if isinstance(agent_insights, dict):
            parsed["agent_insights"] = {
                k: str(v)[:500] for k, v in agent_insights.items()
                if k in _AGENT_ROLES and v
            }

        tradition_insights = result.get("tradition_insights", {})
        if isinstance(tradition_insights, dict):
            parsed["tradition_insights"] = {
                k: str(v)[:500] for k, v in tradition_insights.items() if v
            }

        logger.info(
            "ContextEvolver(LLM): generated %d agent insights, %d tradition insights",
            len(parsed.get("agent_insights", {})),
            len(parsed.get("tradition_insights", {})),
        )
        return parsed if parsed else None

    # ------------------------------------------------------------------
    # Phase 1.4: Layer-specific focus point extraction
    # ------------------------------------------------------------------

    _DIMENSIONS = [
        "visual_perception", "technical_analysis", "cultural_context",
        "critical_interpretation", "philosophical_aesthetic",
    ]

    # Map tradition -> layer -> what matters (seeded from domain knowledge)
    _SEED_FOCUS: dict[str, dict[str, list[str]]] = {
        "chinese_xieyi": {
            "visual_perception": ["ink wash gradients", "negative space (\u7559\u767d)", "brush rhythm"],
            "technical_analysis": ["brushstroke spontaneity", "ink consistency", "rice paper texture"],
            "cultural_context": ["literati painting tradition", "Daoist nature philosophy", "poem-painting unity"],
            "critical_interpretation": ["qi yun (\u6c14\u97f5\u751f\u52a8)", "xie yi spirit over form", "scholar aesthetics"],
            "philosophical_aesthetic": ["Dao in brushwork", "emptiness as presence", "nature-human unity"],
        },
        "chinese_gongbi": {
            "visual_perception": ["line precision", "color layering", "fine detail rendering"],
            "technical_analysis": ["silk/paper preparation", "mineral pigment application", "outline control"],
            "cultural_context": ["court painting tradition", "Tang-Song conventions", "decorative symbolism"],
            "critical_interpretation": ["auspicious symbolism", "narrative scene reading", "rank/status coding"],
            "philosophical_aesthetic": ["beauty through restraint", "order as virtue", "meticulous devotion"],
        },
        "islamic_geometric": {
            "visual_perception": ["geometric symmetry", "tessellation precision", "color harmony"],
            "technical_analysis": ["compass-ruler construction", "pattern repetition accuracy", "gilding quality"],
            "cultural_context": ["aniconism principles", "mathematical beauty", "spiritual geometry"],
            "critical_interpretation": ["infinite pattern meditation", "unity in multiplicity"],
            "philosophical_aesthetic": ["divine order through geometry", "transcendence of material form"],
        },
        "japanese_traditional": {
            "visual_perception": ["seasonal motifs", "asymmetric balance", "wabi-sabi textures"],
            "technical_analysis": ["sumi ink gradation", "woodblock layering", "gold leaf application"],
            "cultural_context": ["mono no aware (\u7269\u306e\u54c0\u308c)", "Zen simplicity", "seasonal awareness"],
            "critical_interpretation": ["ma (\u9593) spatial reading", "impermanence as beauty"],
            "philosophical_aesthetic": ["wabi-sabi acceptance", "nature-art continuity", "quiet depth"],
        },
        "western_academic": {
            "visual_perception": ["chiaroscuro modeling", "linear perspective", "anatomical proportion"],
            "technical_analysis": ["oil layering technique", "color theory application", "canvas preparation"],
            "cultural_context": ["classical tradition", "art historical references", "genre conventions"],
            "critical_interpretation": ["iconographic analysis", "formal composition critique"],
            "philosophical_aesthetic": ["mimesis vs. expression", "beauty and sublimity", "artistic genius"],
        },
        "african_traditional": {
            "visual_perception": ["bold pattern rhythms", "symbolic color use", "sculptural form"],
            "technical_analysis": ["material authenticity", "textile/carving technique", "natural pigments"],
            "cultural_context": ["communal storytelling", "ritual significance", "ancestral symbolism"],
            "critical_interpretation": ["spiritual function", "social identity encoding"],
            "philosophical_aesthetic": ["art as life force", "collective memory", "spiritual embodiment"],
        },
        "south_asian": {
            "visual_perception": ["vivid color saturation", "ornamental density", "narrative composition"],
            "technical_analysis": ["miniature painting precision", "natural dye mastery", "gold detailing"],
            "cultural_context": ["rasa theory (emotional essence)", "mythological narratives", "devotional art"],
            "critical_interpretation": ["rasa identification", "darshan (sacred seeing)", "iconometric rules"],
            "philosophical_aesthetic": ["divine beauty manifestation", "cyclical time in art", "sensory transcendence"],
        },
        "watercolor": {
            "visual_perception": ["luminous transparency", "wet-on-wet diffusion", "paper white preservation"],
            "technical_analysis": ["wash control", "granulation effects", "lifting and blotting"],
            "cultural_context": ["plein air tradition", "botanical illustration heritage", "travel sketching"],
            "critical_interpretation": ["spontaneity vs. control balance", "light as subject"],
            "philosophical_aesthetic": ["ephemerality of the medium", "harmony with accident"],
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
                anti_focus: list[str] = []
                if scores:
                    avg = sum(scores) / len(scores)
                    if avg >= 0.7 and not focus_points:
                        focus_points.append(f"historically strong ({avg:.2f} avg)")
                    if avg >= 0.8:
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

    # ------------------------------------------------------------------
    # Trajectory-based learning
    # ------------------------------------------------------------------

    def _extract_trajectory_insights(self) -> dict | None:
        """Extract learning signals from recorded pipeline trajectories.

        Analyzes trajectory files to learn:
        - avg_rounds_to_accept: How many rounds successful runs typically take
        - common_weak_dimensions: Dimensions most frequently flagged by Critic
        - repair_success_rate: How often rerun improves the flagged dimension
        - per-tradition efficiency patterns
        """
        from collections import Counter, defaultdict

        try:
            from app.prototype.trajectory.trajectory_recorder import TrajectoryRecorder
            recorder = TrajectoryRecorder()
        except Exception:
            return None

        if recorder.count() < 3:
            return None  # Not enough data

        records = recorder.load_all()
        if not records:
            return None

        # Aggregate stats
        rounds_per_accept: list[int] = []
        weak_dims: Counter = Counter()
        repair_attempts = 0
        repair_successes = 0
        tradition_rounds: dict[str, list[int]] = defaultdict(list)

        for rec in records:
            if rec.final_action == "accept":
                rounds_per_accept.append(len(rec.rounds))
            tradition_rounds[rec.tradition].append(len(rec.rounds))

            for i, rnd in enumerate(rec.rounds):
                if rnd.critic_findings:
                    # Track weak dimensions (score < 0.5)
                    for dim, score in rnd.critic_findings.layer_scores.items():
                        if score < 0.5:
                            weak_dims[dim] += 1

                    # Track repair success: if rerun improved the weak dim
                    if (rnd.decision and rnd.decision.action in ("rerun", "rerun_local")
                            and i + 1 < len(rec.rounds)):
                        next_rnd = rec.rounds[i + 1]
                        if next_rnd.critic_findings:
                            for dim, score in rnd.critic_findings.layer_scores.items():
                                if score < 0.5:
                                    repair_attempts += 1
                                    new_score = next_rnd.critic_findings.layer_scores.get(dim, 0)
                                    if new_score > score:
                                        repair_successes += 1

        insights: dict = {
            "total_trajectories": len(records),
            "common_weak_dimensions": [d for d, _ in weak_dims.most_common(5)],
        }

        if rounds_per_accept:
            insights["avg_rounds_to_accept"] = round(
                sum(rounds_per_accept) / len(rounds_per_accept), 2
            )

        if repair_attempts > 0:
            insights["repair_success_rate"] = round(repair_successes / repair_attempts, 3)

        # Per-tradition efficiency
        tradition_efficiency: dict[str, float] = {}
        for t, rounds_list in tradition_rounds.items():
            if rounds_list:
                tradition_efficiency[t] = round(sum(rounds_list) / len(rounds_list), 2)
        if tradition_efficiency:
            insights["tradition_avg_rounds"] = tradition_efficiency

        return insights

    # ------------------------------------------------------------------
    # P2-1: Queen strategy parameter evolution
    # ------------------------------------------------------------------

    _QUEEN_ADJ_STEP = 0.05       # per-cycle adjustment step
    _QUEEN_ADJ_CLAMP = 0.15      # absolute limit for cumulative adjustment

    def _evolve_queen_strategy(
        self, context: dict, patterns: list[Pattern]
    ) -> dict | None:
        """Derive ``queen_strategy`` from detected scoring patterns.

        Logic:
        - ``consistently_high`` patterns -> raise accept_threshold (can be stricter)
        - ``negative_feedback_dominant`` patterns -> lower accept_threshold (need diversity)
        - Adjustment +/-0.05 per cycle, clamped to [-0.15, +0.15].

        Returns a queen_strategy dict or *None* if nothing changed.
        """
        import time as _time

        prev = context.get("queen_strategy", {})
        old_adj: float = prev.get("accept_threshold_adjustment", 0.0)

        high_count = sum(
            1 for p in patterns if p.pattern_type == "consistently_high"
        )
        neg_count = sum(
            1 for p in patterns if p.pattern_type == "negative_feedback_dominant"
        )

        delta = 0.0
        if high_count > neg_count:
            # Quality is consistently good -> tighten threshold
            delta = self._QUEEN_ADJ_STEP
        elif neg_count > high_count:
            # Users unhappy -> relax threshold for diversity
            delta = -self._QUEEN_ADJ_STEP

        if delta == 0.0 and not prev:
            return None  # Nothing to write on first pass with no signal

        new_adj = max(-self._QUEEN_ADJ_CLAMP, min(self._QUEEN_ADJ_CLAMP, old_adj + delta))

        return {
            "accept_threshold_adjustment": round(new_adj, 4),
            "prefer_quality_over_speed": new_adj >= 0.0,
            "high_pattern_count": high_count,
            "negative_feedback_count": neg_count,
            "updated_at": _time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
