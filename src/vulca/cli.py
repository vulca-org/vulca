"""VULCA command-line interface.

Usage::

    vulca evaluate painting.jpg
    vulca evaluate painting.jpg --tradition chinese_xieyi --mode reference
    vulca evaluate painting.jpg -t chinese_xieyi,ukiyoe --mode fusion
    vulca create "水墨山水" --hitl --mode reference
    vulca create "水墨山水" --weights "L1=0.3,L2=0.2,L3=0.2,L4=0.15,L5=0.15"
    vulca tradition --init my_style > my_tradition.yaml
"""

from __future__ import annotations

import argparse
import logging
import sys

from vulca._version import __version__

_VALID_MODES = ("strict", "reference", "fusion")

_DIM_NAMES = {
    "L1": "Visual Perception",
    "L2": "Technical Execution",
    "L3": "Cultural Context",
    "L4": "Critical Interpretation",
    "L5": "Philosophical Aesthetics",
}

_DEVIATION_LABELS = {
    "traditional": "traditional",
    "intentional_departure": "intentional departure",
    "experimental": "experimental",
}


def _parse_weights(raw: str) -> dict[str, float]:
    """Parse "L1=0.3,L2=0.2,..." into a weights dict.

    Accepts formats:
        "L1=0.3,L2=0.2,L3=0.2,L4=0.15,L5=0.15"
        "L1=0.3, L2=0.2, L3=0.2, L4=0.15, L5=0.15"
    """
    weights: dict[str, float] = {}
    for pair in raw.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if "=" not in pair:
            raise ValueError(f"Invalid weight format: {pair!r}. Expected 'L1=0.3'.")
        key, val = pair.split("=", 1)
        key = key.strip().upper()
        if key not in ("L1", "L2", "L3", "L4", "L5"):
            raise ValueError(f"Unknown dimension: {key!r}. Expected L1-L5.")
        weights[key] = float(val.strip())
    return weights


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="vulca",
        description="VULCA -- AI-native cultural art advisor",
    )
    parser.add_argument("--version", action="version", version=f"vulca {__version__}")

    sub = parser.add_subparsers(dest="command")

    # evaluate command
    eval_p = sub.add_parser("evaluate", aliases=["eval", "e"], help="Evaluate an artwork")
    eval_p.add_argument("image", help="Image file path or URL")
    eval_p.add_argument("--intent", "-i", default="", help="Natural language evaluation intent")
    eval_p.add_argument("--tradition", "-t", default="", help="Cultural tradition or path to custom YAML")
    eval_p.add_argument("--subject", "-s", default="", help="Artwork subject/title")
    eval_p.add_argument("--mode", "-m", default="strict", choices=_VALID_MODES,
                        help="Evaluation mode: strict (judge), reference (advisor), fusion (multi-tradition)")
    eval_p.add_argument("--skills", default="", help="Comma-separated extra skills: brand,audience,trend")
    eval_p.add_argument("--json", action="store_true", help="Output raw JSON")
    eval_p.add_argument("--api-key", default="", help="Google API key (or set GOOGLE_API_KEY)")
    eval_p.add_argument("--mock", action="store_true", help="Use mock scoring (no API key required)")
    eval_p.add_argument("--vlm-model", default="", help="VLM model (LiteLLM format, e.g. ollama/llava)")
    eval_p.add_argument("--vlm-base-url", default="", help="VLM base URL (for local models)")
    eval_p.add_argument("--sparse-eval", action="store_true", help="Enable sparse evaluation (score only relevant dimensions)")
    eval_p.add_argument("--reference", default="", help="Reference image path or base64 for comparison")

    # create command
    create_p = sub.add_parser("create", aliases=["c"], help="Create artwork via pipeline")
    create_p.add_argument("intent", help="Natural language creation intent")
    create_p.add_argument("--tradition", "-t", default="", help="Cultural tradition or path to custom YAML")
    create_p.add_argument("--subject", "-s", default="", help="Artwork subject/title")
    create_p.add_argument("--provider", default="nb2", help="Image generation provider")
    create_p.add_argument("--mode", "-m", default="strict", choices=_VALID_MODES,
                          help="Evaluation mode: strict (judge), reference (advisor)")
    create_p.add_argument("--json", action="store_true", help="Output raw JSON")
    create_p.add_argument("--api-key", default="", help="VULCA API key (or set VULCA_API_KEY)")
    create_p.add_argument("--base-url", default="", help="VULCA API base URL")
    create_p.add_argument("--hitl", action="store_true", help="Enable human-in-the-loop (pause before decide)")
    create_p.add_argument("--weights", default="", help="Custom L1-L5 weights: 'L1=0.3,L2=0.2,...'")
    create_p.add_argument("--image-provider", default="", help="Image provider: mock|gemini|openai|comfyui")
    create_p.add_argument("--image-base-url", default="", help="Image provider base URL (for comfyui)")
    create_p.add_argument("--residuals", action="store_true", help="Enable Agent Residuals (selective node aggregation)")
    create_p.add_argument("--sparse-eval", action="store_true", help="Enable sparse evaluation (score only relevant dimensions)")
    create_p.add_argument("--sketch", default="", help="Sketch image path or base64")
    create_p.add_argument("--reference", default="", help="Reference image path or base64")
    create_p.add_argument("--ref-type", default="full", choices=["style", "composition", "full"],
                          help="Reference type: style, composition, or full")
    create_p.add_argument("--colors", default="", help="Hex color palette (comma-separated, e.g. '#C87F4A,#5F8A50')")

    # traditions command
    sub.add_parser("traditions", aliases=["t"], help="List available cultural traditions")

    # tradition detail command
    trad_p = sub.add_parser("tradition", aliases=["td"], help="Get cultural tradition guide")
    trad_p.add_argument("name", nargs="?", default="", help="Tradition name (e.g. chinese_xieyi)")
    trad_p.add_argument("--init", default="", metavar="NAME", help="Generate a template YAML for a custom tradition")
    trad_p.add_argument("--json", action="store_true", help="Output raw JSON")

    # evolution status command
    evo_p = sub.add_parser("evolution", aliases=["evo"], help="Get evolution status for a tradition")
    evo_p.add_argument("name", help="Tradition name")
    evo_p.add_argument("--json", action="store_true", help="Output raw JSON")

    # Studio commands
    studio_parser = sub.add_parser("studio", help="Run interactive Studio session")
    studio_parser.add_argument("intent_or_dir", help="Creative intent or project dir (with --resume)")
    studio_parser.add_argument("--provider", "-p", default="mock", help="Image provider")
    studio_parser.add_argument("--count", "-n", type=int, default=4, help="Number of concepts")
    studio_parser.add_argument("--resume", action="store_true", help="Resume from saved session")
    studio_parser.add_argument("--api-key", default="", help="API key")

    brief_parser = sub.add_parser("brief", help="Create or show a Studio Brief")
    brief_parser.add_argument("project_dir", help="Project directory")
    brief_parser.add_argument("--intent", "-i", default="", help="Creative intent")
    brief_parser.add_argument("--mood", "-m", default="", help="Mood/atmosphere")

    brief_update_parser = sub.add_parser("brief-update", help="Update Brief with NL instruction")
    brief_update_parser.add_argument("project_dir", help="Project directory")
    brief_update_parser.add_argument("instruction", help="Natural language update")

    concept_parser = sub.add_parser("concept", help="Generate or select concepts")
    concept_parser.add_argument("project_dir", help="Project directory")
    concept_parser.add_argument("--count", "-n", type=int, default=4, help="Number of concepts")
    concept_parser.add_argument("--provider", "-p", default="mock", help="Image provider")
    concept_parser.add_argument("--select", "-s", type=int, default=None, help="Select concept (1-based)")
    concept_parser.add_argument("--notes", default="", help="Notes for selection")

    # sync command
    sync_parser = sub.add_parser("sync", help="Sync local session data with cloud")
    sync_parser.add_argument("--push-only", action="store_true", help="Only push local data")
    sync_parser.add_argument("--pull-only", action="store_true", help="Only pull evolved weights")

    # inpaint command
    inpaint_p = sub.add_parser("inpaint", help="Repaint a region of an artwork")
    inpaint_p.add_argument("image", help="Path to image")
    inpaint_p.add_argument("--region", required=True, help="Region: NL description or 'x,y,w,h' coordinates (%%)")
    inpaint_p.add_argument("--instruction", required=True, help="What to change in the region")
    inpaint_p.add_argument("--tradition", "-t", default="default", help="Cultural tradition")
    inpaint_p.add_argument("--count", "-n", type=int, default=4, help="Number of variants")
    inpaint_p.add_argument("--select", "-s", type=int, default=None, help="Auto-select variant (1-based)")
    inpaint_p.add_argument("--output", "-o", default="", help="Output path")
    inpaint_p.add_argument("--mock", action="store_true", help="Use mock mode")

    args = parser.parse_args(argv)

    if args.command in ("evaluate", "eval", "e"):
        _cmd_evaluate(args)
    elif args.command in ("create", "c"):
        if not args.intent.strip():
            print("Error: intent cannot be empty.", file=sys.stderr)
            sys.exit(1)
        if args.hitl:
            _cmd_create_hitl(args)
        else:
            _cmd_create(args)
    elif args.command in ("traditions", "t"):
        _cmd_traditions()
    elif args.command in ("tradition", "td"):
        if args.init:
            _cmd_tradition_init(args)
        elif args.name:
            _cmd_tradition(args)
        else:
            print("Error: provide a tradition name or use --init NAME", file=sys.stderr)
            sys.exit(1)
    elif args.command in ("evolution", "evo"):
        _cmd_evolution(args)
    elif args.command == "studio":
        _cmd_studio(args)
    elif args.command == "brief":
        _cmd_brief(args)
    elif args.command == "brief-update":
        _cmd_brief_update(args)
    elif args.command == "concept":
        _cmd_concept(args)
    elif args.command == "sync":
        _cmd_sync(args)
    elif args.command == "inpaint":
        _cmd_inpaint(args)
    else:
        parser.print_help()
        sys.exit(1)


# ---------------------------------------------------------------------------
# Evaluate command
# ---------------------------------------------------------------------------

def _cmd_evaluate(args: argparse.Namespace) -> None:
    import json as json_mod
    import os
    from vulca import evaluate

    if hasattr(args, 'vlm_model') and args.vlm_model:
        os.environ["VULCA_VLM_MODEL"] = args.vlm_model
    if hasattr(args, 'vlm_base_url') and args.vlm_base_url:
        os.environ["VULCA_VLM_BASE_URL"] = args.vlm_base_url

    skills = [s.strip() for s in args.skills.split(",") if s.strip()] if args.skills else None
    mode = args.mode

    # Fusion mode: evaluate against multiple traditions
    if mode == "fusion" and "," in args.tradition:
        _cmd_evaluate_fusion(args, skills)
        return

    try:
        result = evaluate(
            args.image,
            intent=args.intent,
            tradition=args.tradition,
            subject=args.subject,
            skills=skills,
            api_key=args.api_key,
            mock=args.mock,
            mode=mode,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        import dataclasses
        print(json_mod.dumps(dataclasses.asdict(result), indent=2, ensure_ascii=False))
        return

    if mode == "reference":
        _print_reference_result(result)
    else:
        _print_strict_result(result)


def _print_strict_result(result) -> None:
    """Strict mode output: judge style with pass/fail indicators."""
    print(f"\n  VULCA Evaluation Result")
    print(f"  {'=' * 50}")
    print(f"  Score:     {result.score:.0%}")
    print(f"  Tradition: {result.tradition}")
    print(f"  Risk:      {result.risk_level}")
    print()
    print(f"  Dimensions:")
    for level in ("L1", "L2", "L3", "L4", "L5"):
        score = result.dimensions.get(level, 0)
        bar = "\u2588" * int(score * 20) + "\u2591" * (20 - int(score * 20))
        indicator = "\u2713" if score >= 0.7 else "\u2717"
        print(f"    {level} {_DIM_NAMES[level]:<25s} {bar} {score:.0%}  {indicator}")

    # Extra dimensions (tradition-specific)
    if result.extra_scores:
        print(f"\n  Tradition-Specific:")
        for ekey, escore in result.extra_scores.items():
            extra_names = result.raw.get("_extra_names", {})
            ename = extra_names.get(ekey, ekey)
            bar = "\u2588" * int(escore * 20) + "\u2591" * (20 - int(escore * 20))
            mark = "\u2713" if escore >= 0.6 else "\u2717"
            print(f"    {ename:<32s} {bar} {escore:.0%}  {mark}")

    print()
    print(f"  Summary: {result.summary}")

    if result.suggestions:
        print(f"\n  Suggestions:")
        for level in ("L1", "L2", "L3", "L4", "L5"):
            s = result.suggestions.get(level, "")
            if s and result.dimensions.get(level, 0) < 0.7:
                print(f"    {level}: {s}")

    if result.recommendations:
        print(f"\n  Recommendations:")
        for r in result.recommendations:
            print(f"    - {r}")

    if result.skills:
        print(f"\n  Skills:")
        for name, sr in result.skills.items():
            print(f"    {name}: {sr.score:.0%} -- {sr.summary}")

    print(f"\n  Latency: {result.latency_ms}ms | Cost: ${result.cost_usd:.4f}")
    print()


def _print_reference_result(result) -> None:
    """Reference mode output: advisor style with deviation analysis."""
    print(f"\n  VULCA Cultural Analysis (reference mode)")
    print(f"  {'=' * 50}")
    print(f"  Alignment: {result.score:.0%}")
    print(f"  Tradition: {result.tradition}")
    print()
    print(f"  Dimension Analysis:")
    for level in ("L1", "L2", "L3", "L4", "L5"):
        score = result.dimensions.get(level, 0)
        bar = "\u2588" * int(score * 20) + "\u2591" * (20 - int(score * 20))
        deviation = result.deviation_types.get(level, "traditional")
        dev_label = _DEVIATION_LABELS.get(deviation, deviation)
        print(f"    {level} {_DIM_NAMES[level]:<25s} {bar} {score:.0%}  ({dev_label})")

        # Show rationale for divergent dimensions
        if deviation != "traditional":
            rationale = result.rationales.get(level, "")
            if rationale:
                print(f"       Divergence: {rationale}")

        # Show suggestion
        suggestion = result.suggestions.get(level, "")
        if suggestion:
            if deviation == "traditional":
                print(f"       To push further: {suggestion}")
            else:
                print(f"       To align with tradition: {suggestion}")
                print(f"       To lean into departure: consider amplifying the experimental elements")

    # Extra dimensions (tradition-specific)
    if result.extra_scores:
        print(f"\n  Tradition-Specific:")
        for ekey, escore in result.extra_scores.items():
            extra_names = result.raw.get("_extra_names", {})
            ename = extra_names.get(ekey, ekey)
            bar = "\u2588" * int(escore * 20) + "\u2591" * (20 - int(escore * 20))
            mark = "\u2713" if escore >= 0.6 else "\u2717"
            print(f"    {ename:<32s} {bar} {escore:.0%}  {mark}")

    print()
    print(f"  Summary: {result.summary}")
    print(f"\n  Latency: {result.latency_ms}ms | Cost: ${result.cost_usd:.4f}")
    print()


def _cmd_evaluate_fusion(args: argparse.Namespace, skills: list[str] | None) -> None:
    """Fusion mode: evaluate against multiple traditions and compare."""
    import json as json_mod
    from vulca import evaluate

    traditions = [t.strip() for t in args.tradition.split(",") if t.strip()]
    results = []

    for tradition in traditions:
        try:
            result = evaluate(
                args.image,
                intent=args.intent,
                tradition=tradition,
                subject=args.subject,
                skills=skills,
                api_key=args.api_key,
                mock=args.mock,
                mode="reference",
            )
            results.append((tradition, result))
        except ValueError as e:
            print(f"  Warning: {tradition} failed: {e}", file=sys.stderr)

    if not results:
        print("Error: no traditions evaluated successfully", file=sys.stderr)
        sys.exit(1)

    if args.json:
        import dataclasses
        all_data = {t: dataclasses.asdict(r) for t, r in results}
        print(json_mod.dumps(all_data, indent=2, ensure_ascii=False))
        return

    print(f"\n  VULCA Fusion Analysis ({len(results)} traditions)")
    print(f"  {'=' * 60}")
    print()

    # Comparison table header
    trad_labels = [t.replace("_", " ").title()[:15] for t, _ in results]
    header = f"    {'Dimension':<25s}" + "".join(f" {tl:>15s}" for tl in trad_labels)
    print(header)
    print(f"    {'-' * 25}" + "".join(f" {'-' * 15}" for _ in results))

    for level in ("L1", "L2", "L3", "L4", "L5"):
        row = f"    {_DIM_NAMES[level]:<25s}"
        for _, result in results:
            score = result.dimensions.get(level, 0)
            deviation = result.deviation_types.get(level, "traditional")
            marker = "*" if deviation != "traditional" else " "
            row += f" {score:>13.0%}{marker} "
        print(row)

    print()
    print(f"    {'Overall Alignment':<25s}", end="")
    for _, result in results:
        print(f" {result.score:>14.0%} ", end="")
    print()

    # Best tradition analysis
    best_trad, best_result = max(results, key=lambda x: x[1].score)
    print(f"\n  Closest tradition: {best_trad} ({best_result.score:.0%})")

    # Divergence highlights
    print(f"\n  Divergence highlights:")
    for tradition, result in results:
        departures = [
            level for level in ("L1", "L2", "L3", "L4", "L5")
            if result.deviation_types.get(level) != "traditional"
        ]
        if departures:
            dims = ", ".join(f"{d} ({_DIM_NAMES[d]})" for d in departures)
            print(f"    vs {tradition}: departures in {dims}")

    total_cost = sum(r.cost_usd for _, r in results)
    total_latency = sum(r.latency_ms for _, r in results)
    print(f"\n  Latency: {total_latency}ms | Cost: ${total_cost:.4f}")
    print()


# ---------------------------------------------------------------------------
# Create command
# ---------------------------------------------------------------------------

def _cmd_create(args: argparse.Namespace) -> None:
    import json as json_mod
    import os
    from vulca import create

    if args.image_provider:
        os.environ["VULCA_IMAGE_PROVIDER"] = args.image_provider
    if hasattr(args, 'image_base_url') and args.image_base_url:
        os.environ["VULCA_IMAGE_BASE_URL"] = args.image_base_url

    weights = _parse_weights(args.weights) if args.weights else None

    try:
        result = create(
            args.intent,
            tradition=args.tradition,
            subject=args.subject,
            provider=args.provider,
            api_key=args.api_key,
            base_url=args.base_url,
            weights=weights,
            eval_mode=args.mode,
            residuals=getattr(args, "residuals", False),
            sparse_eval=getattr(args, "sparse_eval", False),
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        import dataclasses
        print(json_mod.dumps(dataclasses.asdict(result), indent=2, ensure_ascii=False))
        return

    print(f"\n  VULCA Creation Result")
    print(f"  {'=' * 40}")
    print(f"  Session:   {result.session_id}")
    print(f"  Mode:      {result.mode} (eval: {result.eval_mode})")
    print(f"  Tradition: {result.tradition}")
    print(f"  Rounds:    {result.total_rounds}")
    if result.best_candidate_id:
        print(f"  Best:      {result.best_candidate_id}")
    if result.summary:
        print(f"  Summary:   {result.summary}")

    if result.suggestions:
        print(f"\n  Suggestions:")
        for level in ("L1", "L2", "L3", "L4", "L5"):
            s = result.suggestions.get(level, "")
            if s:
                print(f"    {level}: {s}")

    if result.recommendations:
        print(f"\n  Recommendations:")
        for r in result.recommendations:
            print(f"    - {r}")
    print(f"\n  Latency: {result.latency_ms}ms | Cost: ${result.cost_usd:.4f}")
    print()


def _cmd_create_hitl(args: argparse.Namespace) -> None:
    """Interactive HITL create: run pipeline, pause, show scores, prompt user."""
    import asyncio
    import json as json_mod
    from vulca.pipeline.engine import execute
    from vulca.pipeline.templates import DEFAULT
    from vulca.pipeline.types import PipelineInput

    weights = _parse_weights(args.weights) if args.weights else None

    node_params: dict[str, dict] = {}
    if weights:
        node_params["evaluate"] = {"custom_weights": weights}

    pipeline_input = PipelineInput(
        subject=args.subject or args.intent,
        intent=args.intent,
        tradition=args.tradition or "default",
        provider=args.provider,
        node_params=node_params,
        eval_mode=args.mode,
    )

    try:
        loop = asyncio.new_event_loop()
        output = loop.run_until_complete(
            execute(DEFAULT, pipeline_input, interrupt_before={"decide"})
        )
        loop.close()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json_mod.dumps(output.to_dict(), indent=2, ensure_ascii=False))
        return

    # Display L1-L5 scores as bar chart
    print(f"\n  VULCA HITL Review (mode: {args.mode})")
    print(f"  {'=' * 40}")
    print(f"  Session:   {output.session_id}")
    print(f"  Tradition: {output.tradition}")
    print(f"  Status:    {output.status}")
    print()
    print(f"  L1-L5 Scores:")
    scores = output.final_scores
    for level in ("L1", "L2", "L3", "L4", "L5"):
        score = scores.get(level, 0.0)
        bar = "\u2588" * int(score * 20) + "\u2591" * (20 - int(score * 20))
        print(f"    {level} {_DIM_NAMES[level]:<25s} {bar} {score:.0%}")
    print(f"\n  Weighted Total: {output.weighted_total:.0%}")
    print()

    # Interactive prompt
    try:
        choice = input("  [A]ccept / [Q]uit? ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        choice = "q"

    if choice in ("a", "accept"):
        print("  -> Accepted. Session stored.")
        # Fire on_complete to persist
        try:
            from vulca.pipeline.hooks import default_on_complete
            oc_loop = asyncio.new_event_loop()
            oc_loop.run_until_complete(default_on_complete(output))
            oc_loop.close()
        except Exception:
            logging.getLogger("vulca").debug("on_complete hook failed in HITL accept")
    else:
        print("  -> Quit. Session discarded.")
    print()


# ---------------------------------------------------------------------------
# Tradition commands
# ---------------------------------------------------------------------------

def _cmd_traditions() -> None:
    from vulca.cultural.loader import get_all_weight_tables

    weights_all = get_all_weight_tables()
    print(f"\n  Available Traditions ({len(weights_all)}):")
    print(f"  {'=' * 50}")
    dim_names = {"L1": "Visual", "L2": "Technical", "L3": "Cultural", "L4": "Critical", "L5": "Philosophical"}
    for name, weights in sorted(weights_all.items()):
        emphasis = max(weights, key=weights.get)
        print(f"    {name:<25s} emphasis: {dim_names.get(emphasis, emphasis)} ({weights[emphasis]:.0%})")
    print(f"\n  Use a custom tradition: vulca evaluate img.jpg -t ./my_tradition.yaml")
    print(f"  Create a template:      vulca tradition --init my_style > my_tradition.yaml")
    print()


def _cmd_tradition(args: argparse.Namespace) -> None:
    import json as json_mod
    from vulca.cultural.loader import get_tradition_guide

    guide = get_tradition_guide(args.name)
    if guide is None:
        print(f"Error: Unknown tradition '{args.name}'", file=sys.stderr)
        print("Run 'vulca traditions' to see available traditions.")
        sys.exit(1)

    if args.json:
        print(json_mod.dumps(guide, indent=2, ensure_ascii=False))
        return

    print(f"\n  Cultural Guide: {guide['tradition']}")
    print(f"  {'=' * 50}")
    print(f"  Description: {guide['description']}")
    print(f"  Emphasis:    {guide['emphasis']}")
    print()
    print(f"  L1-L5 Weights:")
    for level in ("L1", "L2", "L3", "L4", "L5"):
        w = guide["weights"].get(level, 0)
        bar = "\u2588" * int(w * 20) + "\u2591" * (20 - int(w * 20))
        print(f"    {level} {bar} {w:.0%}")

    if guide.get("evolved_weights"):
        print(f"\n  Evolved Weights (from {guide.get('sessions_count', 0)} sessions):")
        for level in ("L1", "L2", "L3", "L4", "L5"):
            ew = guide["evolved_weights"].get(level, 0)
            bar = "\u2588" * int(ew * 20) + "\u2591" * (20 - int(ew * 20))
            print(f"    {level} {bar} {ew:.0%}")

    if guide.get("terminology"):
        print(f"\n  Terminology ({len(guide['terminology'])} terms):")
        for t in guide["terminology"][:10]:
            term = t.get("term", "")
            trans = t.get("translation", "")
            raw_defn = t.get("definition", "")
            if isinstance(raw_defn, dict):
                defn = raw_defn.get("en", "")[:60]
            else:
                defn = str(raw_defn)[:60]
            if trans:
                print(f"    {term} ({trans}): {defn}")
            else:
                print(f"    {term}: {defn}")

    if guide.get("taboos"):
        print(f"\n  Taboos ({len(guide['taboos'])}):")
        for tb in guide["taboos"][:5]:
            print(f"    - {tb}")

    print()


def _cmd_tradition_init(args: argparse.Namespace) -> None:
    """Generate a custom tradition YAML template."""
    name = args.init
    template = f"""# VULCA Custom Tradition: {name}
# Usage: vulca evaluate painting.jpg -t ./{name}.yaml

name: {name}

display_name:
  en: "{name.replace('_', ' ').title()}"
  zh: ""

# Optional: inherit from a built-in tradition (weights, terminology, taboos)
# parent: chinese_xieyi

# L1-L5 evaluation weights (MUST sum to 1.0)
# L1: Visual Perception | L2: Technical Execution | L3: Cultural Context
# L4: Critical Interpretation | L5: Philosophical Aesthetics
weights:
  L1: 0.20
  L2: 0.20
  L3: 0.20
  L4: 0.20
  L5: 0.20

# Override parent weights (only if 'parent' is set):
# override_weights:
#   L1: 0.30
#   L3: 0.10

# Cultural terminology specific to this tradition
terminology:
  - term: "example_technique"
    term_zh: ""
    definition:
      en: "Description of this technique and its significance."
    category: technique
    l_levels: [L2]

# Cultural taboos to watch for
taboos:
  - rule: "Avoid this specific mistake"
    severity: medium
    l_levels: [L3]
    explanation: "Why this is problematic in this context."

# Remove inherited taboos (only if 'parent' is set):
# taboos_remove:
#   - "Inherited taboo rule text to remove"

pipeline:
  variant: default
"""
    print(template)


# ---------------------------------------------------------------------------
# Evolution command
# ---------------------------------------------------------------------------

def _cmd_evolution(args: argparse.Namespace) -> None:
    import json as json_mod
    from vulca.cultural.loader import get_weights
    from vulca.cultural import TRADITION_WEIGHTS

    original = TRADITION_WEIGHTS.get(args.name)
    if original is None:
        print(f"Error: Unknown tradition '{args.name}'", file=sys.stderr)
        sys.exit(1)

    evolved = get_weights(args.name)

    result = {
        "tradition": args.name,
        "original_weights": original,
        "evolved_weights": evolved,
        "weight_changes": {k: f"{evolved.get(k, 0) - original.get(k, 0):+.3f}" for k in original},
    }

    if args.json:
        print(json_mod.dumps(result, indent=2, ensure_ascii=False))
        return

    print(f"\n  Evolution Status: {args.name}")
    print(f"  {'=' * 50}")
    names = {"L1": "Visual", "L2": "Technical", "L3": "Cultural", "L4": "Critical", "L5": "Philosophical"}
    print(f"  {'Dim':<5} {'Original':>10} {'Evolved':>10} {'Change':>10}")
    print(f"  {'-'*5} {'-'*10} {'-'*10} {'-'*10}")
    for level in ("L1", "L2", "L3", "L4", "L5"):
        o = original.get(level, 0)
        e = evolved.get(level, 0)
        delta = e - o
        sign = "+" if delta >= 0 else ""
        print(f"  {level:<5} {o:>9.1%} {e:>9.1%} {sign}{delta:>8.1%}")
    print()


# ---------------------------------------------------------------------------
# Studio commands
# ---------------------------------------------------------------------------

def _cmd_studio(args: argparse.Namespace) -> None:
    from vulca.studio.interactive import run_studio

    if args.resume:
        from vulca.studio.session import StudioSession
        session = StudioSession.load(args.intent_or_dir)
        print(f"Resuming session {session.session_id}...")
        result = run_studio(
            session.brief.intent,
            project_dir=args.intent_or_dir,
            provider=args.provider,
            concept_count=args.count,
            api_key=args.api_key,
        )
    else:
        result = run_studio(
            args.intent_or_dir,
            provider=args.provider,
            concept_count=args.count,
            api_key=args.api_key,
        )
    if result:
        print(f"\nSession {result.get('session_id', '?')}: {result.get('status', 'unknown')}")


def _cmd_brief(args: argparse.Namespace) -> None:
    from pathlib import Path
    from vulca.studio.brief import Brief

    project = Path(args.project_dir)
    brief_file = project / "brief.yaml"

    if args.intent:
        b = Brief.new(args.intent, mood=args.mood)
        filepath = b.save(project)
        print(f"Brief created: {filepath}")
        print(f"  Intent: {b.intent}")
        print(f"  Session: {b.session_id}")
        if b.mood:
            print(f"  Mood: {b.mood}")
    elif brief_file.exists():
        b = Brief.load(project)
        print(f"VULCA Brief -- {b.session_id}")
        print(f"  Intent: {b.intent}")
        if b.mood:
            print(f"  Mood: {b.mood}")
        if b.style_mix:
            styles = ", ".join(s.tradition or s.tag for s in b.style_mix)
            print(f"  Style: {styles}")
        if b.selected_concept:
            print(f"  Concept: {b.selected_concept}")
        if b.generations:
            print(f"  Generations: {len(b.generations)}")
    else:
        print(f"No brief found at {project}. Use --intent to create one.", file=sys.stderr)
        sys.exit(1)


def _cmd_brief_update(args: argparse.Namespace) -> None:
    from pathlib import Path
    from vulca.studio.brief import Brief
    from vulca.studio.nl_update import apply_update, parse_nl_update

    b = Brief.load(Path(args.project_dir))
    result = parse_nl_update(args.instruction, b)
    apply_update(b, result)
    b.save(Path(args.project_dir))
    print(f"Brief updated (rollback to: {result.rollback_to.value})")
    print(f"  Changes: {', '.join(result.field_updates.keys())}")
    print(f"  {result.explanation}")


def _cmd_concept(args: argparse.Namespace) -> None:
    import asyncio
    from pathlib import Path
    from vulca.studio.brief import Brief
    from vulca.studio.phases.concept import ConceptPhase

    b = Brief.load(Path(args.project_dir))
    phase = ConceptPhase()

    if args.select is not None:
        phase.select(b, index=args.select - 1, notes=args.notes)
        b.save(Path(args.project_dir))
        print(f"Selected concept {args.select}: {b.selected_concept}")
    else:
        loop = asyncio.new_event_loop()
        paths = loop.run_until_complete(
            phase.generate_concepts(b, count=args.count, provider=args.provider, project_dir=args.project_dir)
        )
        loop.close()
        b.save(Path(args.project_dir))
        print(f"Generated {len(paths)} concepts:")
        for i, p in enumerate(paths, 1):
            print(f"  {i}. {p}")
        print(f"\nSelect with: vulca concept {args.project_dir} --select N")


# ---------------------------------------------------------------------------
# Sync command
# ---------------------------------------------------------------------------

def _cmd_sync(args: argparse.Namespace) -> None:
    import json as json_mod
    import os
    from pathlib import Path

    api_url = os.environ.get("VULCA_API_URL", "")
    api_key = os.environ.get("VULCA_API_KEY", "")
    if not api_url:
        print("Error: Set VULCA_API_URL environment variable.", file=sys.stderr)
        print("  export VULCA_API_URL='https://your-backend.com'", file=sys.stderr)
        print("  export VULCA_API_KEY='your-key'", file=sys.stderr)
        sys.exit(1)

    data_dir = Path.home() / ".vulca" / "data"

    if not args.pull_only:
        # Push local sessions
        sessions_file = data_dir / "sessions.jsonl"
        synced_file = data_dir / "synced.json"

        synced_ids: set[str] = set()
        if synced_file.exists():
            synced_ids = set(json_mod.loads(synced_file.read_text()))

        to_push = []
        if sessions_file.exists():
            for line in sessions_file.read_text().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json_mod.loads(line)
                    sid = entry.get("session_id", "")
                    if sid and sid not in synced_ids:
                        to_push.append(entry)
                        synced_ids.add(sid)
                except json_mod.JSONDecodeError:
                    continue

        if to_push:
            import httpx
            try:
                resp = httpx.post(
                    f"{api_url.rstrip('/')}/api/v1/sync",
                    json={"sessions": to_push},
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=30,
                )
                resp.raise_for_status()
                synced_file.parent.mkdir(parents=True, exist_ok=True)
                synced_file.write_text(json_mod.dumps(sorted(synced_ids)))
                print(f"Pushed {len(to_push)} sessions to {api_url}")
            except Exception as exc:
                print(f"Push failed: {exc}", file=sys.stderr)
                sys.exit(1)
        else:
            print("No new sessions to push.")

    if not args.push_only:
        # Pull evolved context
        import httpx
        try:
            resp = httpx.get(
                f"{api_url.rstrip('/')}/api/v1/evolved-context",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30,
            )
            resp.raise_for_status()
            evolved_path = data_dir / "evolved_context.json"
            evolved_path.parent.mkdir(parents=True, exist_ok=True)
            evolved_path.write_text(resp.text)
            print(f"Pulled evolved context -> {evolved_path}")
        except Exception as exc:
            print(f"Pull failed: {exc}", file=sys.stderr)
            sys.exit(1)


# ---------------------------------------------------------------------------
# Inpaint command
# ---------------------------------------------------------------------------

def _cmd_inpaint(args: argparse.Namespace) -> None:
    from vulca.inpaint import inpaint as do_inpaint

    select_idx = (args.select - 1) if args.select else 0
    result = do_inpaint(
        args.image,
        region=args.region,
        instruction=args.instruction,
        tradition=args.tradition,
        count=args.count,
        select=select_idx,
        output=args.output,
        mock=args.mock,
    )
    print(f"\n  VULCA Inpaint Result")
    print(f"  {'='*40}")
    print(f"  Region: {result.bbox}")
    print(f"  Variants: {len(result.variants)}")
    print(f"  Selected: v{result.selected + 1}")
    print(f"  Blended: {result.blended}")
    print(f"  Latency: {result.latency_ms}ms | Cost: ${result.cost_usd:.4f}")


if __name__ == "__main__":
    main()
