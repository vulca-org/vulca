from __future__ import annotations

import json
from pathlib import Path
import sqlite3


def test_compile_database_writes_case_and_module_rows(tmp_path: Path):
    from vulca.vector_aesthetics.compiler import compile_database
    from vulca.vector_aesthetics.seeds import write_seed_cases

    root = tmp_path / "vector-aesthetics"
    write_seed_cases(root)
    sqlite_path = root / "references.sqlite"

    records = compile_database(root, sqlite_path)

    assert len(records) == 12
    with sqlite3.connect(sqlite_path) as conn:
        assert conn.execute("select count(*) from cases").fetchone()[0] == 12
        assert conn.execute("select count(*) from module_payloads").fetchone()[0] == 40
        assert conn.execute("select count(*) from captures").fetchone()[0] == 36


def test_export_review_json_is_bounded_and_sorted(tmp_path: Path):
    from vulca.vector_aesthetics.compiler import (
        compile_database,
        export_review_json,
        export_review_json_from_sqlite,
    )
    from vulca.vector_aesthetics.seeds import write_seed_cases

    root = tmp_path / "vector-aesthetics"
    write_seed_cases(root)
    sqlite_path = root / "references.sqlite"
    records = compile_database(root, sqlite_path)
    output_path = tmp_path / "references.json"
    sqlite_output_path = tmp_path / "references-from-sqlite.json"

    export_review_json(records, output_path)
    export_review_json_from_sqlite(sqlite_path, sqlite_output_path)
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert payload["schema_version"] == 1
    assert payload["summary"]["case_count"] == 12
    assert payload["summary"]["gold_case_count"] == 0
    assert payload["summary"]["seed_stub_case_count"] == 12
    assert payload["summary"]["multimodal_complete_count"] == 0
    assert [case["id"] for case in payload["cases"]] == sorted(case["id"] for case in payload["cases"])
    assert all(case["coverage"]["module_payloads"] == "seed_stub" for case in payload["cases"])
    assert all("metadata_only_modules" in case["data_quality_flags"] for case in payload["cases"])
    assert "sk-" not in json.dumps(payload)
    assert output_path.read_text(encoding="utf-8") == sqlite_output_path.read_text(encoding="utf-8")


def test_compile_database_exports_stable_non_absolute_case_paths(tmp_path: Path):
    from vulca.vector_aesthetics.compiler import compile_database, export_review_json_from_sqlite
    from vulca.vector_aesthetics.seeds import write_seed_cases

    root = (tmp_path / "vector-aesthetics").resolve()
    write_seed_cases(root)
    sqlite_path = root / "references.sqlite"
    output_path = tmp_path / "references.json"

    compile_database(root, sqlite_path)
    export_review_json_from_sqlite(sqlite_path, output_path)

    payload_text = output_path.read_text(encoding="utf-8")
    payload = json.loads(payload_text)
    assert str(tmp_path) not in payload_text
    assert all(case["case_rel"].startswith("cases/") for case in payload["cases"])
    assert all(not Path(case["case_rel"]).is_absolute() for case in payload["cases"])


def test_compile_database_is_deterministic_for_same_case_folders(tmp_path: Path):
    from vulca.vector_aesthetics.compiler import compile_database, export_review_json
    from vulca.vector_aesthetics.seeds import write_seed_cases

    root = tmp_path / "vector-aesthetics"
    write_seed_cases(root)
    first_records = compile_database(root, root / "first.sqlite")
    second_records = compile_database(root, root / "second.sqlite")
    first_json = export_review_json(first_records, tmp_path / "first.json").read_text(encoding="utf-8")
    second_json = export_review_json(second_records, tmp_path / "second.json").read_text(encoding="utf-8")

    assert first_json == second_json


def test_compile_database_keeps_existing_sqlite_when_validation_fails(tmp_path: Path):
    from vulca.vector_aesthetics.compiler import compile_database
    from vulca.vector_aesthetics.seeds import write_seed_cases

    root = tmp_path / "vector-aesthetics"
    write_seed_cases(root)
    sqlite_path = root / "references.sqlite"
    compile_database(root, sqlite_path)
    before = sqlite_path.read_bytes()
    bad_case = root / "cases" / "bad-case"
    bad_case.mkdir()
    (bad_case / "metadata.json").write_text("{}", encoding="utf-8")

    try:
        compile_database(root, sqlite_path)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid case unexpectedly compiled")

    assert sqlite_path.read_bytes() == before


def test_compile_database_raises_when_cases_root_missing_and_preserves_sqlite(tmp_path: Path):
    from vulca.vector_aesthetics.compiler import compile_database
    from vulca.vector_aesthetics.seeds import write_seed_cases

    root = tmp_path / "vector-aesthetics"
    write_seed_cases(root)
    sqlite_path = root / "references.sqlite"
    compile_database(root, sqlite_path)
    before = sqlite_path.read_bytes()

    missing_root = tmp_path / "missing-root"

    try:
        compile_database(missing_root, sqlite_path)
    except ValueError as exc:
        assert "cases" in str(exc)
    else:
        raise AssertionError("missing cases root unexpectedly compiled")

    assert sqlite_path.read_bytes() == before
