from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_build_review_cli_writes_sqlite_json_and_html(tmp_path: Path, capsys):
    from scripts.vector_aesthetics_seed_cases import main as seed_main
    from scripts.vector_aesthetics_build_review import main as build_main

    root = tmp_path / "vector-aesthetics"
    output = tmp_path / "review"
    assert seed_main(["--root", str(root)]) == 0
    capsys.readouterr()

    rc = build_main(["--root", str(root), "--output", str(output)])

    captured = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(captured)
    assert payload["status"] == "written"
    assert payload["case_count"] == 12
    assert (root / "references.sqlite").exists()
    assert (output / "data" / "references.json").exists()
    assert (output / "index.html").exists()
    review_payload = json.loads((output / "data" / "references.json").read_text(encoding="utf-8"))
    assert all(case["coverage"]["screenshots"] in {"complete", "partial"} for case in review_payload["cases"])
    assert all(case["coverage"]["video"] in {"complete", "partial"} for case in review_payload["cases"])
    assert any("capture_failed" in json.dumps(case["captures"]) for case in review_payload["cases"])
    with (root / "references.sqlite").open("rb") as handle:
        assert handle.read(16).startswith(b"SQLite format 3")
