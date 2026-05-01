"""CLI harness for real-brief benchmark dry runs."""
from __future__ import annotations

import argparse
from datetime import date as date_type


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be >= 0")
    return parsed


def _selected_slugs(slug: str) -> list[str]:
    from vulca.real_brief.fixtures import (
        build_real_brief_fixtures,
        get_real_brief_fixture,
    )

    if slug == "all":
        return [fixture.slug for fixture in build_real_brief_fixtures()]
    return [get_real_brief_fixture(slug).slug]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write real-brief benchmark dry-run artifacts."
    )
    parser.add_argument("--slug", default="all")
    parser.add_argument("--date", default=date_type.today().isoformat())
    parser.add_argument(
        "--output-root",
        default="docs/product/experiments/real-brief-results",
    )
    parser.add_argument("--real-provider", action="store_true")
    parser.add_argument(
        "--provider",
        default="openai",
        choices=["openai", "gemini", "comfyui"],
    )
    parser.add_argument("--max-images", type=_non_negative_int, default=0)
    parser.add_argument(
        "--write-html-review",
        dest="write_html_review",
        action="store_true",
        default=True,
    )
    parser.add_argument(
        "--no-html-review",
        dest="write_html_review",
        action="store_false",
    )
    args = parser.parse_args(argv)

    if args.real_provider:
        raise RuntimeError("real provider execution is not implemented")

    from vulca.real_brief.artifacts import write_real_brief_dry_run

    slugs = _selected_slugs(args.slug)
    for slug in slugs:
        write_real_brief_dry_run(
            output_root=args.output_root,
            slug=slug,
            date=args.date,
            write_html_review=args.write_html_review,
        )
    return 0


def _cli() -> int:
    try:
        return main()
    except (RuntimeError, ValueError) as exc:
        raise SystemExit(f"error: {exc}") from None


if __name__ == "__main__":
    raise SystemExit(_cli())
