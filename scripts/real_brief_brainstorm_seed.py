"""CLI wrapper for seeding /visual-brainstorm proposals from real-brief packages."""
from __future__ import annotations

import argparse
import json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Seed a draft /visual-brainstorm proposal from real-brief artifacts."
    )
    parser.add_argument("--root", default=".")
    parser.add_argument("--slug", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    from vulca.real_brief.brainstorm_seed import (
        seed_real_brief_brainstorm_proposal,
    )

    result = seed_real_brief_brainstorm_proposal(
        root=args.root,
        slug=args.slug,
        date=args.date,
        force=args.force,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _cli() -> int:
    try:
        return main()
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise SystemExit(f"error: {exc}") from None


if __name__ == "__main__":
    raise SystemExit(_cli())
