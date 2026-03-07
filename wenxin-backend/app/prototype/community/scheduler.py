"""Simple scheduler that runs community agents on configurable intervals.

Usage::

    from app.prototype.community.scheduler import AgentScheduler
    from app.prototype.community.sim_user_agent import SimUserAgent

    scheduler = AgentScheduler()
    scheduler.register(SimUserAgent("casual_creator"), interval_seconds=300)
    scheduler.register(SimUserAgent("pro_designer"), interval_seconds=600)

    # One-shot (e.g. from a cron job / Cloud Run Job)
    await scheduler.run_once()

    # Or long-running loop
    await scheduler.run_forever()

Environment variables
---------------------
VULCA_AGENT_TICK : int
    Base tick interval in seconds for ``run_forever`` (default 60).
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field

from app.prototype.community.base_agent import BaseAgent

logger = logging.getLogger(__name__)

_DEFAULT_TICK = int(os.environ.get("VULCA_AGENT_TICK", "60"))


@dataclass
class _Registration:
    """Internal bookkeeping for a registered agent."""

    agent: BaseAgent
    interval_seconds: float
    last_run: float = 0.0


@dataclass
class AgentScheduler:
    """Run registered agents on fixed intervals."""

    tick_seconds: float = field(default_factory=lambda: float(_DEFAULT_TICK))
    _registrations: list[_Registration] = field(default_factory=list, repr=False)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, agent: BaseAgent, interval_seconds: float = 300) -> None:
        """Add *agent* to the schedule with the given interval."""
        self._registrations.append(
            _Registration(agent=agent, interval_seconds=interval_seconds)
        )
        logger.info(
            "Registered agent %s with interval %ss",
            agent.name,
            interval_seconds,
        )

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def run_once(self) -> list[dict]:
        """Run all *due* agents once and return their summaries."""
        now = time.monotonic()
        results: list[dict] = []

        for reg in self._registrations:
            elapsed = now - reg.last_run
            if elapsed < reg.interval_seconds and reg.last_run > 0:
                continue
            if not reg.agent.should_run():
                continue

            logger.info("Running agent %s", reg.agent.name)
            try:
                summary = await reg.agent.run_cycle()
                results.append({"agent": reg.agent.name, **summary})
            except Exception as exc:
                logger.exception("Agent %s failed", reg.agent.name)
                results.append({"agent": reg.agent.name, "status": "error", "error": str(exc)})

            reg.last_run = time.monotonic()

        return results

    async def run_forever(self) -> None:  # pragma: no cover
        """Loop indefinitely, ticking every :attr:`tick_seconds`.

        Designed for long-running processes (e.g. a background worker).
        """
        logger.info(
            "AgentScheduler starting run_forever (tick=%ss, agents=%d)",
            self.tick_seconds,
            len(self._registrations),
        )
        while True:
            try:
                results = await self.run_once()
                if results:
                    logger.info("Tick completed: %d agents ran", len(results))
            except Exception:
                logger.exception("Scheduler tick error")
            await asyncio.sleep(self.tick_seconds)
