"""Select high-scoring sessions as few-shot examples for agent prompts.

Scans sessions.jsonl for high-scoring sessions, selects the best per
tradition (capped globally), and writes them to evolved_context.json
under the ``few_shot_examples`` key.  Agent prompts consume these via
:func:`~app.prototype.cultural_pipelines.cultural_weights.get_evolved_prompt_context`.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger("vulca")

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_SESSIONS_PATH = _DATA_DIR / "sessions.jsonl"
_EVOLVED_PATH = _DATA_DIR / "evolved_context.json"

# Selection criteria
MIN_SCORE_THRESHOLD = 0.75  # Minimum final_weighted_total to qualify
MAX_EXAMPLES_PER_TRADITION = 3  # Cap per tradition
MAX_TOTAL_EXAMPLES = 15  # Global cap


class FewShotUpdater:
    """Selects top sessions as few-shot examples and saves to evolved_context."""

    def __init__(
        self,
        sessions_path: str | None = None,
        evolved_path: str | None = None,
    ) -> None:
        self._sessions_path = Path(sessions_path).resolve() if sessions_path else _SESSIONS_PATH
        self._evolved_path = Path(evolved_path).resolve() if evolved_path else _EVOLVED_PATH

    def update(self) -> int:
        """Select best sessions as few-shot examples.

        Returns the count of examples selected and saved.
        """
        sessions = self._load_sessions()
        if not sessions:
            logger.debug("FewShotUpdater: no sessions found")
            return 0

        # Filter high-scoring sessions
        candidates = [s for s in sessions if self._get_score(s) >= MIN_SCORE_THRESHOLD]
        if not candidates:
            logger.debug("FewShotUpdater: no sessions above threshold %.2f", MIN_SCORE_THRESHOLD)
            return 0

        # Group by tradition, take top N per tradition
        by_tradition: dict[str, list[dict]] = {}
        for s in candidates:
            t = s.get("tradition", "default")
            by_tradition.setdefault(t, []).append(s)

        examples: list[dict] = []
        for tradition, tradition_sessions in by_tradition.items():
            # Sort by score descending
            sorted_sessions = sorted(
                tradition_sessions, key=self._get_score, reverse=True
            )
            for s in sorted_sessions[:MAX_EXAMPLES_PER_TRADITION]:
                examples.append(self._to_few_shot(s, tradition))

        # Global cap: keep highest-scoring across all traditions
        examples = sorted(examples, key=lambda e: e["score"], reverse=True)[
            :MAX_TOTAL_EXAMPLES
        ]

        # Save to evolved_context.json
        self._save_examples(examples)

        logger.info(
            "FewShotUpdater: selected %d examples from %d candidates",
            len(examples),
            len(candidates),
        )
        return len(examples)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_score(session: dict) -> float:
        """Extract weighted_total score from session.

        Checks ``final_weighted_total`` first (canonical field), then
        falls back to ``final_scores.weighted_total``.
        """
        # Canonical field on SessionDigest
        fwt = session.get("final_weighted_total")
        if isinstance(fwt, (int, float)) and fwt > 0:
            return float(fwt)
        # Fallback: nested in final_scores
        scores = session.get("final_scores", {})
        if isinstance(scores, dict):
            wt = scores.get("weighted_total")
            if isinstance(wt, (int, float)):
                return float(wt)
        return 0.0

    @staticmethod
    def _to_few_shot(session: dict, tradition: str) -> dict:
        """Convert session to a compact few-shot example (~50 tokens)."""
        return {
            "tradition": tradition,
            "subject": session.get("subject", ""),
            "intent": session.get("intent", ""),
            "score": FewShotUpdater._get_score(session),
            "session_id": session.get("session_id", ""),
            "key_strengths": FewShotUpdater._extract_strengths(session),
        }

    @staticmethod
    def _extract_strengths(session: dict) -> list[str]:
        """Extract which dimensions scored highest in this session."""
        strengths: list[str] = []
        scores = session.get("final_scores", {})
        if isinstance(scores, dict):
            for dim, val in scores.items():
                if dim in ("weighted_total", "final_weighted_total"):
                    continue
                if isinstance(val, (int, float)) and val >= 0.8:
                    strengths.append(dim)
        return strengths[:5]

    def _load_sessions(self) -> list[dict]:
        """Load sessions from local JSONL first, then SessionStore (DB) fallback."""
        _digestion_logger = logging.getLogger("vulca.digestion")
        # Primary: read local JSONL (works in tests + dev)
        if self._sessions_path.exists():
            _digestion_logger.info(
                "Loading sessions from local JSONL: %s (use SessionStore for production data)",
                self._sessions_path,
            )
            sessions: list[dict] = []
            for line in self._sessions_path.read_text(encoding="utf-8").strip().split("\n"):
                if line.strip():
                    try:
                        sessions.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            if sessions:
                return sessions

        # Fallback: SessionStore (Supabase DB in prod)
        try:
            from app.prototype.session.store import SessionStore
            return SessionStore.get().get_all()
        except Exception:
            return []

    def _save_examples(self, examples: list[dict]) -> None:
        """Merge few_shot_examples into evolved_context.json."""
        ctx: dict = {}
        if self._evolved_path.exists():
            try:
                ctx = json.loads(self._evolved_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass

        ctx["few_shot_examples"] = examples

        self._evolved_path.parent.mkdir(parents=True, exist_ok=True)
        self._evolved_path.write_text(
            json.dumps(ctx, indent=2, ensure_ascii=False), encoding="utf-8"
        )
