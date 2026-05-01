"""CLI wrapper for building the real-brief workflow review surface."""
from __future__ import annotations

import argparse
import json


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a workflow-level HTML review for adapted real briefs."
    )
    parser.add_argument("--root", required=True)
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    from vulca.real_brief.workflow_review_html import write_workflow_review_html

    html_path = write_workflow_review_html(root=args.root, output=args.output)
    print(
        json.dumps(
            {
                "status": "written",
                "html": str(html_path),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def _cli() -> int:
    try:
        return main()
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise SystemExit(f"error: {exc}") from None


if __name__ == "__main__":
    raise SystemExit(_cli())
