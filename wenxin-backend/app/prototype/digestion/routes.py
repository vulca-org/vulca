"""Digestion system API routes."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from fastapi import APIRouter

from app.prototype.digestion.aggregator import DigestAggregator
from app.prototype.digestion.context_evolver import ContextEvolver
from app.prototype.digestion.pattern_detector import PatternDetector
from app.prototype.digestion.preference_learner import PreferenceLearner
from app.prototype.session.store import SessionStore

logger = logging.getLogger("vulca")

digestion_router = APIRouter(prefix="/api/v1/digestion", tags=["digestion"])


@digestion_router.get("/status")
async def digestion_status() -> dict:
    """Return current digestion system status and aggregate stats."""
    store = SessionStore.get()
    aggregator = DigestAggregator(store)

    stats = aggregator.aggregate()

    # Load evolved context for v2 data
    context_path = Path(__file__).resolve().parent.parent / "data" / "evolved_context.json"
    cultures: dict = {}
    prompt_contexts: dict = {}
    feature_space: dict = {}
    if context_path.exists():
        try:
            with open(context_path, "r", encoding="utf-8") as f:
                ctx = json.load(f)
            cultures = ctx.get("cultures", {})
            prompt_contexts = ctx.get("prompt_contexts", {})
            feature_space = ctx.get("feature_space", {})
        except Exception:
            pass

    return {
        "total_sessions": store.count(),
        "traditions": {k: v.to_dict() for k, v in stats.items()},
        "cultures": cultures,
        "prompt_contexts": prompt_contexts,
        "feature_space": feature_space,
    }


@digestion_router.get("/report")
async def digestion_report() -> dict:
    """Return a summary report of the evolved context state.

    Replaces the old evolution/ AdminAgent weekly report with a
    lightweight, digestion-native summary.
    """
    evolver = ContextEvolver()
    return evolver.generate_report()


@digestion_router.post("/run")
async def run_digestion() -> dict:
    """Trigger a full digestion + evolution cycle."""
    # Sync inline feedback from sessions before running digestion
    from app.prototype.feedback.feedback_store import FeedbackStore
    from app.prototype.digestion.feature_extractor import backfill_missing_features

    try:
        backfill_missing_features()
        FeedbackStore.get().sync_from_sessions()
    except Exception:
        logger.debug("Pre-digestion sync failed (non-fatal)")

    evolver = ContextEvolver()
    result = evolver.evolve()

    # Update few-shot examples from high-scoring sessions
    few_shot_count = 0
    try:
        from app.prototype.digestion.few_shot_updater import FewShotUpdater
        few_shot_count = FewShotUpdater().update()
    except Exception:
        logger.debug("Few-shot update failed (non-fatal)")

    detector = PatternDetector()
    patterns = detector.detect()

    learner = PreferenceLearner()
    preferences = learner.learn()

    return {
        "evolution": result.to_dict(),
        "patterns": [p.to_dict() for p in patterns],
        "preferences": {k: v.to_dict() for k, v in preferences.items()},
        "few_shot_examples_count": few_shot_count,
    }
