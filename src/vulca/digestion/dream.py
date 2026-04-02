"""Dream-style evolution consolidation.

Inspired by Claude Code's autoDream system — a periodic background process
that consolidates session data into durable evolution insights through
four phases: Orient → Gather → Consolidate → Prune.

Gate: 24h + 10 new sessions since last consolidation.
"""

from __future__ import annotations

import json
import logging
import os
import time
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)

# Gate thresholds (inspired by Claude Code Dream's triple-gate)
_MIN_HOURS = 24
_MIN_NEW_SESSIONS = 10
_LOCK_FILE = ".dream-lock"


class DreamConsolidator:
    """Four-phase evolution consolidation engine."""

    def __init__(self, *, data_dir: str = ""):
        self._data_dir = Path(data_dir) if data_dir else Path.home() / ".vulca" / "data"

    def should_run(self) -> bool:
        """Check triple-gate: time + sessions + no lock."""
        # Gate 1: Time
        last_run = self._load_last_run_time()
        hours_since = (time.time() - last_run) / 3600
        if hours_since < _MIN_HOURS:
            return False

        # Gate 2: Session count
        new_sessions = self._count_new_sessions(last_run)
        if new_sessions < _MIN_NEW_SESSIONS:
            return False

        # Gate 3: No concurrent lock
        lock_path = self._data_dir / _LOCK_FILE
        if lock_path.exists():
            # Check staleness (1 hour)
            try:
                lock_age = time.time() - lock_path.stat().st_mtime
                if lock_age < 3600:
                    return False
            except OSError:
                pass

        return True

    def _acquire_lock(self) -> bool:
        """Atomically acquire the lock file using O_CREAT|O_EXCL.

        Returns True if lock acquired, False if another process holds it.
        Stale locks (>1h) are broken and re-acquired.
        """
        lock_path = self._data_dir / _LOCK_FILE
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(int(time.time())).encode())
            os.close(fd)
            return True
        except FileExistsError:
            # Check staleness
            try:
                lock_age = time.time() - lock_path.stat().st_mtime
                if lock_age >= 3600:
                    lock_path.unlink(missing_ok=True)
                    return self._acquire_lock()
            except OSError:
                pass
            return False

    def run(self) -> dict:
        """Execute four-phase consolidation. Returns summary of changes."""
        self._data_dir.mkdir(parents=True, exist_ok=True)
        lock_path = self._data_dir / _LOCK_FILE

        if not self._acquire_lock():
            return {"status": "skipped_locked"}

        try:

            # Phase 1: Orient
            orientation = self._phase_orient()

            # Phase 2: Gather
            signals = self._phase_gather(orientation)

            # Phase 3: Consolidate
            changes = self._phase_consolidate(signals, orientation)

            # Phase 4: Prune
            pruned = self._phase_prune()

            # Record completion
            self._record_completion()

            return {
                "status": "completed",
                "traditions_updated": list(changes.keys()),
                "sessions_analyzed": signals.get("total_sessions", 0),
                "insights_written": sum(1 for v in changes.values() if v),
                "pruned_count": pruned,
            }
        except Exception as e:
            logger.error("Dream consolidation failed: %s", e)
            # Rollback lock
            lock_path.unlink(missing_ok=True)
            return {"status": "failed", "error": str(e)}
        finally:
            lock_path.unlink(missing_ok=True)

    def _phase_orient(self) -> dict:
        """Phase 1: Read current evolution state."""
        evolved_path = self._data_dir / "evolved_context.json"
        evolved = {}
        if evolved_path.exists():
            try:
                evolved = json.loads(evolved_path.read_text())
            except (json.JSONDecodeError, OSError):
                pass

        # Scan per-tradition insight files
        evolved_dir = self._data_dir / "evolved"
        existing_traditions = []
        if evolved_dir.exists():
            existing_traditions = [d.name for d in evolved_dir.iterdir() if d.is_dir()]

        return {
            "evolved_context": evolved,
            "existing_traditions": existing_traditions,
            "last_evolved_at": evolved.get("_meta", {}).get("last_evolved_at", 0),
        }

    def _phase_gather(self, orientation: dict) -> dict:
        """Phase 2: Collect new signals from sessions."""
        sessions_path = self._data_dir / "sessions.jsonl"
        if not sessions_path.exists():
            return {"total_sessions": 0, "by_tradition": {}}

        last_evolved = orientation["last_evolved_at"]
        by_tradition = defaultdict(list)
        total = 0

        for line in sessions_path.read_text().strip().split("\n"):
            if not line.strip():
                continue
            try:
                session = json.loads(line)
                if session.get("timestamp", 0) > last_evolved:
                    tradition = session.get("tradition", "default")
                    by_tradition[tradition].append(session)
                    total += 1
            except json.JSONDecodeError:
                continue

        return {"total_sessions": total, "by_tradition": dict(by_tradition)}

    def _phase_consolidate(self, signals: dict, orientation: dict) -> dict:
        """Phase 3: Update per-tradition insights and evolved_context."""
        changes = {}
        by_tradition = signals.get("by_tradition", {})

        for tradition, sessions in by_tradition.items():
            if len(sessions) < 2:
                continue

            # Compute dimension statistics
            dim_sums = defaultdict(float)
            dim_counts = defaultdict(int)
            deviation_counts = defaultdict(lambda: defaultdict(int))
            score_history = []
            mode_counts = {"strict": 0, "reference": 0}

            for s in sessions:
                scores = s.get("final_scores") or s.get("scores") or {}
                wt = s.get("weighted_total", 0)
                score_history.append({
                    "session_id": s.get("session_id", ""),
                    "weighted_total": wt,
                    "timestamp": s.get("timestamp", 0),
                })

                for dim in ["L1", "L2", "L3", "L4", "L5"]:
                    val = scores.get(dim)
                    if val is not None:
                        dim_sums[dim] += float(val)
                        dim_counts[dim] += 1

                    dev = s.get("deviations", {}).get(dim, "traditional")
                    deviation_counts[dim][dev] += 1

                mode = s.get("eval_mode", "strict")
                mode_counts[mode] = mode_counts.get(mode, 0) + 1

            # Compute averages
            dim_avgs = {}
            for dim in ["L1", "L2", "L3", "L4", "L5"]:
                if dim_counts[dim] > 0:
                    dim_avgs[dim] = round(dim_sums[dim] / dim_counts[dim], 4)

            # Find weak dimensions (bottom 2)
            sorted_dims = sorted(dim_avgs.items(), key=lambda x: x[1])
            weak_dims = [d for d, _ in sorted_dims[:2]] if len(sorted_dims) >= 2 else []

            # Filter out intentional departures (>=30% ratio)
            total_strict = mode_counts.get("strict", 0) or 1
            innovation_signals = []
            filtered_weak = []
            for dim in weak_dims:
                intentional = deviation_counts[dim].get("intentional_departure", 0)
                if intentional / max(total_strict, 1) >= 0.3:
                    innovation_signals.append(dim)
                else:
                    filtered_weak.append(dim)

            overall_avg = round(sum(dim_avgs.values()) / max(len(dim_avgs), 1), 4)
            strict_ratio = mode_counts.get("strict", 0) / max(sum(mode_counts.values()), 1)

            # Write per-tradition insights
            insights = {
                "tradition": tradition,
                "updated_at": time.time(),
                "session_count": len(sessions),
                "total_sessions_all_time": len(sessions) + len(
                    [t for t in orientation.get("evolved_context", {}).get("traditions", {}).get(tradition, {}).get("score_history", [])
                     if isinstance(t, dict)]
                ),
                "score_history": score_history[-50:],  # Keep last 50
                "dimension_averages": dim_avgs,
                "deviation_patterns": {d: dict(v) for d, v in deviation_counts.items()},
                "weak_dimensions": filtered_weak,
                "innovation_signals": innovation_signals,
                "strict_ratio": round(strict_ratio, 3),
                "overall_avg": overall_avg,
            }

            insights_dir = self._data_dir / "evolved" / tradition
            insights_dir.mkdir(parents=True, exist_ok=True)
            (insights_dir / "insights.json").write_text(json.dumps(insights, indent=2))
            changes[tradition] = True
            logger.info("Dream: consolidated %d sessions for %s (avg=%.3f)", len(sessions), tradition, overall_avg)

        return changes

    def _phase_prune(self) -> int:
        """Phase 4: Clean up stale data."""
        pruned = 0
        evolved_dir = self._data_dir / "evolved"
        if not evolved_dir.exists():
            return 0

        for tradition_dir in evolved_dir.iterdir():
            if not tradition_dir.is_dir():
                continue
            insights_path = tradition_dir / "insights.json"
            if not insights_path.exists():
                continue
            try:
                insights = json.loads(insights_path.read_text())
                # Prune score_history beyond 50 entries
                history = insights.get("score_history", [])
                if len(history) > 50:
                    insights["score_history"] = history[-50:]
                    insights_path.write_text(json.dumps(insights, indent=2))
                    pruned += 1
            except (json.JSONDecodeError, OSError):
                continue

        return pruned

    def _load_last_run_time(self) -> float:
        meta_path = self._data_dir / "evolved" / "_dream_meta.json"
        if not meta_path.exists():
            return 0.0
        try:
            return float(json.loads(meta_path.read_text()).get("last_run", 0))
        except (json.JSONDecodeError, ValueError, OSError):
            return 0.0

    def _count_new_sessions(self, since: float) -> int:
        sessions_path = self._data_dir / "sessions.jsonl"
        if not sessions_path.exists():
            return 0
        count = 0
        for line in sessions_path.read_text().strip().split("\n"):
            if not line.strip():
                continue
            try:
                s = json.loads(line)
                if s.get("timestamp", 0) > since:
                    count += 1
            except json.JSONDecodeError:
                continue
        return count

    def _record_completion(self):
        meta_dir = self._data_dir / "evolved"
        meta_dir.mkdir(parents=True, exist_ok=True)
        (meta_dir / "_dream_meta.json").write_text(json.dumps({
            "last_run": time.time(),
            "version": 1,
        }))
