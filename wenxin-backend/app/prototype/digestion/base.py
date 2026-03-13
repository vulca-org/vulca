"""Base digester interface for the VULCA digestion pipeline.

Every digestion step should subclass ``BaseDigester`` and set a unique
``STEP_NAME``.  Registered digesters are auto-discovered and can be
queried via ``BaseDigester.list_digesters()``.

Example — adding a new digester::

    # digestion/sentiment_analyzer.py
    from app.prototype.digestion.base import BaseDigester, DigestContext

    class SentimentAnalyzer(BaseDigester):
        STEP_NAME = "sentiment"

        def digest(self, sessions: list, ctx: DigestContext) -> DigestContext:
            # ... your logic here ...
            ctx.data["sentiment"] = {"positive_ratio": 0.72}
            return ctx

The ``ContextEvolver`` can then pick up your step automatically:

    for digester_cls in BaseDigester.list_digesters().values():
        digester = digester_cls()
        ctx = digester.digest(sessions, ctx)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class DigestContext:
    """Shared context passed through the digestion pipeline.

    Each digester reads from and writes to ``data``, a free-form dict
    that ultimately gets persisted as ``evolved_context.json``.
    """

    data: dict = field(default_factory=dict)
    session_count: int = 0
    changed: bool = False

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
    """

    STEP_NAME: str = ""

    # Auto-populated: step_name -> digester class
    _registry: dict[str, type[BaseDigester]] = {}

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        if cls.STEP_NAME:
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
    def list_digesters(cls) -> dict[str, type[BaseDigester]]:
        """Return all registered digesters."""
        return dict(cls._registry)
