"""CLI wrapper for importing real-brief packages into visual workflow seeds."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _resolve_source_package(args: argparse.Namespace) -> Path:
    if args.source_package:
        return Path(args.source_package)
    if not args.source_root or not args.slug or not args.date:
        raise RuntimeError(
            "--source-package or all of --source-root, --slug, and --date is required"
        )
    return Path(args.source_root) / f"{args.date}-{args.slug}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Import a real-brief benchmark package into Vulca visual workflow seeds."
        )
    )
    parser.add_argument("--source-package")
    parser.add_argument("--source-root")
    parser.add_argument("--slug")
    parser.add_argument("--root", default=".")
    parser.add_argument("--date", required=True)
    parser.add_argument("--force-discovery", action="store_true")
    parser.add_argument("--force-real-brief", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    source_package = _resolve_source_package(args)

    from vulca.real_brief.workflow_adapter import adapt_real_brief_package

    result = adapt_real_brief_package(
        source_package=source_package,
        root=args.root,
        date=args.date,
        force_discovery=args.force_discovery,
        force_real_brief=args.force_real_brief,
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
