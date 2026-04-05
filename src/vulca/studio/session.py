"""StudioSession -- state machine for creative studio sessions."""
from __future__ import annotations

import uuid
from enum import Enum
from pathlib import Path

import yaml

from vulca.studio.brief import Brief


class SessionState(Enum):
    INTENT = "intent"
    CONCEPT = "concept"
    GENERATE = "generate"
    EVALUATE = "evaluate"
    DONE = "done"


_STATE_ORDER = [
    SessionState.INTENT, SessionState.CONCEPT, SessionState.GENERATE,
    SessionState.EVALUATE, SessionState.DONE,
]


class StudioSession:
    def __init__(self, session_id: str, brief: Brief, state: SessionState, project_dir: Path):
        self.session_id = session_id
        self.brief = brief
        self.state = state
        self.project_dir = project_dir

    @classmethod
    def new(cls, intent: str, *, project_dir: str = "") -> StudioSession:
        sid = uuid.uuid4().hex[:8]
        brief = Brief.new(intent)
        brief.session_id = sid
        pdir = Path(project_dir) if project_dir else Path(f"./vulca-studio/{sid}")
        pdir.mkdir(parents=True, exist_ok=True)
        return cls(session_id=sid, brief=brief, state=SessionState.INTENT, project_dir=pdir)

    def advance_to(self, target: SessionState) -> None:
        current_idx = _STATE_ORDER.index(self.state)
        target_idx = _STATE_ORDER.index(target)
        if target_idx <= current_idx:
            raise ValueError(
                f"Cannot advance from {self.state.value} to {target.value} "
                f"(use rollback_to for going backward)")
        self.state = target

    def rollback_to(self, target: SessionState) -> None:
        self.state = target

    def save(self) -> Path:
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.brief.save(self.project_dir)
        state_file = self.project_dir / "session.yaml"
        state_file.write_text(
            yaml.dump({"session_id": self.session_id, "state": self.state.value},
                      allow_unicode=True), encoding="utf-8")
        return state_file

    async def accept(self, *, data_dir: str = "") -> dict:
        """Accept the artwork and trigger digestion.

        Digestion is fire-and-forget — failure does not block accept.
        Requires at least GENERATE state to have been reached.
        """
        min_state = SessionState.GENERATE
        if _STATE_ORDER.index(self.state) < _STATE_ORDER.index(min_state):
            raise ValueError(
                f"Cannot accept: session is in '{self.state.value}' state. "
                f"Must reach '{min_state.value}' first."
            )
        if self.state != SessionState.DONE:
            self.state = SessionState.DONE

        self.save()

        # Digestion (non-fatal)
        signals: dict = {}
        try:
            from vulca.digestion.store import StudioStore
            from vulca.digestion.signals import extract_signals

            store = StudioStore(data_dir=data_dir) if data_dir else StudioStore()
            store.save_session(self.brief, user_feedback="accept")
            signals = extract_signals(self.brief, user_feedback="accept")
        except Exception as exc:
            import logging
            logging.getLogger("vulca.studio").warning("Digestion failed (non-fatal): %s", exc)

        return {
            "status": "accepted",
            "session_id": self.session_id,
            "signals": signals,
        }

    async def on_complete(self, *, data_dir: str = "") -> None:
        """Trigger digestion after session completion."""
        from vulca.digestion.store import StudioStore
        from vulca.digestion.signals import extract_signals
        store = StudioStore(data_dir=data_dir) if data_dir else StudioStore()
        store.save_session(self.brief, user_feedback="complete")

    def on_complete_sync(self, *, data_dir: str = "") -> None:
        """Synchronous version of on_complete for non-async contexts."""
        from vulca.digestion.store import StudioStore
        store = StudioStore(data_dir=data_dir) if data_dir else StudioStore()
        store.save_session(self.brief, user_feedback="complete")

    @classmethod
    def load(cls, project_dir: str | Path) -> StudioSession:
        pdir = Path(project_dir)
        brief = Brief.load(pdir)
        state_file = pdir / "session.yaml"
        if state_file.exists():
            data = yaml.safe_load(state_file.read_text(encoding="utf-8"))
            state = SessionState(data.get("state", "intent"))
            sid = data.get("session_id", brief.session_id)
        else:
            state = SessionState.INTENT
            sid = brief.session_id
        return cls(session_id=sid, brief=brief, state=state, project_dir=pdir)
