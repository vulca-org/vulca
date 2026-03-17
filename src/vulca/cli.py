"""VULCA command-line interface.

Usage::

    vulca evaluate painting.jpg
    vulca evaluate painting.jpg --intent "check ink wash style"
    vulca evaluate painting.jpg --tradition chinese_xieyi
    vulca evaluate painting.jpg --skills brand,audience,trend
"""

from __future__ import annotations

import argparse
import sys

from vulca._version import __version__


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

    # create command
    create_p = sub.add_parser("create", aliases=["c"], help="Create artwork via pipeline")
    create_p.add_argument("intent", help="Natural language creation intent")
    create_p.add_argument("--tradition", "-t", default="", help="Cultural tradition (auto-detected if empty)")
    create_p.add_argument("--subject", "-s", default="", help="Artwork subject/title")
    create_p.add_argument("--provider", default="nb2", help="Image generation provider")
    create_p.add_argument("--json", action="store_true", help="Output raw JSON")
    create_p.add_argument("--api-key", default="", help="VULCA API key (or set VULCA_API_KEY)")
    create_p.add_argument("--base-url", default="", help="VULCA API base URL")

    # traditions command
    sub.add_parser("traditions", aliases=["t"], help="List available cultural traditions")

    args = parser.parse_args(argv)

    if args.command in ("evaluate", "eval", "e"):
        _cmd_evaluate(args)
    elif args.command in ("create", "c"):
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

    try:
        result = create(
            args.intent,
            tradition=args.tradition,
            subject=args.subject,
            provider=args.provider,
            api_key=args.api_key,
            base_url=args.base_url,
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
