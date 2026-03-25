"""Layer 0 Preloader — pre-session intelligence.

Loads relevant context BEFORE a session starts, based on:
1. Intent keyword → tradition matching
2. Similar past sessions from JSONL store
3. Aggregated prompt hints from past session scores
"""
from __future__ import annotations

from typing import Any

from vulca.digestion.storage import JsonlStudioStorage

# Reuse tradition hints from IntentPhase
_INTENT_TRADITION_HINTS: dict[str, str] = {
    "水墨": "chinese_xieyi", "写意": "chinese_xieyi", "山水": "chinese_xieyi",
    "ink wash": "chinese_xieyi", "国画": "chinese_xieyi", "江南": "chinese_xieyi",
    "工笔": "chinese_gongbi", "gongbi": "chinese_gongbi",
    "浮世绘": "japanese_traditional", "ukiyo": "japanese_traditional",
    "油画": "western_academic", "oil painting": "western_academic",
    "水彩": "watercolor", "watercolor": "watercolor",
    "几何": "islamic_geometric", "geometric": "islamic_geometric",
    "抽象": "contemporary_art", "abstract": "contemporary_art",
    "商业": "brand_design", "品牌": "brand_design", "brand": "brand_design",
    "摄影": "photography", "photo": "photography",
}


def preload_intelligence(
    intent: str,
    *,
    data_dir: str = "",
    user_id: str = "",
) -> dict[str, Any]:
    """Load pre-session intelligence from local store.

    Returns a context dict with suggested traditions, similar sessions, and prompt hints.
    """
    ctx: dict[str, Any] = {
        "suggested_traditions": [],
        "similar_session_count": 0,
        "prompt_hints": [],
    }

    # 1. Keyword-based tradition suggestions (always works, even cold start)
    intent_lower = intent.lower()
    suggested = []
    for keyword, tradition in _INTENT_TRADITION_HINTS.items():
        if keyword in intent_lower and tradition not in suggested:
            suggested.append(tradition)
    ctx["suggested_traditions"] = suggested

    # 2. Load similar sessions from history
    store = JsonlStudioStorage(data_dir=data_dir)
    all_sessions = store.get_sessions()

    if all_sessions:
        # Simple keyword overlap similarity
        intent_chars = set(intent_lower)
        similar = []
        for session in all_sessions:
            session_intent = session.get("brief", {}).get("intent", "").lower()
            if not session_intent:
                continue
            overlap = len(intent_chars & set(session_intent)) / max(len(intent_chars), 1)
            if overlap > 0.3:
                similar.append(session)

        ctx["similar_session_count"] = len(similar)

        # Boost tradition suggestions from history
        for session in similar:
            for t in session.get("traditions", []):
                if t and t not in ctx["suggested_traditions"]:
                    ctx["suggested_traditions"].append(t)

        # 3. Aggregate prompt hints from similar sessions' scores
        hints = []
        weak_dims: dict[str, int] = {}
        for session in similar:
            scores = session.get("final_scores", {})
            if scores:
                weakest = min(scores, key=scores.get)
                weak_dims[weakest] = weak_dims.get(weakest, 0) + 1

        if weak_dims:
            most_weak = max(weak_dims, key=weak_dims.get)
            count = weak_dims[most_weak]
            if count >= 2:
                hints.append(
                    f"Similar past sessions struggled with {most_weak} — "
                    f"pay extra attention to this dimension."
                )

        ctx["prompt_hints"] = hints

    return ctx
