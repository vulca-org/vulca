"""Interactive terminal UI for VULCA Studio."""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from vulca.studio.brief import Brief
from vulca.studio.session import SessionState, StudioSession
from vulca.studio.phases.intent import IntentPhase
from vulca.studio.phases.scout import ScoutPhase
from vulca.studio.phases.concept import ConceptPhase
from vulca.studio.phases.generate import GeneratePhase
from vulca.studio.phases.evaluate import EvaluatePhase
from vulca.studio.nl_update import parse_nl_update, parse_nl_update_llm, apply_update
from vulca.digestion.preloader import preload_intelligence

logger = logging.getLogger("vulca.studio")


def _print(msg: str) -> None:
    """Print with VULCA prefix."""
    print(msg)


def _ask(prompt: str) -> str:
    """Ask user for input."""
    return input(prompt)


def run_studio(
    intent: str,
    *,
    project_dir: str = "",
    provider: str = "mock",
    concept_count: int = 4,
    api_key: str = "",
    data_dir: str = "",
) -> dict:
    """Run interactive studio session. Returns summary dict."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(
            _run_studio_async(
                intent,
                project_dir=project_dir,
                provider=provider,
                concept_count=concept_count,
                api_key=api_key,
                data_dir=data_dir,
            )
        )
    finally:
        loop.close()


async def _run_studio_async(
    intent: str,
    *,
    project_dir: str = "",
    provider: str = "mock",
    concept_count: int = 4,
    api_key: str = "",
    data_dir: str = "",
) -> dict:
    # Create session
    session = StudioSession.new(intent, project_dir=project_dir)
    pdir = str(session.project_dir)

    _print(f"\nVULCA Studio — session {session.session_id}")
    _print(f"Project: {session.project_dir}/\n")

    # ── Layer 0: Pre-session intelligence ──
    preload_ctx = preload_intelligence(intent, data_dir=data_dir)
    if preload_ctx.get("suggested_traditions"):
        _print(f"  Suggested styles: {', '.join(preload_ctx['suggested_traditions'])}")
    if preload_ctx.get("prompt_hints"):
        for hint in preload_ctx["prompt_hints"]:
            _print(f"  Hint: {hint}")

    # ── Sketch prompt ──
    sketch_path = _ask("Reference sketch? (path or Enter to skip): ").strip()
    if sketch_path and Path(sketch_path).exists():
        intent_phase = IntentPhase()
        intent_phase.set_sketch(session.brief, sketch_path)
        _print(f"  Sketch loaded: {sketch_path}")
    else:
        intent_phase = IntentPhase()

    # ── Phase 1: INTENT ──
    _print("[Intent] Analyzing your creative vision...")
    await intent_phase.parse_intent_llm(session.brief)

    if session.brief.style_mix:
        styles = ", ".join(
            f"{s.tradition or s.tag} ({s.weight:.0%})" for s in session.brief.style_mix
        )
        _print(f"  Style detected: {styles}")

        # Style weight adjustment
        if len(session.brief.style_mix) >= 2:
            adj = _ask("  Adjust weights? (e.g. 70/30, or Enter to keep): ").strip()
            if adj and "/" in adj:
                parts = adj.split("/")
                try:
                    raw = [float(p) for p in parts]
                    total = sum(raw)
                    if total > 0:
                        for i, s in enumerate(session.brief.style_mix):
                            if i < len(raw):
                                s.weight = round(raw[i] / total, 2)
                        _print(f"  Weights adjusted: {', '.join(f'{s.tradition or s.tag} ({s.weight:.0%})' for s in session.brief.style_mix)}")
                except ValueError:
                    pass

    # Ask clarifying questions
    questions = intent_phase.generate_questions(session.brief)
    for q in questions:
        labels = q.get("labels", q["options"])
        _print(f"\n  {q['text']}")
        for i, label in enumerate(labels, 1):
            _print(f"    {i}. {label}")

        answer = _ask("> ").strip()
        if answer.lower() == "q":
            session.save()
            return {"status": "quit", "session_id": session.session_id}

        try:
            idx = int(answer) - 1
            if 0 <= idx < len(q["options"]):
                intent_phase.apply_answer(session.brief, q, q["options"][idx])
        except (ValueError, IndexError):
            pass  # Skip invalid input

    # Scout (generate references in background)
    _print("\n  Generating references...")
    scout_phase = ScoutPhase()
    try:
        refs = await scout_phase.generate_references(
            session.brief, provider=provider, project_dir=pdir, api_key=api_key
        )
        for ref in refs:
            _print(f"  → {ref.path}")
    except Exception:
        pass

    session.advance_to(SessionState.CONCEPT)
    session.save()

    # ── Phase 2: CONCEPT ──
    _print(f"\n[Concept] Generating {concept_count} concepts...")
    concept_phase = ConceptPhase()
    paths = await concept_phase.generate_concepts(
        session.brief, count=concept_count, provider=provider,
        project_dir=pdir, api_key=api_key
    )
    for i, p in enumerate(paths, 1):
        ppath = Path(p)
        size = ppath.stat().st_size if ppath.exists() else 0
        size_str = f"{size / 1024:.0f}KB" if size >= 1024 else f"{size}B"
        _print(f"  {i}. {ppath.name} ({size_str})")

    answer = _ask("Select (1-N, or describe changes): ").strip()
    if answer.lower() == "q":
        session.save()
        return {"status": "quit", "session_id": session.session_id}

    # Parse: number = select, text = select 1 + notes
    try:
        parts = answer.split(maxsplit=1)
        idx = int(parts[0]) - 1
        notes = parts[1] if len(parts) > 1 else ""
        concept_phase.select(session.brief, index=idx, notes=notes)
    except (ValueError, IndexError):
        concept_phase.select(session.brief, index=0)

    session.advance_to(SessionState.GENERATE)
    session.save()

    # ── Generate → Evaluate → Decide loop ──
    # Track whether we've entered EVALUATE state already to avoid advance_to errors
    entered_evaluate = False

    while True:
        # Phase 3: GENERATE
        _print(f"\n[Generate] Creating artwork via {provider}...")
        gen_phase = GeneratePhase()
        result_path = await gen_phase.generate(
            session.brief, provider=provider, project_dir=pdir, api_key=api_key
        )
        _print(f"  → {result_path}")

        # Advance to EVALUATE on first entry; use rollback_to on re-entry
        if not entered_evaluate:
            session.advance_to(SessionState.EVALUATE)
            entered_evaluate = True
        else:
            session.rollback_to(SessionState.EVALUATE)

        # Phase 4: EVALUATE
        _print("\n[Evaluate] L1-L5 (based on your Brief):")
        eval_phase = EvaluatePhase()
        scores = await eval_phase.evaluate(
            session.brief, image_path=result_path, mock=(provider == "mock"), api_key=api_key
        )

        for dim in ("L1", "L2", "L3", "L4", "L5"):
            score = scores.get(dim, 0.0)
            bar = "\u2588" * int(score * 20) + "\u2591" * (20 - int(score * 20))
            _print(f"  {dim} {bar} {score:.0%}")

        # Record scores in Brief
        if session.brief.generations:
            session.brief.generations[-1].scores = scores

        session.save()

        # User decision
        _print("\n  Next: (a)ccept  (u)pdate  (r)egenerate  (q)uit")
        decision = _ask("> ").strip().lower()

        if decision in ("a", "accept"):
            _print("\nArtwork accepted!")
            if session.state != SessionState.DONE:
                session.advance_to(SessionState.DONE)
            session.save()
            return {
                "status": "accepted",
                "session_id": session.session_id,
                "image_path": result_path,
                "scores": scores,
            }
        elif decision in ("q", "quit"):
            session.save()
            return {"status": "quit", "session_id": session.session_id}
        elif decision.startswith("u"):
            # NL update
            if len(decision) > 2:
                instruction = decision[2:].strip()
            else:
                instruction = _ask("Update instruction: ").strip()
            if instruction:
                nl_result = await parse_nl_update_llm(instruction, session.brief)
                apply_update(session.brief, nl_result)
                _print(f"  Brief updated → rollback to {nl_result.rollback_to.value}")
                session.rollback_to(SessionState.GENERATE)
                entered_evaluate = False
            # Continue loop → regenerate
        else:
            # Default: regenerate — rollback to GENERATE state
            session.rollback_to(SessionState.GENERATE)
            entered_evaluate = False
