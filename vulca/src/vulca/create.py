"""Create API -- local pipeline execution or remote API call."""

from __future__ import annotations

import asyncio
import os

from vulca.types import CreateResult


async def acreate(
    intent: str,
    *,
    tradition: str = "",
    subject: str = "",
    provider: str = "nb2",
    mode: str = "auto",
    base_url: str = "",
    api_key: str = "",
) -> CreateResult:
    """Create artwork via local pipeline or remote API (async).

    Parameters
    ----------
    intent:
        Natural language description of what to create.
    tradition:
        Cultural tradition. If empty, auto-detected.
    subject:
        Optional artwork subject/title.
    provider:
        Image generation provider (nb2 | mock).
    mode:
        Execution mode: 'local' (pipeline engine), 'remote' (API call),
        or 'auto' (local if mock, else remote).
    base_url:
        VULCA API base URL (remote mode). Defaults to VULCA_API_URL env.
    api_key:
        API key. Defaults to VULCA_API_KEY env.

    Returns
    -------
    CreateResult
        Complete creation result with session ID, rounds, and scores.
    """
    if mode == "local" or (mode == "auto" and provider == "mock"):
        return await _create_local(
            intent, tradition=tradition, subject=subject, provider=provider
        )
    return await _create_remote(
        intent,
        tradition=tradition,
        subject=subject,
        provider=provider,
        base_url=base_url,
        api_key=api_key,
    )


async def _create_local(
    intent: str,
    *,
    tradition: str = "",
    subject: str = "",
    provider: str = "mock",
) -> CreateResult:
    """Run the slim pipeline engine locally."""
    from vulca.pipeline.engine import execute
    from vulca.pipeline.hooks import default_on_complete
    from vulca.pipeline.templates import DEFAULT
    from vulca.pipeline.types import PipelineInput

    pipeline_input = PipelineInput(
        subject=subject or intent,
        intent=intent,
        tradition=tradition or "default",
        provider=provider,
    )

    output = await execute(DEFAULT, pipeline_input, on_complete=default_on_complete)

    return CreateResult(
        session_id=output.session_id,
        mode="create",
        tradition=output.tradition,
        scores=output.final_scores,
        weighted_total=output.weighted_total,
        best_candidate_id=output.best_candidate_id,
        best_image_url=output.best_image_url,
        total_rounds=output.total_rounds,
        rounds=[r.to_dict() for r in output.rounds],
        summary=output.summary,
        recommendations=output.recommendations,
        latency_ms=output.total_latency_ms,
        cost_usd=output.total_cost_usd,
        raw=output.to_dict(),
    )


async def _create_remote(
    intent: str,
    *,
    tradition: str = "",
    subject: str = "",
    provider: str = "nb2",
    base_url: str = "",
    api_key: str = "",
) -> CreateResult:
    """Call remote VULCA API for creation."""
    import httpx

    url = base_url or os.environ.get("VULCA_API_URL", "http://localhost:8001")
    key = api_key or os.environ.get("VULCA_API_KEY", "")

    body = {
        "intent": intent,
        "tradition": tradition or "default",
        "subject": subject or intent,
        "provider": provider,
        "stream": False,
    }

    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{url}/api/v1/create",
            json=body,
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()

    return CreateResult(
        session_id=data.get("session_id", ""),
        mode=data.get("mode", "create"),
        tradition=data.get("tradition", "default"),
        scores=data.get("scores") or {},
        weighted_total=data.get("weighted_total") or 0.0,
        best_candidate_id=data.get("best_candidate_id") or "",
        best_image_url=data.get("best_image_url") or "",
        total_rounds=data.get("total_rounds") or 0,
        rounds=data.get("rounds") or [],
        summary=data.get("summary") or "",
        recommendations=data.get("recommendations") or [],
        latency_ms=data.get("latency_ms", 0),
        cost_usd=data.get("cost_usd", 0.0),
        raw=data,
    )


def create(
    intent: str,
    *,
    tradition: str = "",
    subject: str = "",
    provider: str = "nb2",
    mode: str = "auto",
    base_url: str = "",
    api_key: str = "",
) -> CreateResult:
    """Create artwork (synchronous wrapper).

    See :func:`acreate` for parameter documentation.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    coro = acreate(
        intent,
        tradition=tradition,
        subject=subject,
        provider=provider,
        mode=mode,
        base_url=base_url,
        api_key=api_key,
    )

    if loop and loop.is_running():
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)
