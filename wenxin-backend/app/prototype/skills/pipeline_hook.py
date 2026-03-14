"""Marketplace-Execution Bridge — run marketplace skills on pipeline artifacts.

Standalone bridge module that maps pipeline stages to skill executors.
Designed to be called by ``PipelineOrchestrator._run_skill_hook()`` but
works independently with no dependency on the orchestrator.

Usage::

    from app.prototype.skills.pipeline_hook import (
        run_pipeline_skills,
        list_available_pipeline_skills,
    )

    # Run default skills for the post_critic stage
    results = run_pipeline_skills("output/image.png", stage="post_critic")

    # Override skill selection
    results = run_pipeline_skills(
        "output/image.png",
        skill_names=["style_transfer", "brand_consistency"],
    )

    # Inspect available stage → skill mappings
    print(list_available_pipeline_skills())
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import asdict

logger = logging.getLogger(__name__)

__all__ = [
    "run_pipeline_skills",
    "list_available_pipeline_skills",
]

# ---------------------------------------------------------------------------
# Stage → skills mapping
# ---------------------------------------------------------------------------

_STAGE_SKILLS: dict[str, list[str]] = {
    "post_critic": ["composition_balance", "color_harmony"],
    "post_draft": ["style_transfer"],
    "post_accept": ["brand_consistency", "audience_fit", "trend_alignment"],
}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def list_available_pipeline_skills() -> dict[str, list[str]]:
    """Return stage -> skill_names mapping."""
    return dict(_STAGE_SKILLS)


def run_pipeline_skills(
    image_path: str,
    tradition: str = "default",
    stage: str = "post_critic",
    skill_names: list[str] | None = None,
    context: dict | None = None,
    timeout_per_skill: float = 30.0,
) -> list[dict]:
    """Run marketplace skills on pipeline artifacts.

    Args:
        image_path: Path to the generated image.
        tradition: Cultural tradition context.
        stage: Pipeline stage (post_critic, post_draft, post_accept).
        skill_names: Override skill selection (None = use stage defaults).
        context: Additional context dict passed to skills.
        timeout_per_skill: Timeout per skill execution in seconds.

    Returns:
        List of skill result dicts with keys: skill_name, success, result/error.
    """
    # Import executors package (not just base) to trigger __init_subclass__
    # registration of all concrete executors.
    import app.prototype.skills.executors  # noqa: F401 — triggers registration
    from app.prototype.skills.executors.base import BaseSkillExecutor

    # Determine which skills to run
    names = skill_names if skill_names is not None else _STAGE_SKILLS.get(stage, [])

    if not names:
        logger.debug(
            "No skills configured for stage=%r (skill_names=%r)", stage, skill_names
        )
        return []

    # Build context dict with tradition metadata
    ctx = dict(context or {})
    ctx.setdefault("tradition", tradition)
    ctx.setdefault("stage", stage)

    results: list[dict] = []

    for name in names:
        executor_cls = BaseSkillExecutor.get_executor(name)
        if executor_cls is None:
            logger.debug(
                "Skill executor not found for %r — skipping (stage=%s)", name, stage
            )
            results.append({
                "skill_name": name,
                "success": False,
                "error": f"Executor not found for skill: {name}",
            })
            continue

        try:
            executor = executor_cls()
            result = _run_async_skill(
                executor, image_path, ctx, timeout_per_skill
            )
            results.append({
                "skill_name": name,
                "success": True,
                "result": asdict(result),
            })
        except Exception as exc:
            logger.warning(
                "Skill %r failed on stage=%s: %s", name, stage, exc, exc_info=True
            )
            results.append({
                "skill_name": name,
                "success": False,
                "error": str(exc),
            })

    return results


# ---------------------------------------------------------------------------
# Async bridge helper
# ---------------------------------------------------------------------------


def _run_async_skill(
    executor: object,
    image_path: str,
    context: dict,
    timeout: float,
) -> object:
    """Bridge async executor.execute() into sync context.

    Handles three scenarios:
    1. No running event loop — use ``asyncio.run()``.
    2. Running event loop with ``nest_asyncio`` available — patch and run.
    3. Running event loop without ``nest_asyncio`` — run in a new thread.
    """

    async def _coro():
        return await asyncio.wait_for(
            executor.execute(image_path, context=context),  # type: ignore[attr-defined]
            timeout=timeout,
        )

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop is None:
        # No running event loop — simplest path
        return asyncio.run(_coro())

    # There is already a running event loop.
    # Try nest_asyncio first (common in Jupyter / Gradio contexts).
    try:
        import nest_asyncio

        nest_asyncio.apply()
        return loop.run_until_complete(_coro())
    except ImportError:
        pass

    # Fallback: run the coroutine in a separate thread with its own loop.
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(asyncio.run, _coro())
        return future.result(timeout=timeout + 5)
