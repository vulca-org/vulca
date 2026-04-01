"""Parallel creation agents for multi-path exploration.

Inspired by Claude Code's fork agent pattern. Runs multiple pipeline
instances concurrently with different configurations (traditions, weights,
templates) and returns all results for comparison/selection.

Usage:
    results = await explore_parallel(
        subject="mountain landscape",
        variations=[
            {"tradition": "chinese_xieyi"},
            {"tradition": "chinese_gongbi"},
            {"tradition": "japanese_traditional"},
        ],
        provider="mock",
    )
    best = max(results, key=lambda r: r.final_scores.get("weighted_total", 0))
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from vulca.pipeline.engine import execute
from vulca.pipeline.templates import FAST
from vulca.pipeline.types import PipelineDefinition, PipelineInput, PipelineOutput

logger = logging.getLogger(__name__)


async def explore_parallel(
    subject: str,
    variations: list[dict[str, Any]],
    *,
    provider: str = "mock",
    template: PipelineDefinition | None = None,
    max_concurrent: int = 3,
    base_config: dict[str, Any] | None = None,
) -> list[PipelineOutput]:
    """Run multiple pipeline instances in parallel with different configs.

    Args:
        subject: The creation intent/subject.
        variations: List of config overrides. Each dict can contain:
            - tradition: str
            - eval_mode: str
            - node_params: dict
            - Any other PipelineInput field
        provider: Image provider name.
        template: Pipeline template (defaults to FAST for speed).
        max_concurrent: Maximum parallel pipelines (respects provider QPS).
        base_config: Default config applied to all variations.

    Returns:
        List of PipelineOutput, one per variation. Failed runs return
        PipelineOutput with status=FAILED.
    """
    defn = template or FAST
    sem = asyncio.Semaphore(max_concurrent)
    base = base_config or {}

    async def _run_one(variation: dict) -> PipelineOutput:
        async with sem:
            config = {**base, "subject": subject, "provider": provider, **variation}
            inp = PipelineInput(
                subject=config.pop("subject", subject),
                tradition=config.pop("tradition", "default"),
                provider=config.pop("provider", provider),
                eval_mode=config.pop("eval_mode", "strict"),
                max_rounds=config.pop("max_rounds", 1),
                node_params=config.pop("node_params", {}),
            )
            try:
                return await execute(defn, inp)
            except Exception as e:
                logger.warning("Parallel run failed for %s: %s", variation, e)
                return PipelineOutput(
                    session_id="",
                    status="failed",
                    final_scores={},
                    rounds=[],
                    events=[],
                )

    results = await asyncio.gather(*[_run_one(v) for v in variations])
    return list(results)


def rank_results(
    results: list[PipelineOutput], *, key: str = "weighted_total"
) -> list[PipelineOutput]:
    """Rank parallel results by score. Failed runs sorted to the end."""

    def _score(r: PipelineOutput) -> float:
        if not r.final_scores:
            return -1.0
        return r.final_scores.get(key, 0.0)

    return sorted(results, key=_score, reverse=True)
