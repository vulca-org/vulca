"""Tests for Layer 3 Evolution — cross-session pattern detection."""
from __future__ import annotations

import pytest


def test_pattern_detection_from_real_data(tmp_path):
    """Detect style patterns from accumulated session data."""
    from vulca.digestion.evolver import detect_patterns
    from vulca.digestion.storage import JsonlStudioStorage
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight, GenerationRound

    store = JsonlStudioStorage(data_dir=str(tmp_path))
    # Seed 5 xieyi sessions with varying L2 weakness
    for i in range(5):
        b = Brief.new(f"水墨 #{i}", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
        b.generations = [GenerationRound(round_num=1, image_path=f"r{i}.png",
                                          scores={"L1": 0.8, "L2": 0.4 + i * 0.02, "L3": 0.7, "L4": 0.6, "L5": 0.85})]
        store.save_session(b, user_feedback="accepted")

    patterns = detect_patterns(store)

    assert isinstance(patterns, list)
    assert len(patterns) >= 1
    # Should detect that L2 is consistently weak for xieyi
    pattern_strs = str(patterns)
    assert "L2" in pattern_strs or "chinese_xieyi" in pattern_strs


def test_weight_evolution_from_accept_reject(tmp_path):
    """Evolve tradition weights based on accept/reject feedback."""
    from vulca.digestion.evolver import evolve_weights
    from vulca.digestion.storage import JsonlStudioStorage
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight, GenerationRound

    store = JsonlStudioStorage(data_dir=str(tmp_path))

    # 3 accepted sessions with high L5, low L2
    for i in range(3):
        b = Brief.new(f"accepted #{i}", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
        b.generations = [GenerationRound(round_num=1, image_path=f"a{i}.png",
                                          scores={"L1": 0.7, "L2": 0.4, "L3": 0.8, "L4": 0.6, "L5": 0.9})]
        store.save_session(b, user_feedback="accepted")

    # 2 rejected sessions
    for i in range(2):
        b = Brief.new(f"rejected #{i}", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
        b.generations = [GenerationRound(round_num=1, image_path=f"r{i}.png",
                                          scores={"L1": 0.3, "L2": 0.3, "L3": 0.4, "L4": 0.3, "L5": 0.3})]
        store.save_session(b, user_feedback="rejected")

    weights = evolve_weights(store, tradition="chinese_xieyi")

    assert isinstance(weights, dict)
    assert "L1" in weights
    assert "L5" in weights
    # Accepted sessions had high L5 → L5 weight should be notable
    assert all(0.0 <= v <= 1.0 for v in weights.values())


def test_no_mock_data_contamination(tmp_path):
    """Evolution should only use sessions with user_feedback, not mock data."""
    from vulca.digestion.evolver import evolve_weights
    from vulca.digestion.storage import JsonlStudioStorage
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight, GenerationRound

    store = JsonlStudioStorage(data_dir=str(tmp_path))

    # Sessions without feedback (mock/incomplete)
    for i in range(5):
        b = Brief.new(f"no feedback #{i}", style_mix=[StyleWeight(tradition="chinese_xieyi", weight=1.0)])
        b.generations = [GenerationRound(round_num=1, image_path=f"m{i}.png",
                                          scores={"L1": 0.99, "L2": 0.99, "L3": 0.99, "L4": 0.99, "L5": 0.99})]
        store.save_session(b)  # No user_feedback

    weights = evolve_weights(store, tradition="chinese_xieyi")

    # Should return default equal weights (no valid feedback data)
    assert weights == {"L1": 0.2, "L2": 0.2, "L3": 0.2, "L4": 0.2, "L5": 0.2}
