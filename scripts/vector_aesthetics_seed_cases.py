from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write seed case folders for the 3D vector aesthetics corpus.")
    parser.add_argument("--root", default="data/vector-aesthetics")
    parser.add_argument("--captured-at")
    args = parser.parse_args(argv)

    from vulca.vector_aesthetics.seeds import write_seed_cases

    written = write_seed_cases(Path(args.root), captured_at=args.captured_at)
    print(
        json.dumps(
            {"status": "written", "root": args.root, "case_count": len(written), "cases": [path.name for path in written]},
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
