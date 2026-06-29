from __future__ import annotations

import json
from pathlib import Path


def test_seed_cases_write_twelve_valid_case_folders(tmp_path: Path):
    from vulca.vector_aesthetics.schema import validate_case_folder
    from vulca.vector_aesthetics.seeds import SEED_CASES, write_seed_cases

    written = write_seed_cases(tmp_path)

    assert len(SEED_CASES) == 12
    assert len(written) == 12
    assert len({path.name for path in written}) == 12
    records = [validate_case_folder(path) for path in written]
    assert {record.metadata["review_status"] for record in records} == {"candidate"}
    assert all(record.coverage["metadata"] == "complete" for record in records)
    assert all(record.coverage["screenshots"] in {"complete", "partial"} for record in records)
    assert all(record.coverage["video"] in {"complete", "partial"} for record in records)
    assert all("Primitive:" in record.anatomy and "Technique:" in record.anatomy for record in records)
    assert all("minimal_rebuild_exercise" in record.lesson for record in records)
    assert sum("Moment:" in record.anatomy for record in records) >= 6
    assert sum("runtime_target:" in record.lesson for record in records) >= 3


def test_seed_cases_use_source_link_only_for_unclear_assets(tmp_path: Path):
    from vulca.vector_aesthetics.seeds import write_seed_cases

    written = write_seed_cases(tmp_path)

    for case_dir in written:
        metadata = json.loads((case_dir / "metadata.json").read_text(encoding="utf-8"))
        for capture in metadata["captures"]:
            assert capture["rights_status"] in {"source_link_only", "open_asset", "local_capture", "unclear"}
        failure_types = {
            capture["evidence_type"]
            for capture in metadata["captures"]
            if capture["interaction"] == "capture_failed"
        }
        assert {"screenshot", "video"} <= failure_types
        assert "/Users/" not in json.dumps(metadata)
        assert "private://local_path/" not in json.dumps(metadata)


def test_seed_script_writes_requested_root(tmp_path: Path, capsys):
    from scripts.vector_aesthetics_seed_cases import main

    rc = main(["--root", str(tmp_path)])

    captured = capsys.readouterr().out
    assert rc == 0
    assert '"status": "written"' in captured
    assert len(list((tmp_path / "cases").iterdir())) == 12
