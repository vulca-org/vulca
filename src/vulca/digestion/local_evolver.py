"""Local evolution -- reads JSONL sessions, writes evolved_context.json."""
from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger("vulca.digestion")

_DEFAULT_DATA_DIR = Path.home() / ".vulca" / "data"
_MIN_SESSIONS = 5
_MIN_FEEDBACK = 3
_ADJUSTMENT = 0.05


class LocalEvolver:
    """Lightweight evolver that reads local JSONL and writes evolved_context.json."""

    def __init__(self, *, data_dir: str = ""):
        self.data_dir = Path(data_dir) if data_dir else _DEFAULT_DATA_DIR

    def evolve(self) -> dict | None:
        """Run evolution on local sessions. Returns evolved context or None if insufficient data."""
        sessions = self._load_sessions()
        if not sessions:
            return None

        # Filter sessions with real feedback
        feedback_sessions = [s for s in sessions if s.get("user_feedback") in ("accepted", "rejected")]
        if len(feedback_sessions) < _MIN_FEEDBACK:
            return None
        if len(sessions) < _MIN_SESSIONS:
            return None

        # Group by tradition
        by_tradition: dict[str, list[dict]] = defaultdict(list)
        for s in feedback_sessions:
            tradition = s.get("tradition", "default")
            by_tradition[tradition].append(s)

        # Build evolved context
        evolved: dict = {"traditions": {}}
        for tradition, tradition_sessions in by_tradition.items():
            if len(tradition_sessions) < 2:
                continue

            # Find weak dimensions (average score < 0.5)
            dim_totals: dict[str, float] = defaultdict(float)
            dim_counts: dict[str, int] = defaultdict(int)
            for s in tradition_sessions:
                scores = s.get("final_scores", {})
                for dim, score in scores.items():
                    if isinstance(score, (int, float)):
                        dim_totals[dim] += score
                        dim_counts[dim] += 1

            dim_avgs = {d: dim_totals[d] / dim_counts[d] for d in dim_totals if dim_counts[d] > 0}
            weak_dims = [d for d, avg in dim_avgs.items() if avg < 0.5]

            evolved["traditions"][tradition] = {
                "session_count": len(tradition_sessions),
                "dimension_averages": {d: round(v, 3) for d, v in dim_avgs.items()},
                "weak_dimensions": weak_dims,
                "weight_adjustments": {d: _ADJUSTMENT for d in weak_dims},
            }

        # Write to file
        evolved_path = self.data_dir / "evolved_context.json"
        evolved_path.parent.mkdir(parents=True, exist_ok=True)
        evolved_path.write_text(json.dumps(evolved, indent=2, ensure_ascii=False))
        logger.debug("Local evolution written to %s", evolved_path)

        return evolved

    def _load_sessions(self) -> list[dict]:
        """Load sessions from local JSONL."""
        sessions_file = self.data_dir / "sessions.jsonl"
        if not sessions_file.exists():
            return []
        sessions = []
        for line in sessions_file.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    sessions.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return sessions
