from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the 3D vector aesthetics learning DB review atlas.")
    parser.add_argument("--root", default="data/vector-aesthetics")
    parser.add_argument("--output", default="output/review/3d-vector-aesthetics-learning-db")
    args = parser.parse_args(argv)

    from vulca.vector_aesthetics.compiler import compile_database, export_review_json_from_sqlite
    from vulca.vector_aesthetics.review_html import write_review_html

    root = Path(args.root)
    output = Path(args.output)
    sqlite_path = root / "references.sqlite"
    review_json = output / "data" / "references.json"
    html_path = output / "index.html"

    records = compile_database(root, sqlite_path)
    export_review_json_from_sqlite(sqlite_path, review_json)
    write_review_html(review_json, html_path)
    print(
        json.dumps(
            {
                "status": "written",
                "case_count": len(records),
                "sqlite": str(sqlite_path),
                "review_json": str(review_json),
                "html": str(html_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
