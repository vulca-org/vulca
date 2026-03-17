"""Unified session entry point -- auto-routes between evaluate and create.

Has image -> vulca.evaluate()
No image  -> vulca.create()
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from vulca.types import CreateResult, EvalResult


async def asession(
    intent: str,
    *,
    image: str | Path | None = None,
    tradition: str = "",
    subject: str = "",
    api_key: str = "",
    base_url: str = "",
) -> EvalResult | CreateResult:
    """Unified session -- routes to evaluate or create based on image presence.

    Parameters
    ----------
    intent:
        Natural language intent.
    image:
        Image file path or URL. If provided, runs evaluate mode.
        If None, runs create mode.
    tradition:
        Cultural tradition.
    subject:
        Artwork subject/title.
    api_key:
        API key for evaluate mode (Google) or create mode (VULCA API).
    base_url:
        Base URL for create mode API.

    Returns
    -------
    EvalResult | CreateResult
        Evaluation or creation result.
    """
    if image is not None:
        from vulca.evaluate import aevaluate
        return await aevaluate(
            str(image),
            intent=intent,
            tradition=tradition,
            subject=subject,
            api_key=api_key,
        )
    else:
        from vulca.create import acreate
        return await acreate(
            intent,
            tradition=tradition,
            subject=subject,
            base_url=base_url,
            api_key=api_key,
        )


def session(
    intent: str,
    *,
    image: str | Path | None = None,
    tradition: str = "",
    subject: str = "",
    api_key: str = "",
    base_url: str = "",
) -> EvalResult | CreateResult:
    """Unified session (synchronous wrapper).

    See :func:`asession` for parameter documentation.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(
                asyncio.run,
                asession(
                    intent,
                    image=image,
                    tradition=tradition,
                    subject=subject,
                    api_key=api_key,
                    base_url=base_url,
                ),
            )
            return future.result()
    else:
        return asyncio.run(
            asession(
                intent,
                image=image,
                tradition=tradition,
                subject=subject,
                api_key=api_key,
                base_url=base_url,
            )
        )
