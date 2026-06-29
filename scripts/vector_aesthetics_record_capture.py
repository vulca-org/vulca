from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Record local evidence or capture failures for a vector aesthetics case."
    )
    parser.add_argument("--case-dir", required=True)
    parser.add_argument("--failure", action="store_true")
    parser.add_argument("--evidence-type", required=True)
    parser.add_argument("--path-or-url")
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--notes", required=True)
    parser.add_argument("--id", default="")
    parser.add_argument("--viewport", default="none")
    parser.add_argument("--interaction", default="none")
    parser.add_argument("--captured-at", default="2026-06-29")
    args = parser.parse_args(argv)

    from vulca.vector_aesthetics.captures import add_capture, record_capture_failure

    case_dir = Path(args.case_dir)
    if args.failure:
        payload = record_capture_failure(
            case_dir,
            evidence_type=args.evidence_type,
            notes=args.notes,
            source_url=args.source_url,
        )
    else:
        if not args.path_or_url:
            raise SystemExit("error: --path-or-url is required unless --failure is set")
        payload = add_capture(
            case_dir,
            {
                "id": args.id or f"{args.evidence_type}-{args.interaction}",
                "evidence_type": args.evidence_type,
                "path_or_url": args.path_or_url,
                "capture_method": "manual_browser",
                "viewport": args.viewport,
                "interaction": args.interaction,
                "captured_at": args.captured_at,
                "source_url": args.source_url,
                "confidence": "medium",
                "rights_status": "local_capture",
                "notes": args.notes,
            },
        )
    print(
        json.dumps(
            {
                "status": "recorded",
                "case_id": payload["id"],
                "capture_count": len(payload["captures"]),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
