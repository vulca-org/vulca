"""MetaOrchestrator — top-level entry point for NoCode evaluation.

Orchestrates: Intent → Skills → Pipeline → Results → Feedback.
This is the default entry point for Layer 0 (NoCode) users.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

from app.prototype.intent.config_translator import ConfigTranslator, PipelineConfig
from app.prototype.intent.intent_agent import IntentAgent
from app.prototype.intent.result_formatter import ResultFormatter
from app.prototype.intent.skill_selector import SkillPlan, SkillSelector
from app.prototype.intent.types import IntentResult, ResultCard

logger = logging.getLogger(__name__)

__all__ = ["MetaOrchestrator", "OrchestrationResult"]


@dataclass
class OrchestrationResult:
    """Full result from MetaOrchestrator.run()."""

    # Result card (Layer 0 output)
    result_card: ResultCard

    # Pipeline details
    scores: dict[str, float] = field(default_factory=dict)
    rationales: dict[str, str] = field(default_factory=dict)
    weighted_total: float = 0.0
    tradition_used: str = "default"
    risk_flags: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    evidence_summary: dict | None = None

    # Intent layer metadata
    intent: IntentResult | None = None
    skill_plan: SkillPlan | None = None
    pipeline_config: PipelineConfig | None = None

    # Extra skill results
    extra_skill_results: list[dict] = field(default_factory=list)

    # Timing
    latency_ms: int = 0
    cost_usd: float = 0.0

    def to_dict(self) -> dict:
        return {
            "result_card": {
                "score": self.result_card.score,
                "summary": self.result_card.summary,
                "risk_level": self.result_card.risk_level,
                "dimensions": self.result_card.dimensions,
                "recommendations": self.result_card.recommendations,
                "tradition_used": self.result_card.tradition_used,
            },
            "scores": self.scores,
            "weighted_total": self.weighted_total,
            "tradition_used": self.tradition_used,
            "risk_flags": self.risk_flags,
            "recommendations": self.recommendations,
            "intent": {
                "tradition": self.intent.tradition,
                "context": self.intent.context,
                "confidence": self.intent.confidence,
            } if self.intent else None,
            "skills_used": self.skill_plan.skill_names() if self.skill_plan else [],
            "extra_skill_results": self.extra_skill_results,
            "latency_ms": self.latency_ms,
            "cost_usd": self.cost_usd,
        }


class MetaOrchestrator:
    """Top-level orchestrator: Intent → Skills → Pipeline → Results.

    Usage::

        orch = MetaOrchestrator.get_instance()
        result = await orch.run(
            user_input="Check this for Japanese market",
            image_path="/tmp/artwork.png",
        )
        print(result.result_card.summary)
    """

    _instance: MetaOrchestrator | None = None

    def __init__(self):
        self.intent_agent = IntentAgent.get()
        self.skill_selector = SkillSelector()
        self.config_translator = ConfigTranslator()
        self.formatter = ResultFormatter()

    @classmethod
    def get_instance(cls) -> MetaOrchestrator:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def run(
        self,
        user_input: str,
        image_path: str,
        subject: str = "",
    ) -> OrchestrationResult:
        """Full NoCode evaluation flow.

        1. Parse intent (~1-2s)
        2. Select skills (<10ms)
        3. Translate to pipeline config (<1ms)
        4. Execute VLM scoring (~5-30s)
        5. Run extra skills in parallel (~5-15s)
        6. Format result card
        """
        t0 = time.monotonic()

        # 1. Parse intent
        intent = await self.intent_agent.resolve(user_input)
        logger.info("MetaOrchestrator: intent resolved → tradition=%s (%.2f)",
                     intent.tradition, intent.confidence)

        # 2. Select skills
        plan = self.skill_selector.select(intent)

        # 3. Translate to pipeline config
        config = self.config_translator.translate(plan)

        # 4. Execute core VLM scoring
        scores, rationales, weighted_total, risk_flags, evidence_summary = (
            await self._run_vlm_scoring(config, image_path, subject or user_input)
        )

        # 5. Run extra skills (brand, audience, trend) in parallel
        extra_results = await self._run_extra_skills(
            config.extra_skills, image_path, plan.context
        )

        # 6. Build recommendations
        recommendations = self._build_recommendations(scores, risk_flags)

        # 7. Format result card
        response_data = {
            "scores": scores,
            "weighted_total": weighted_total,
            "tradition_used": config.tradition,
            "recommendations": recommendations,
            "risk_flags": risk_flags,
        }
        # ResultFormatter.format expects an EvaluateResponse-like object
        # Use a simple duck-type approach
        result_card = ResultCard(
            score=weighted_total,
            summary=self._generate_summary(weighted_total, risk_flags),
            risk_level="low" if len(risk_flags) == 0 else "medium" if len(risk_flags) <= 2 else "high",
            dimensions=scores,
            recommendations=recommendations,
            tradition_used=config.tradition,
        )

        elapsed_ms = int((time.monotonic() - t0) * 1000)

        return OrchestrationResult(
            result_card=result_card,
            scores=scores,
            rationales=rationales,
            weighted_total=weighted_total,
            tradition_used=config.tradition,
            risk_flags=risk_flags,
            recommendations=recommendations,
            evidence_summary=evidence_summary,
            intent=intent,
            skill_plan=plan,
            pipeline_config=config,
            extra_skill_results=extra_results,
            latency_ms=elapsed_ms,
        )

    async def _run_vlm_scoring(
        self,
        config: PipelineConfig,
        image_path: str,
        subject: str,
    ) -> tuple[dict, dict, float, list[str], dict | None]:
        """Run the core VLM-based L1-L5 scoring."""
        from app.prototype.agents.vlm_critic import VLMCritic

        scores: dict[str, float] = {}
        rationales: dict[str, str] = {}
        risk_flags: list[str] = []
        evidence_summary: dict | None = None

        dim_to_label = {
            "visual_perception": "L1",
            "technical_analysis": "L2",
            "cultural_context": "L3",
            "critical_interpretation": "L4",
            "philosophical_aesthetic": "L5",
        }

        if not config.enable_vlm:
            # No VLM needed, return empty scores
            return scores, rationales, 0.0, risk_flags, None

        vlm = VLMCritic.get()
        if not vlm.available:
            logger.warning("MetaOrchestrator: VLM not available")
            return scores, rationales, 0.0, risk_flags, None

        # Optional evidence gathering
        evidence_dict: dict = {}
        if config.include_evidence:
            try:
                from app.prototype.tools.scout_service import get_scout_service
                scout = get_scout_service()
                evidence = scout.gather_evidence(subject, config.tradition)
                evidence_dict = evidence.to_dict()
                evidence_summary = {
                    "sample_matches": len(evidence.sample_matches),
                    "terminology_hits": len(evidence.terminology_hits),
                    "taboo_violations": len(evidence.taboo_violations),
                }
                # Extract risk flags from taboo violations
                for tv in evidence_dict.get("taboo_violations", []):
                    desc = tv.get("description", tv.get("rule_id", "unknown"))
                    risk_flags.append(f"[{tv.get('severity', 'warn')}] {desc}")
            except Exception:
                logger.warning("Evidence gathering failed, continuing without")

        # VLM scoring
        raw_scores = vlm.score_image(
            image_path=image_path,
            subject=subject,
            cultural_tradition=config.tradition,
            evidence=evidence_dict or None,
        )

        if raw_scores is None:
            logger.error("VLM scoring returned None")
            return scores, rationales, 0.0, risk_flags, evidence_summary

        # Extract L1-L5 scores
        for dim_id, label in dim_to_label.items():
            scores[label] = round(raw_scores.get(label, 0.0), 4)
            rationales[label] = raw_scores.get(f"{label}_rationale", "")

        # Weighted total
        weighted_total = sum(
            config.critic_config.weights.get(dim_id, 0.0) * raw_scores.get(label, 0.0)
            for dim_id, label in dim_to_label.items()
        )

        return scores, rationales, round(weighted_total, 4), risk_flags, evidence_summary

    async def _run_extra_skills(
        self,
        skill_names: list[str],
        image_path: str,
        context: dict,
    ) -> list[dict]:
        """Run non-cultural skills via auto-registered executors."""
        if not skill_names:
            return []

        from app.prototype.skills.executors.base import BaseSkillExecutor

        # Ensure all built-in executors are imported so __init_subclass__
        # registers them.  The executors __init__.py re-exports them.
        import app.prototype.skills.executors  # noqa: F401

        results = []
        for name in skill_names:
            executor_cls = BaseSkillExecutor.get_executor(name)
            if executor_cls is None:
                logger.debug("No executor registered for skill %r", name)
                continue
            try:
                executor = executor_cls()
                result = await executor.execute(image_path, context)
                results.append({
                    "skill": result.skill_name,
                    "score": result.score,
                    "summary": result.summary,
                    "suggestions": result.suggestions,
                })
            except Exception:
                logger.warning("Extra skill %s failed", name, exc_info=True)

        return results

    @staticmethod
    def _build_recommendations(
        scores: dict[str, float],
        risk_flags: list[str],
    ) -> list[str]:
        """Generate recommendations from low scores and risk flags."""
        label_to_dim = {
            "L1": "visual_perception",
            "L2": "technical_analysis",
            "L3": "cultural_context",
            "L4": "critical_interpretation",
            "L5": "philosophical_aesthetic",
        }
        recs = []
        for label, score_val in scores.items():
            if score_val < 0.6:
                dim_name = label_to_dim.get(label, label)
                recs.append(
                    f"{label} ({dim_name}): score {score_val:.2f} — consider strengthening"
                )
        if risk_flags:
            recs.append(f"{len(risk_flags)} cultural risk(s) detected — review before use")
        return recs

    @staticmethod
    def _generate_summary(weighted_total: float, risk_flags: list[str]) -> str:
        """Generate a one-line summary based on score and risks."""
        if risk_flags:
            return f"Cultural risks detected ({len(risk_flags)} flags). Review before use."
        if weighted_total >= 0.85:
            return "Excellent quality. Ready for use."
        if weighted_total >= 0.70:
            return "Generally good with some areas for improvement."
        if weighted_total >= 0.50:
            return "Moderate quality. Several dimensions need attention."
        return "Low quality score. Significant improvements recommended."
