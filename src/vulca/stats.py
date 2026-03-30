"""Session statistics computation — pure functions, no I/O."""
from __future__ import annotations

import math
from typing import Any


def compute_session_stats(
    sessions: list[dict[str, Any]],
    *,
    tradition: str = "",
    since: str = "",
) -> dict[str, Any]:
    filtered = sessions
    if tradition:
        filtered = [s for s in filtered if s.get("tradition") == tradition]
    if since:
        try:
            from datetime import datetime
            ts = datetime.strptime(since, "%Y-%m-%d").timestamp()
            filtered = [s for s in filtered if s.get("created_at", 0) >= ts]
        except ValueError:
            pass

    total = len(filtered)
    by_mode: dict[str, int] = {}
    for s in filtered:
        mode = s.get("mode", "unknown")
        by_mode[mode] = by_mode.get(mode, 0) + 1

    trad_groups: dict[str, list[float]] = {}
    for s in filtered:
        t = s.get("tradition", "unknown")
        score = s.get("final_weighted_total", 0.0)
        trad_groups.setdefault(t, []).append(score)

    by_tradition = sorted(
        [{"name": name, "count": len(scores),
          "avg_score": round(sum(scores) / len(scores), 4) if scores else 0.0,
          "std": round(_std(scores), 4)}
         for name, scores in trad_groups.items()],
        key=lambda x: x["count"], reverse=True,
    )

    all_scores = [s.get("final_weighted_total", 0.0) for s in filtered if s.get("final_weighted_total") is not None]
    dist = _distribution(all_scores)

    low_scores = [
        {"session_id": s.get("session_id", ""), "score": s.get("final_weighted_total", 0.0), "tradition": s.get("tradition", "")}
        for s in filtered if (s.get("final_weighted_total") or 0.0) < 0.5
    ]
    failed = [
        {"session_id": s.get("session_id", ""), "status": s.get("status", ""), "tradition": s.get("tradition", "")}
        for s in filtered if s.get("status") not in ("completed", None, "")
    ]
    zero_rounds = [
        {"session_id": s.get("session_id", ""), "tradition": s.get("tradition", "")}
        for s in filtered if s.get("total_rounds", -1) == 0
    ]

    scored = [s for s in filtered if s.get("final_weighted_total") is not None]
    scored_sorted = sorted(scored, key=lambda s: s.get("final_weighted_total", 0.0), reverse=True)
    top = [{"session_id": s.get("session_id", ""), "score": s.get("final_weighted_total", 0.0), "tradition": s.get("tradition", "")} for s in scored_sorted[:5]]
    bottom = [{"session_id": s.get("session_id", ""), "score": s.get("final_weighted_total", 0.0), "tradition": s.get("tradition", "")} for s in reversed(scored_sorted[-5:])] if scored_sorted else []

    return {
        "total": total, "by_mode": by_mode, "by_tradition": by_tradition,
        "score_distribution": dist,
        "anomalies": {"low_scores": low_scores, "failed": failed, "zero_rounds": zero_rounds},
        "top_sessions": top, "bottom_sessions": bottom,
    }


def format_stats_text(stats: dict[str, Any]) -> str:
    lines = ["VULCA Session Statistics", "=" * 40]
    mode_str = ", ".join(f"{k}: {v}" for k, v in stats["by_mode"].items())
    lines.append(f"Total: {stats['total']} sessions ({mode_str})")
    lines.append("")
    lines.append("By tradition (top 10):")
    for t in stats["by_tradition"][:10]:
        lines.append(f"  {t['name']:25s} {t['count']:4d}  avg={t['avg_score']:.2f}  std={t['std']:.2f}")
    lines.append("")
    d = stats["score_distribution"]
    lines.append("Score distribution:")
    lines.append(f"  mean={d['mean']:.2f}  median={d['median']:.2f}  min={d['min']:.2f}  max={d['max']:.2f}  std={d['std']:.2f}")
    lines.append("")
    a = stats["anomalies"]
    lines.append("Anomalies:")
    lines.append(f"  Low scores (<0.5):       {len(a['low_scores'])}")
    lines.append(f"  Failed (not completed):  {len(a['failed'])}")
    lines.append(f"  Zero rounds:             {len(a['zero_rounds'])}")
    lines.append("")
    if stats["top_sessions"]:
        lines.append("Top 5: " + ", ".join(f"{s['session_id']}:{s['score']:.2f}" for s in stats["top_sessions"]))
    if stats["bottom_sessions"]:
        lines.append("Bottom 5: " + ", ".join(f"{s['session_id']}:{s['score']:.2f}" for s in stats["bottom_sessions"]))
    return "\n".join(lines)


def _std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))


def _distribution(values: list[float]) -> dict[str, float]:
    if not values:
        return {"mean": 0.0, "median": 0.0, "min": 0.0, "max": 0.0, "std": 0.0}
    sorted_v = sorted(values)
    n = len(sorted_v)
    median = sorted_v[n // 2] if n % 2 else (sorted_v[n // 2 - 1] + sorted_v[n // 2]) / 2
    return {
        "mean": round(sum(values) / n, 4), "median": round(median, 4),
        "min": round(min(values), 4), "max": round(max(values), 4),
        "std": round(_std(values), 4),
    }
