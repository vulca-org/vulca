"""VULCA command-line interface.

Usage::

    vulca evaluate painting.jpg
    vulca evaluate painting.jpg --intent "check ink wash style"
    vulca evaluate painting.jpg --tradition chinese_xieyi
    vulca evaluate painting.jpg --skills brand,audience,trend
    vulca create "水墨山水" --hitl
    vulca create "水墨山水" --weights "L1=0.3,L2=0.2,L3=0.2,L4=0.15,L5=0.15"
"""

from __future__ import annotations

import argparse
import sys

from vulca._version import __version__


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
        description="VULCA -- AI-native creation organism",
    )
    parser.add_argument("--version", action="version", version=f"vulca {__version__}")

    sub = parser.add_subparsers(dest="command")

    # evaluate command
    eval_p = sub.add_parser("evaluate", aliases=["eval", "e"], help="Evaluate an artwork")
    eval_p.add_argument("image", help="Image file path or URL")
    eval_p.add_argument("--intent", "-i", default="", help="Natural language evaluation intent")
    eval_p.add_argument("--tradition", "-t", default="", help="Cultural tradition (auto-detected if empty)")
    eval_p.add_argument("--subject", "-s", default="", help="Artwork subject/title")
    eval_p.add_argument("--skills", default="", help="Comma-separated extra skills: brand,audience,trend")
    eval_p.add_argument("--json", action="store_true", help="Output raw JSON")
    eval_p.add_argument("--api-key", default="", help="Google API key (or set GOOGLE_API_KEY)")
    eval_p.add_argument("--mock", action="store_true", help="Use mock scoring (no API key required)")

    # create command
    create_p = sub.add_parser("create", aliases=["c"], help="Create artwork via pipeline")
    create_p.add_argument("intent", help="Natural language creation intent")
    create_p.add_argument("--tradition", "-t", default="", help="Cultural tradition (auto-detected if empty)")
    create_p.add_argument("--subject", "-s", default="", help="Artwork subject/title")
    create_p.add_argument("--provider", default="nb2", help="Image generation provider")
    create_p.add_argument("--json", action="store_true", help="Output raw JSON")
    create_p.add_argument("--api-key", default="", help="VULCA API key (or set VULCA_API_KEY)")
    create_p.add_argument("--base-url", default="", help="VULCA API base URL")
    create_p.add_argument("--hitl", action="store_true", help="Enable human-in-the-loop (pause before decide)")
    create_p.add_argument("--weights", default="", help="Custom L1-L5 weights: 'L1=0.3,L2=0.2,...'")

    # traditions command
    sub.add_parser("traditions", aliases=["t"], help="List available cultural traditions")

    args = parser.parse_args(argv)

    if args.command in ("evaluate", "eval", "e"):
        _cmd_evaluate(args)
    elif args.command in ("create", "c"):
        if args.hitl:
            _cmd_create_hitl(args)
        else:
            _cmd_create(args)
    elif args.command in ("traditions", "t"):
        _cmd_traditions()
    else:
        parser.print_help()
        sys.exit(1)


def _cmd_evaluate(args: argparse.Namespace) -> None:
    import json as json_mod
    from vulca import evaluate

    skills = [s.strip() for s in args.skills.split(",") if s.strip()] if args.skills else None

    try:
        result = evaluate(
            args.image,
            intent=args.intent,
            tradition=args.tradition,
            subject=args.subject,
            skills=skills,
            api_key=args.api_key,
            mock=args.mock,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        import dataclasses
        print(json_mod.dumps(dataclasses.asdict(result), indent=2, ensure_ascii=False))
        return

    print(f"\n  VULCA Evaluation Result")
    print(f"  {'=' * 40}")
    print(f"  Score:     {result.score:.0%}")
    print(f"  Tradition: {result.tradition}")
    print(f"  Risk:      {result.risk_level}")
    print()
    print(f"  Dimensions:")
    names = {"L1": "Visual Perception", "L2": "Technical Execution", "L3": "Cultural Context", "L4": "Critical Interpretation", "L5": "Philosophical Aesthetics"}
    for level in ("L1", "L2", "L3", "L4", "L5"):
        score = result.dimensions.get(level, 0)
        bar = "\u2588" * int(score * 20) + "\u2591" * (20 - int(score * 20))
        print(f"    {level} {names[level]:<25s} {bar} {score:.0%}")
    print()
    print(f"  Summary: {result.summary}")

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


def _cmd_create(args: argparse.Namespace) -> None:
    import json as json_mod
    from vulca import create

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
    print(f"  Mode:      {result.mode}")
    print(f"  Tradition: {result.tradition}")
    print(f"  Rounds:    {result.total_rounds}")
    if result.best_candidate_id:
        print(f"  Best:      {result.best_candidate_id}")
    if result.summary:
        print(f"  Summary:   {result.summary}")
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
    print(f"\n  VULCA HITL Review")
    print(f"  {'=' * 40}")
    print(f"  Session:   {output.session_id}")
    print(f"  Tradition: {output.tradition}")
    print(f"  Status:    {output.status}")
    print()
    print(f"  L1-L5 Scores:")
    names = {"L1": "Visual Perception", "L2": "Technical Execution", "L3": "Cultural Context", "L4": "Critical Interpretation", "L5": "Philosophical Aesthetics"}
    scores = output.final_scores
    for level in ("L1", "L2", "L3", "L4", "L5"):
        score = scores.get(level, 0.0)
        bar = "\u2588" * int(score * 20) + "\u2591" * (20 - int(score * 20))
        print(f"    {level} {names[level]:<25s} {bar} {score:.0%}")
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
            pass
    else:
        print("  -> Quit. Session discarded.")
    print()


def _cmd_traditions() -> None:
    from vulca.cultural import TRADITION_WEIGHTS

    print("\n  Available Cultural Traditions:")
    print(f"  {'=' * 50}")
    for name, weights in TRADITION_WEIGHTS.items():
        emphasis = max(weights, key=weights.get)
        names = {"L1": "Visual", "L2": "Technical", "L3": "Cultural", "L4": "Critical", "L5": "Philosophical"}
        print(f"    {name:<25s} emphasis: {names.get(emphasis, emphasis)} ({weights[emphasis]:.0%})")
    print()


if __name__ == "__main__":
    main()
