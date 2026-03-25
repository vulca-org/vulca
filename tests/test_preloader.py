"""Tests for Layer 0 Preloader — pre-session intelligence."""
from __future__ import annotations

import pytest


def test_preload_cold_start_fallback(tmp_path):
    """With no history, preloader should return tradition YAML defaults."""
    from vulca.digestion.preloader import preload_intelligence

    ctx = preload_intelligence(
        intent="水墨山水",
        data_dir=str(tmp_path),  # empty dir = no history
    )

    assert ctx is not None
    assert "suggested_traditions" in ctx
    # Should still suggest based on intent keywords
    assert len(ctx["suggested_traditions"]) >= 1


def test_preload_with_session_history(tmp_path):
    """With past sessions, preloader should suggest based on similar intents."""
    from vulca.digestion.preloader import preload_intelligence
    from vulca.digestion.storage import JsonlStudioStorage
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight

    # Seed some history
    store = JsonlStudioStorage(data_dir=str(tmp_path))
    for i in range(3):
        b = Brief.new(f"水墨山水画 #{i}", mood="serene",
                      style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
        store.save_session(b, user_feedback="accepted")

    ctx = preload_intelligence(
        intent="新的水墨山水",
        data_dir=str(tmp_path),
    )

    assert ctx is not None
    # Should find similar sessions
    assert ctx.get("similar_session_count", 0) >= 1
    # Should suggest xieyi based on history
    assert "chinese_xieyi" in ctx.get("suggested_traditions", [])


def test_preload_returns_prompt_hints(tmp_path):
    """Preload context should include prompt hints for generation."""
    from vulca.digestion.preloader import preload_intelligence
    from vulca.digestion.storage import JsonlStudioStorage
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight, GenerationRound

    store = JsonlStudioStorage(data_dir=str(tmp_path))
    b = Brief.new("水墨山水", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
    b.generations = [GenerationRound(round_num=1, image_path="r1.png",
                                     scores={"L1": 0.8, "L2": 0.4, "L3": 0.7, "L4": 0.6, "L5": 0.9})]
    store.save_session(b, user_feedback="accepted")

    ctx = preload_intelligence(intent="水墨画", data_dir=str(tmp_path))

    assert "prompt_hints" in ctx
    assert isinstance(ctx["prompt_hints"], list)
