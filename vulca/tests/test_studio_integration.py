"""Integration tests for Studio pipeline end-to-end."""
from __future__ import annotations

import asyncio
import pytest


def test_full_session_intent_to_concept(tmp_path):
    """End-to-end: create session → intent → concept → select."""
    from vulca.studio.session import StudioSession, SessionState
    from vulca.studio.phases.intent import IntentPhase
    from vulca.studio.phases.concept import ConceptPhase

    # Create session
    session = StudioSession.new("水墨山水", project_dir=str(tmp_path / "proj"))
    assert session.state == SessionState.INTENT

    # Phase 1: Intent
    intent_phase = IntentPhase()
    intent_phase.parse_intent(session.brief)
    assert len(session.brief.style_mix) >= 1  # Should detect chinese_xieyi

    session.advance_to(SessionState.CONCEPT)

    # Phase 2: Concept
    concept_phase = ConceptPhase()
    loop = asyncio.new_event_loop()
    paths = loop.run_until_complete(
        concept_phase.generate_concepts(session.brief, count=2, provider="mock",
                                         project_dir=str(session.project_dir))
    )
    loop.close()

    assert len(paths) == 2
    concept_phase.select(session.brief, index=0, notes="more ink")
    assert session.brief.selected_concept

    session.advance_to(SessionState.GENERATE)
    assert session.state == SessionState.GENERATE


def test_session_save_load_resume(tmp_path):
    """Session can be saved and resumed from disk."""
    from vulca.studio.session import StudioSession, SessionState

    session = StudioSession.new("save-load test", project_dir=str(tmp_path / "proj"))
    session.brief.mood = "serene"
    session.advance_to(SessionState.CONCEPT)
    session.save()

    loaded = StudioSession.load(str(tmp_path / "proj"))
    assert loaded.state == SessionState.CONCEPT
    assert loaded.brief.mood == "serene"
    assert loaded.brief.intent == "save-load test"
    assert loaded.session_id == session.session_id


def test_nl_update_mid_flow(tmp_path):
    """NL update during concept phase should rollback correctly."""
    from vulca.studio.session import StudioSession, SessionState
    from vulca.studio.nl_update import parse_nl_update, apply_update

    session = StudioSession.new("test", project_dir=str(tmp_path / "proj"))
    session.advance_to(SessionState.GENERATE)

    # NL update that affects composition → should rollback to CONCEPT
    result = parse_nl_update("把山改得更高", session.brief)
    apply_update(session.brief, result)
    session.rollback_to(result.rollback_to)

    assert session.state == SessionState.CONCEPT


def test_brief_to_tradition_to_eval_chain():
    """Brief → TraditionConfig → eval criteria → evaluation prompt chain."""
    from vulca.studio.brief import Brief
    from vulca.studio.types import StyleWeight
    from vulca.studio.from_brief import brief_to_tradition
    from vulca.studio.eval_criteria import generate_eval_criteria_sync
    from vulca.studio.phases.evaluate import EvaluatePhase

    b = Brief.new("赛博水墨", style_mix=[
        StyleWeight(tradition="chinese_xieyi", weight=0.6),
        StyleWeight(tag="cyberpunk", weight=0.4),
    ])
    b.must_avoid = ["vector style"]

    # Bridge to tradition
    tc = brief_to_tradition(b)
    assert tc.name == "brief_fusion"
    assert any("vector style" in t.rule for t in tc.taboos)

    # Generate criteria
    criteria = generate_eval_criteria_sync(b, use_llm=False)
    b.eval_criteria = criteria
    assert "L1" in b.eval_criteria

    # Build eval prompt
    phase = EvaluatePhase()
    prompt = phase.build_eval_prompt(b)
    assert "L1" in prompt
    assert len(prompt) > 100
