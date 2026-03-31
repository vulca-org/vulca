"""Public evaluate API -- the main entry point for VULCA."""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

from vulca.types import EvalResult


async def aevaluate(
    image: str | Path,
    *,
    intent: str = "",
    tradition: str = "",
    subject: str = "",
    skills: list[str] | None = None,
    include_evidence: bool = False,
    api_key: str = "",
    mock: bool = False,
    mode: str = "strict",
    sparse: bool = False,
) -> EvalResult:
    """Evaluate an artwork image asynchronously.

    Parameters
    ----------
    image:
        File path, URL, or base64-encoded image string.
    intent:
        Natural language description of what to evaluate.
        If empty, a general evaluation is performed.
    tradition:
        Cultural tradition to use. If empty, auto-detected from intent.
        One of: default, chinese_xieyi, chinese_gongbi, western_academic,
        islamic_geometric, japanese_traditional, watercolor,
        african_traditional, south_asian.  Also accepts a file path to
        a custom YAML tradition file.
    subject:
        Optional subject/title of the artwork.
    skills:
        Extra skills to run: ``["brand", "audience", "trend"]``.
    include_evidence:
        Whether to gather cultural evidence before scoring.
    api_key:
        Google API key. If empty, reads from ``GOOGLE_API_KEY`` env var.
    mock:
        Use mock scoring (no API key required). Useful for testing.
    mode:
        Evaluation mode:
        - ``"strict"`` (default): Judge mode — scores reflect conformance.
        - ``"reference"``: Advisor mode — scores show alignment without judgment.
        - ``"fusion"``: Multi-tradition comparison (pass comma-separated traditions).

    Returns
    -------
    EvalResult
        Complete evaluation result with scores, rationales, suggestions, and recommendations.
    """
    from vulca._engine import Engine

    engine = Engine.get_instance(api_key=api_key, mock=mock)
    t0 = time.monotonic()
    result = await engine.run(
        image=str(image),
        intent=intent,
        tradition=tradition,
        subject=subject,
        skills=skills or [],
        include_evidence=include_evidence,
        mode=mode,
    )
    result.latency_ms = int((time.monotonic() - t0) * 1000)

    if sparse:
        from vulca.scoring.sparse import BriefIndexer
        indexer = BriefIndexer()
        activation = indexer.index(intent or subject or "", tradition=tradition)
        result.sparse_activation = {
            "active": activation.active,
            "skipped": activation.skipped,
            "method": activation.method,
        }

    return result


def evaluate(
    image: str | Path,
    *,
    intent: str = "",
    tradition: str = "",
    subject: str = "",
    skills: list[str] | None = None,
    include_evidence: bool = False,
    api_key: str = "",
    mock: bool = False,
    mode: str = "strict",
    sparse: bool = False,
) -> EvalResult:
    """Evaluate an artwork image (synchronous wrapper).

    See :func:`aevaluate` for parameter documentation.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    coro = aevaluate(
        image,
        intent=intent,
        tradition=tradition,
        subject=subject,
        skills=skills,
        include_evidence=include_evidence,
        api_key=api_key,
        mock=mock,
        mode=mode,
        sparse=sparse,
    )

    if loop and loop.is_running():
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)
