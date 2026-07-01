from __future__ import annotations

import json
from pathlib import Path
import sqlite3

from .schema import CaseRecord, case_to_review_dict, validate_case_folder


SCHEMA_SQL = """
drop table if exists cases;
drop table if exists module_payloads;
drop table if exists captures;
create table cases (
  id text primary key,
  title text not null,
  canonical_url text not null,
  source_type text not null,
  year integer not null,
  author_or_studio text not null,
  currentness text not null,
  review_status text not null,
  quality_score_total integer not null,
  coverage_json text not null,
  metadata_json text not null,
  review_json text not null
);
create table module_payloads (
  id integer primary key autoincrement,
  case_id text not null,
  module_type text not null,
  payload_json text not null,
  evidence_refs_json text not null,
  confidence text not null,
  review_status text not null,
  review_notes text not null
);
create table captures (
  id text not null,
  case_id text not null,
  evidence_type text not null,
  path_or_url text not null,
  capture_method text not null,
  rights_status text not null,
  confidence text not null,
  notes text not null,
  primary key (case_id, id)
);
"""


def _case_dirs(root: Path) -> list[Path]:
    cases_root = root / "cases"
    if not cases_root.is_dir():
        raise ValueError(f"cases folder missing: {cases_root}")
    case_dirs = sorted(path for path in cases_root.iterdir() if path.is_dir())
    if not case_dirs:
        raise ValueError(f"no case folders found under {cases_root}")
    return case_dirs


def _sqlite_tmp_path(sqlite_path: Path) -> Path:
    return sqlite_path.with_name(f".{sqlite_path.name}.tmp")


def _write_sqlite(records: list[CaseRecord], sqlite_path: Path, dataset_root: Path) -> None:
    tmp_sqlite_path = _sqlite_tmp_path(sqlite_path)
    if tmp_sqlite_path.exists():
        tmp_sqlite_path.unlink()

    try:
        with sqlite3.connect(tmp_sqlite_path) as conn:
            conn.executescript(SCHEMA_SQL)
            for record in records:
                conn.execute(
                    """
                    insert into cases
                    (id, title, canonical_url, source_type, year, author_or_studio, currentness,
                     review_status, quality_score_total, coverage_json, metadata_json, review_json)
                    values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.id,
                        record.metadata["title"],
                        record.metadata["canonical_url"],
                        record.metadata["source_type"],
                        int(record.metadata["year"]),
                        record.metadata["author_or_studio"],
                        record.metadata["currentness"],
                        record.metadata["review_status"],
                        record.quality_score_total,
                        json.dumps(record.coverage, sort_keys=True),
                        json.dumps(record.metadata, sort_keys=True),
                        json.dumps(case_to_review_dict(record, dataset_root=dataset_root), sort_keys=True),
                    ),
                )
                for module in record.metadata["modules"]:
                    conn.execute(
                        """
                        insert into module_payloads
                        (case_id, module_type, payload_json, evidence_refs_json, confidence, review_status, review_notes)
                        values (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            record.id,
                            module["module_type"],
                            json.dumps(module["payload"], sort_keys=True),
                            json.dumps(module.get("evidence_refs", []), sort_keys=True),
                            module["confidence"],
                            module["review_status"],
                            module.get("review_notes", ""),
                        ),
                    )
                for capture in record.metadata["captures"]:
                    conn.execute(
                        """
                        insert into captures
                        (id, case_id, evidence_type, path_or_url, capture_method, rights_status, confidence, notes)
                        values (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            capture["id"],
                            record.id,
                            capture["evidence_type"],
                            capture["path_or_url"],
                            capture["capture_method"],
                            capture["rights_status"],
                            capture["confidence"],
                            capture["notes"],
                        ),
                    )
        tmp_sqlite_path.replace(sqlite_path)
    finally:
        if tmp_sqlite_path.exists():
            tmp_sqlite_path.unlink()


def compile_database(root: Path, sqlite_path: Path) -> list[CaseRecord]:
    records = [validate_case_folder(case_dir) for case_dir in _case_dirs(root)]
    seen_ids: set[str] = set()
    duplicate_ids: set[str] = set()
    for record in records:
        if record.id in seen_ids:
            duplicate_ids.add(record.id)
        seen_ids.add(record.id)
    if duplicate_ids:
        raise ValueError(f"duplicate case ids: {sorted(duplicate_ids)}")
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    _write_sqlite(records, sqlite_path, root)
    return records


def _review_payload(cases: list[dict[str, object]]) -> dict[str, object]:
    def is_multimodal_complete(case: dict[str, object]) -> bool:
        coverage = case.get("coverage", {})
        if not isinstance(coverage, dict):
            return False
        return coverage.get("screenshots") == "complete" and coverage.get("video") == "complete"

    def is_gold_case(case: dict[str, object]) -> bool:
        coverage = case.get("coverage", {})
        if not isinstance(coverage, dict):
            return False
        return (
            is_multimodal_complete(case)
            and not case.get("data_quality_flags")
            and coverage.get("code_anatomy") == "complete"
            and coverage.get("lesson") == "complete"
            and coverage.get("vulca_translation") == "complete"
            and coverage.get("module_payloads") == "complete"
        )

    def is_seed_stub(case: dict[str, object]) -> bool:
        flags = case.get("data_quality_flags", [])
        return isinstance(flags, list) and any("seed" in str(flag) or flag == "metadata_only_modules" for flag in flags)

    payload = {
        "schema_version": 1,
        "summary": {
            "case_count": len(cases),
            "shortlist_count": sum(1 for case in cases if case["review_status"] == "shortlist"),
            "candidate_count": sum(1 for case in cases if case["review_status"] == "candidate"),
            "gold_case_count": sum(1 for case in cases if is_gold_case(case)),
            "seed_stub_case_count": sum(1 for case in cases if is_seed_stub(case)),
            "multimodal_complete_count": sum(1 for case in cases if is_multimodal_complete(case)),
        },
        "cases": cases,
    }
    return payload


def _review_cases_from_sqlite(sqlite_path: Path) -> list[dict[str, object]]:
    with sqlite3.connect(sqlite_path) as conn:
        rows = conn.execute("select review_json from cases order by id").fetchall()
    return [json.loads(row[0]) for row in rows]


def export_review_json(records: list[CaseRecord], output_path: Path) -> Path:
    cases = [case_to_review_dict(record) for record in sorted(records, key=lambda item: item.id)]
    payload = _review_payload(cases)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def export_review_json_from_sqlite(sqlite_path: Path, output_path: Path) -> Path:
    cases = _review_cases_from_sqlite(sqlite_path)
    payload = _review_payload(cases)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path
