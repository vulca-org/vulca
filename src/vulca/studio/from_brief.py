"""Convert a Brief to a TraditionConfig for evaluation."""
from __future__ import annotations

from vulca.cultural.types import TabooEntry, TraditionConfig
from vulca.studio.brief import Brief

_DEFAULT_WEIGHTS = {"L1": 0.20, "L2": 0.20, "L3": 0.20, "L4": 0.20, "L5": 0.20}


def brief_to_tradition(brief: Brief) -> TraditionConfig:
    if not brief.style_mix:
        return _load_or_default("default")

    known = [s for s in brief.style_mix if s.tradition]
    free = [s for s in brief.style_mix if s.tag and not s.tradition]

    if len(known) == 1 and not free:
        tc = _load_or_default(known[0].tradition)
        return _add_brief_taboos(tc, brief)

    if known:
        return _merge_traditions(known, free, brief)

    tc = TraditionConfig(name="brief_custom",
                         display_name={"en": brief.intent[:50], "zh": ""},
                         weights_l=dict(_DEFAULT_WEIGHTS))
    return _add_brief_taboos(tc, brief)


def _load_or_default(name: str) -> TraditionConfig:
    try:
        from vulca.cultural.loader import get_tradition
        tc = get_tradition(name)
        if tc is not None:
            return tc
    except Exception:
        pass
    return TraditionConfig(name=name,
                           display_name={"en": name.replace("_", " ").title(), "zh": ""},
                           weights_l=dict(_DEFAULT_WEIGHTS))


def _merge_traditions(known: list, free: list, brief: Brief) -> TraditionConfig:
    merged: dict[str, float] = {f"L{i}": 0.0 for i in range(1, 6)}
    all_terms, all_taboos = [], []
    total = sum(s.weight for s in known) + sum(s.weight for s in free)
    if total == 0:
        total = 1.0

    for sw in known:
        tc = _load_or_default(sw.tradition)
        nw = sw.weight / total
        for dim, val in tc.weights_l.items():
            merged[dim] = merged.get(dim, 0.0) + val * nw
        all_terms.extend(tc.terminology)
        all_taboos.extend(tc.taboos)

    for sw in free:
        nw = sw.weight / total
        for dim in merged:
            merged[dim] += _DEFAULT_WEIGHTS.get(dim, 0.2) * nw

    w_sum = sum(merged.values())
    if w_sum > 0:
        merged = {k: v / w_sum for k, v in merged.items()}

    tc = TraditionConfig(name="brief_fusion",
                         display_name={"en": brief.intent[:50], "zh": ""},
                         weights_l=merged, terminology=all_terms, taboos=all_taboos)
    return _add_brief_taboos(tc, brief)


def _add_brief_taboos(tc: TraditionConfig, brief: Brief) -> TraditionConfig:
    for avoid in brief.must_avoid:
        tc.taboos.append(TabooEntry(
            rule=f"AVOID: {avoid}", severity="high", l_levels=["L3", "L4"],
            explanation=f"User constraint from Brief: must avoid '{avoid}'"))
    return tc
