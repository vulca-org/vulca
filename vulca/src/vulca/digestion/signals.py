"""Extract learning signals from completed Studio sessions."""
from __future__ import annotations

from vulca.studio.brief import Brief


def extract_signals(brief: Brief, *, user_feedback: str = "") -> dict:
    """Extract structured learning signals from a completed session.

    Signals are used for future session improvement:
    - concept_preference: which concept was chosen (index + total)
    - dimension_difficulty: which L dimension was weakest
    - style_mix: what style combination was used
    - user_feedback: accept/reject/quit
    """
    signals: dict = {
        "session_id": brief.session_id,
        "intent": brief.intent,
        "user_feedback": user_feedback,
    }

    # Concept preference
    if brief.concept_candidates and brief.selected_concept:
        try:
            idx = brief.concept_candidates.index(brief.selected_concept)
        except ValueError:
            idx = -1
        signals["concept_preference"] = {
            "selected_index": idx,
            "total_candidates": len(brief.concept_candidates),
            "had_notes": bool(brief.concept_notes),
        }
    else:
        signals["concept_preference"] = {
            "selected_index": -1,
            "total_candidates": 0,
            "had_notes": False,
        }

    # Dimension difficulty (weakest dimension across generations)
    if brief.generations:
        last_scores = brief.generations[-1].scores
        if last_scores:
            weakest = min(last_scores, key=last_scores.get)
            signals["dimension_difficulty"] = {
                "weakest": weakest,
                "weakest_score": last_scores[weakest],
                "strongest": max(last_scores, key=last_scores.get),
                "strongest_score": last_scores[max(last_scores, key=last_scores.get)],
            }
        else:
            signals["dimension_difficulty"] = {"weakest": None}
    else:
        signals["dimension_difficulty"] = {"weakest": None}

    # Style mix
    if brief.style_mix:
        signals["style_mix"] = [
            {"tradition": s.tradition, "tag": s.tag, "weight": s.weight}
            for s in brief.style_mix
        ]
    else:
        signals["style_mix"] = []

    # Update frequency
    signals["update_count"] = len(brief.updates)
    signals["generation_count"] = len(brief.generations)

    return signals


def extract_action_signal(brief: Brief, *, action: str, instruction: str = "") -> dict:
    """Extract a signal from a specific user action (deterministic, no LLM).

    Actions: concept_select, nl_update, evaluate, accept, reject, quit.
    """
    signal: dict = {
        "action": action,
        "session_id": brief.session_id,
    }

    if action == "concept_select":
        idx = -1
        if brief.selected_concept and brief.concept_candidates:
            try:
                idx = brief.concept_candidates.index(brief.selected_concept)
            except ValueError:
                idx = -1
        signal["concept_index"] = idx
        signal["total_candidates"] = len(brief.concept_candidates)
        signal["had_notes"] = bool(brief.concept_notes)
        signal["concept_notes"] = brief.concept_notes

    elif action == "nl_update":
        signal["instruction"] = instruction
        # Extract fields changed from latest update
        if brief.updates:
            latest = brief.updates[-1]
            signal["fields_changed"] = latest.fields_changed
            signal["rollback_to"] = getattr(latest, "rollback_to", "")
        else:
            signal["fields_changed"] = []
            signal["rollback_to"] = ""

    elif action == "evaluate":
        if brief.generations:
            last = brief.generations[-1]
            signal["round_num"] = last.round_num
            signal["scores"] = dict(last.scores) if last.scores else {}
            if last.scores:
                signal["weakest"] = min(last.scores, key=last.scores.get)
                signal["strongest"] = max(last.scores, key=last.scores.get)
        else:
            signal["round_num"] = 0
            signal["scores"] = {}

    elif action in ("accept", "reject", "quit"):
        signal["total_rounds"] = len(brief.generations)
        signal["total_updates"] = len(brief.updates)

    return signal


def accumulate_preferences(signals: list[dict]) -> dict:
    """Accumulate multiple action signals into a preference profile (deterministic)."""
    prefs: dict = {}

    for sig in signals:
        action = sig.get("action", "")

        if action == "concept_select":
            idx = sig.get("concept_index", -1)
            total = sig.get("total_candidates", 0)
            if total > 0 and idx >= 0:
                # Normalize position: 0.0 (first) to 1.0 (last)
                prefs["concept_position_preference"] = round(idx / max(total - 1, 1), 2)
            prefs["prefers_notes"] = sig.get("had_notes", False)

        elif action == "evaluate":
            if sig.get("weakest"):
                prefs["weak_dimension"] = sig["weakest"]
            if sig.get("strongest"):
                prefs["strong_dimension"] = sig["strongest"]

        elif action == "nl_update":
            fields = sig.get("fields_changed", [])
            if "frequently_changed" not in prefs:
                prefs["frequently_changed"] = {}
            for f in fields:
                prefs["frequently_changed"][f] = prefs["frequently_changed"].get(f, 0) + 1

    return prefs
