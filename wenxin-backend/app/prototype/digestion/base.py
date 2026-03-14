"""Base digester interface for the VULCA digestion pipeline.

Every digestion step should subclass ``BaseDigester`` and set a unique
``STEP_NAME``.  Registered digesters are auto-discovered and can be
queried via ``BaseDigester.list_digesters()``.

Example — adding a new digester::

    # digestion/sentiment_analyzer.py
    from app.prototype.digestion.base import BaseDigester, DigestContext

    class SentimentAnalyzer(BaseDigester):
        STEP_NAME = "sentiment"
        PRIORITY = 55

        def digest(self, sessions: list, ctx: DigestContext) -> DigestContext:
            # ... your logic here ...
            ctx.data["sentiment"] = {"positive_ratio": 0.72}
            return ctx

The ``ContextEvolver`` can then pick up your step automatically:

    for digester_cls in BaseDigester.get_ordered_digesters():
        digester = digester_cls()
        ctx = digester.digest(sessions, ctx)
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar

logger = logging.getLogger(__name__)


@dataclass
class DigestContext:
    """Shared context passed through the digestion pipeline.

    Each digester reads from and writes to ``data``, a free-form dict
    that ultimately gets persisted as ``evolved_context.json``.

    Additional typed fields (``sessions``, ``patterns``, ``clusters``,
    ``actions``) carry intermediate results between pipeline steps.
    The ``evolver`` reference allows step adapters to call private
    methods on the ``ContextEvolver`` instance when needed.
    """

    data: dict = field(default_factory=dict)
    session_count: int = 0
    changed: bool = False

    # Inter-step data carriers
    sessions: list = field(default_factory=list)
    patterns: list = field(default_factory=list)
    clusters: list = field(default_factory=list)
    actions: list = field(default_factory=list)

    # Reference to the ContextEvolver instance (for steps that wrap
    # private methods like _extract_layer_focus, _extract_trajectory_insights,
    # _evolve_queen_strategy, _generate_llm_insights).
    evolver: Any = None

    def set(self, key: str, value: object) -> None:
        """Write a key into the context, marking it changed."""
        self.data[key] = value
        self.changed = True

    def get(self, key: str, default: object = None) -> object:
        """Read a key from the context."""
        return self.data.get(key, default)


class BaseDigester(ABC):
    """Abstract base for all digestion steps.

    Subclasses must set ``STEP_NAME`` and implement ``digest()``.
    Setting ``STEP_NAME`` auto-registers the class into the digester
    registry via ``__init_subclass__``.

    Class attributes
    ----------------
    STEP_NAME : str
        Unique identifier for this step (empty = abstract, not registered).
    PRIORITY : int
        Execution order — lower values run earlier (default 100).
    ENABLED_BY_DEFAULT : bool
        Whether this step is included in ``get_ordered_digesters()``
        (default ``True``).
    """

    STEP_NAME: str = ""
    PRIORITY: int = 100
    ENABLED_BY_DEFAULT: bool = True

    # Auto-populated: step_name -> digester class
    _registry: ClassVar[dict[str, type[BaseDigester]]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if cls.STEP_NAME:
            existing = BaseDigester._registry.get(cls.STEP_NAME)
            if existing is not None and existing is not cls:
                logger.warning(
                    "BaseDigester: STEP_NAME '%s' already registered by %s, overriding with %s",
                    cls.STEP_NAME, existing.__name__, cls.__name__,
                )
            BaseDigester._registry[cls.STEP_NAME] = cls

    @abstractmethod
    def digest(self, sessions: list, ctx: DigestContext) -> DigestContext:
        """Run this digestion step.

        Parameters
        ----------
        sessions : list
            All sessions from the session store.
        ctx : DigestContext
            Shared context dict — read inputs from earlier steps,
            write outputs for later steps.

        Returns
        -------
        DigestContext
            The (potentially modified) context.
        """
        ...

    @classmethod
    def get_digester(cls, step_name: str) -> type[BaseDigester] | None:
        """Look up a registered digester by step name."""
        return cls._registry.get(step_name)

    @classmethod
    def get_ordered_digesters(cls) -> list[type[BaseDigester]]:
        """Return enabled digesters sorted by PRIORITY (ascending)."""
        return sorted(
            [d for d in cls._registry.values() if d.ENABLED_BY_DEFAULT],
            key=lambda d: (d.PRIORITY, d.STEP_NAME),
        )

    @classmethod
    def list_digesters(cls) -> list[dict]:
        """Return metadata for all registered digesters, ordered by priority.

        Each entry contains ``name``, ``priority``, and ``enabled`` keys.
        """
        all_digesters = sorted(cls._registry.values(), key=lambda d: (d.PRIORITY, d.STEP_NAME))
        return [
            {
                "name": d.STEP_NAME,
                "priority": d.PRIORITY,
                "enabled": d.ENABLED_BY_DEFAULT,
            }
            for d in all_digesters
        ]
