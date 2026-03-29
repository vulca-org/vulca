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


def should_suggest_stop(score_history: list[float], *, target: float = 0.85) -> bool:
    """Suggest stopping when score reaches target OR converges (<3% change for 2 rounds)."""
    if len(score_history) == 0:
        return False
    if score_history[-1] >= target:
        return True
    if len(score_history) >= 2:
        delta = abs(score_history[-1] - score_history[-2])
        if delta < 0.03:
            return True
    return False


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

        # Auto-stop suggestion
        all_scores = []
        for g in session.brief.generations:
            if g.scores:
                vals = [v for v in g.scores.values() if isinstance(v, (int, float))]
                if vals:
                    all_scores.append(sum(vals) / len(vals))
        if should_suggest_stop(all_scores):
            if all_scores and all_scores[-1] >= 0.85:
                _print(f"\n  Score target reached ({all_scores[-1]:.0%}). Consider accepting.")
            elif len(all_scores) >= 2:
                _print(f"\n  Score plateaued ({all_scores[-2]:.0%} -> {all_scores[-1]:.0%}). Consider accepting or trying a different approach.")

        # User decision
        _print("\n  Next: (a)ccept  (u)pdate  (r)egenerate  (i)npaint  (q)uit")
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
                # Regenerate concepts as variations of selected
                if session.brief.selected_concept and Path(session.brief.selected_concept).exists():
                    from vulca.studio.nl_update import infer_variation_strength
                    strength = infer_variation_strength(instruction)
                    _print(f"\n[Concept] Generating {concept_count} variations (strength: {strength:.1f})...")
                    concept_phase_loop = ConceptPhase()
                    loop_paths = await concept_phase_loop.generate_concepts(
                        session.brief, count=concept_count, provider=provider,
                        project_dir=pdir, api_key=api_key,
                        reference_image=session.brief.selected_concept,
                        variation_strength=strength,
                    )
                    for ci, cp in enumerate(loop_paths, 1):
                        cppath = Path(cp)
                        sz = cppath.stat().st_size if cppath.exists() else 0
                        sz_str = f"{sz / 1024:.0f}KB" if sz >= 1024 else f"{sz}B"
                        _print(f"  {ci}. {cppath.name} ({sz_str})")
                    sel_answer = _ask("Select variation (1-N): ").strip()
                    try:
                        sel_idx = int(sel_answer.split()[0]) - 1
                        concept_phase_loop.select(session.brief, index=sel_idx)
                    except (ValueError, IndexError):
                        concept_phase_loop.select(session.brief, index=0)
                    session.save()
            # Continue loop → regenerate
        elif decision.startswith("i"):
            # Inpaint mode
            region_input = _ask("Describe region to repaint (or x,y,w,h %): ").strip()
            inpaint_instruction = _ask("Repaint instruction: ").strip()
            if region_input and inpaint_instruction:
                from vulca.inpaint import ainpaint
                _print("\n[Inpaint] Processing...")
                inpaint_result = await ainpaint(
                    result_path,
                    region=region_input,
                    instruction=inpaint_instruction,
                    tradition=session.brief.style_mix[0].tradition if session.brief.style_mix else "default",
                    count=4,
                    api_key=api_key,
                )
                if inpaint_result.variants:
                    _print(f"  {len(inpaint_result.variants)} variants generated:")
                    for vi, vp in enumerate(inpaint_result.variants, 1):
                        _print(f"    {vi}. {Path(vp).name}")
                    sel = _ask("Select (1-N): ").strip()
                    try:
                        sel_idx = int(sel) - 1
                    except ValueError:
                        sel_idx = 0

                    # Re-blend with selected variant
                    from vulca.studio.phases.inpaint import InpaintPhase
                    phase = InpaintPhase()
                    blended = await phase.blend(
                        result_path, inpaint_result.variants[sel_idx],
                        bbox=inpaint_result.bbox, api_key=api_key,
                    )
                    result_path = blended
                    session.brief.selected_concept = blended
                    _print(f"  Blended: {blended}")
                    session.save()
            # Continue loop
        else:
            # Default: regenerate — rollback to GENERATE state
            session.rollback_to(SessionState.GENERATE)
            entered_evaluate = False
