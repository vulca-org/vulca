"""Tests for Digestion V2 Alembic migration script — validates structure without executing."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

MIGRATION_DIR = Path(__file__).resolve().parent.parent.parent / "wenxin-backend" / "alembic" / "versions"
MIGRATION_FILE = MIGRATION_DIR / "digestion_v2_schema.py"


def test_migration_file_exists():
    """The digestion V2 migration script must exist."""
    assert MIGRATION_FILE.exists(), f"Migration not found at {MIGRATION_FILE}"


def test_migration_has_valid_revision():
    """Migration must have revision and down_revision identifiers."""
    content = MIGRATION_FILE.read_text(encoding="utf-8")

    assert "revision" in content
    assert "down_revision" in content
    # Should chain from the current head
    assert "vulca_47d_complete" in content, "down_revision should reference vulca_47d_complete"


def test_migration_creates_studio_sessions_table():
    """Migration must create studio_sessions table with required columns."""
    content = MIGRATION_FILE.read_text(encoding="utf-8")

    assert "studio_sessions" in content
    # Key columns
    assert "brief" in content  # JSONB brief storage
    assert "state" in content
    assert "satisfaction" in content
    assert "iteration_count" in content
    assert "created_at" in content


def test_migration_creates_artifacts_table():
    """Migration must create artifacts table for L1-L5 analysis."""
    content = MIGRATION_FILE.read_text(encoding="utf-8")

    assert "artifacts" in content
    assert "artifact_type" in content
    assert "analysis" in content  # JSONB analysis
    assert "session_id" in content


def test_migration_creates_signals_table():
    """Migration must create signals table for per-action data."""
    content = MIGRATION_FILE.read_text(encoding="utf-8")

    assert "signals" in content
    assert "action" in content
    assert "phase" in content
    assert "raw_data" in content or "extracted_preferences" in content


def test_migration_creates_evolved_patterns_table():
    """Migration must create evolved_patterns table."""
    content = MIGRATION_FILE.read_text(encoding="utf-8")

    assert "evolved_patterns" in content
    assert "pattern_type" in content
    assert "pattern_key" in content
    assert "confidence" in content


def test_migration_creates_brief_templates_table():
    """Migration must create brief_templates table."""
    content = MIGRATION_FILE.read_text(encoding="utf-8")

    assert "brief_templates" in content
    assert "template_brief" in content
    assert "avg_satisfaction" in content


def test_migration_has_downgrade():
    """Migration must have a downgrade function that drops all tables."""
    content = MIGRATION_FILE.read_text(encoding="utf-8")

    tree = ast.parse(content)
    func_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

    assert "upgrade" in func_names
    assert "downgrade" in func_names

    # Downgrade should drop tables
    assert "drop_table" in content or "drop_all" in content


def test_migration_has_indexes():
    """Migration must create indexes for common query patterns."""
    content = MIGRATION_FILE.read_text(encoding="utf-8")

    assert "create_index" in content.lower() or "Index" in content
