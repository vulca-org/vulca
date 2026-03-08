"""OpenAPI schema contract tests.

Verify structural properties of the OpenAPI schema to catch accidental
route deletions or breaking schema changes.  The tests are deliberately
*not* fragile -- they check for the presence of key sections and
endpoints rather than exact field-by-field equality.
"""

import json
import os
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Environment defaults (CI-safe)
# ---------------------------------------------------------------------------
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-at-least-32-chars")

from app.main import app  # noqa: E402  (after env setup)

SNAPSHOT_DIR = pathlib.Path(__file__).parent / "snapshots"
SNAPSHOT_PATH = SNAPSHOT_DIR / "openapi_snapshot.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_schema() -> dict:
    """Return the current OpenAPI schema dict."""
    schema = app.openapi()
    assert isinstance(schema, dict), "app.openapi() must return a dict"
    return schema


def _paths(schema: dict) -> list[str]:
    """Return sorted list of path strings."""
    return sorted(schema.get("paths", {}).keys())


# ---------------------------------------------------------------------------
# 1. Structural integrity
# ---------------------------------------------------------------------------

class TestSchemaStructure:
    """The schema must contain required top-level sections."""

    def test_has_openapi_version(self):
        schema = _get_schema()
        assert "openapi" in schema
        assert schema["openapi"].startswith("3.")

    def test_has_info_section(self):
        schema = _get_schema()
        assert "info" in schema
        info = schema["info"]
        assert "title" in info
        assert "version" in info

    def test_has_paths_section(self):
        schema = _get_schema()
        assert "paths" in schema
        assert len(schema["paths"]) > 0, "Schema must expose at least one path"

    def test_has_components_section(self):
        schema = _get_schema()
        assert "components" in schema, (
            "Schema should have a components section (schemas, securitySchemes, etc.)"
        )


# ---------------------------------------------------------------------------
# 2. Key endpoints existence
# ---------------------------------------------------------------------------

class TestKeyEndpoints:
    """Critical route families must be present in the schema."""

    def test_health_endpoint(self):
        paths = _paths(_get_schema())
        assert "/health" in paths, f"/health missing from {paths}"

    def test_create_endpoints(self):
        paths = _paths(_get_schema())
        matches = [p for p in paths if "create" in p.lower()]
        assert len(matches) >= 1, (
            f"Expected at least one 'create' endpoint, found none in {paths}"
        )

    def test_evaluate_endpoints(self):
        paths = _paths(_get_schema())
        matches = [p for p in paths if "evaluat" in p.lower()]
        assert len(matches) >= 1, (
            f"Expected at least one 'evaluate' endpoint, found none in {paths}"
        )

    def test_skills_endpoints(self):
        paths = _paths(_get_schema())
        matches = [p for p in paths if "skill" in p.lower()]
        assert len(matches) >= 1, (
            f"Expected at least one 'skills' endpoint, found none in {paths}"
        )

    def test_auth_endpoints(self):
        paths = _paths(_get_schema())
        matches = [p for p in paths if "auth" in p.lower()]
        assert len(matches) >= 1, (
            f"Expected at least one 'auth' endpoint, found none in {paths}"
        )


# ---------------------------------------------------------------------------
# 3. Snapshot management
# ---------------------------------------------------------------------------

class TestSnapshot:
    """Save / compare a snapshot of endpoint paths to prevent regressions."""

    @staticmethod
    def _save_snapshot(paths: list[str]) -> None:
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_PATH.write_text(
            json.dumps({"endpoint_count": len(paths), "paths": paths}, indent=2)
            + "\n"
        )

    @staticmethod
    def _load_snapshot() -> dict | None:
        if not SNAPSHOT_PATH.exists():
            return None
        return json.loads(SNAPSHOT_PATH.read_text())

    def test_snapshot_create_or_compare(self):
        """On first run, create the snapshot.  On subsequent runs, compare."""
        current_paths = _paths(_get_schema())
        existing = self._load_snapshot()

        if existing is None:
            # First run -- write snapshot
            self._save_snapshot(current_paths)
            pytest.skip("Snapshot created for the first time; re-run to compare.")
        else:
            # Compare: current must be a superset (no accidental deletions)
            snapshot_paths = set(existing["paths"])
            current_set = set(current_paths)
            removed = snapshot_paths - current_set
            assert not removed, (
                f"Endpoints removed since last snapshot: {sorted(removed)}. "
                "If intentional, delete tests/snapshots/openapi_snapshot.json and re-run."
            )

    def test_endpoint_count_does_not_drop(self):
        """Total route count must not decrease compared to snapshot."""
        current_paths = _paths(_get_schema())
        existing = self._load_snapshot()

        if existing is None:
            pytest.skip("No snapshot yet; run test_snapshot_create_or_compare first.")

        old_count = existing["endpoint_count"]
        new_count = len(current_paths)
        assert new_count >= old_count, (
            f"Endpoint count dropped from {old_count} to {new_count}. "
            f"Missing routes? Delete snapshot to reset."
        )

    def test_update_snapshot_if_endpoints_added(self):
        """If new endpoints were added, update the snapshot automatically."""
        current_paths = _paths(_get_schema())
        existing = self._load_snapshot()

        if existing is None:
            pytest.skip("No snapshot yet.")

        if len(current_paths) > existing["endpoint_count"]:
            self._save_snapshot(current_paths)
            # Not a failure -- just an informational update
