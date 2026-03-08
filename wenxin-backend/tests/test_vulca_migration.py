"""Test VULCA data migration and synchronization.

These tests require a fully initialised database with seeded models.
They are skipped automatically in CI / lightweight environments where
``init_db.py`` has not been executed.
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-at-least-32-chars")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_session():
    """Return an async DB session, or None if the DB is not initialised."""
    try:
        from app.core.database import AsyncSessionLocal
        session = AsyncSessionLocal()
        # Quick probe: can we query ai_models?
        from sqlalchemy import text
        result = await session.execute(text("SELECT count(*) FROM ai_models"))
        count = result.scalar()
        if count == 0:
            await session.close()
            return None
        return session
    except Exception:
        return None


async def _has_db() -> bool:
    """Return True if the database is available and has models."""
    session = await _get_session()
    if session is None:
        return False
    await session.close()
    return True


def _db_has_models() -> bool:
    """Check if the test.db has the ai_models table with data."""
    try:
        import sqlite3
        conn = sqlite3.connect("test.db")
        cursor = conn.execute("SELECT count(*) FROM ai_models")
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        return False


needs_db = pytest.mark.skipif(
    not _db_has_models(),
    reason="Requires initialised database with seeded models (run init_db.py)",
)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@needs_db
@pytest.mark.asyncio
async def test_vulca_field_existence():
    """Test that VULCA fields exist in ai_models table"""
    from app.core.database import AsyncSessionLocal
    from app.models.ai_model import AIModel
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(AIModel).limit(1))
        model = result.scalar_one_or_none()

        if model is None:
            pytest.skip("No models found in database")

        assert hasattr(model, "vulca_scores_47d"), "vulca_scores_47d field missing"
        assert hasattr(model, "vulca_cultural_perspectives"), "vulca_cultural_perspectives field missing"
        assert hasattr(model, "vulca_evaluation_date"), "vulca_evaluation_date field missing"
        assert hasattr(model, "vulca_sync_status"), "vulca_sync_status field missing"


@needs_db
@pytest.mark.asyncio
async def test_vulca_data_sync():
    """Test VULCA data synchronization"""
    from app.core.database import AsyncSessionLocal
    from app.models.ai_model import AIModel
    from app.services.vulca_sync_service import VULCASyncService
    from sqlalchemy import select

    sync_service = VULCASyncService()

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(AIModel).where(AIModel.is_active == True).limit(1))
        model = result.scalar_one_or_none()
        if model is None:
            pytest.skip("No active models in database")

        test_vulca_data = {
            "scores_47d": {f"dimension_{i}": min(100.0, 80.5 + i * 0.4) for i in range(47)},
            "cultural_perspectives": {
                "western": 85.0, "eastern": 82.0, "african": 78.0,
                "latin_american": 80.0, "middle_eastern": 79.0,
                "south_asian": 81.0, "oceanic": 77.0, "indigenous": 75.0,
            },
            "scores_6d": {
                "creativity": 85.0, "technique": 82.0, "emotion": 80.0,
                "context": 78.0, "innovation": 83.0, "impact": 81.0,
            },
        }

        success = await sync_service.sync_evaluation_to_model(
            model_id=model.id, vulca_evaluation=test_vulca_data, db=db,
        )
        assert success, "Sync failed"

        await db.refresh(model)
        assert model.vulca_scores_47d is not None
        assert model.vulca_cultural_perspectives is not None
        assert model.vulca_sync_status == "completed"


@needs_db
@pytest.mark.asyncio
async def test_vulca_data_integrity():
    """Test VULCA data integrity after sync"""
    from app.core.database import AsyncSessionLocal
    from app.models.ai_model import AIModel
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(AIModel).where(AIModel.vulca_sync_status == "completed"))
        models = result.scalars().all()

        if not models:
            pytest.skip("No models with completed VULCA sync")

        for model in models:
            if model.vulca_scores_47d:
                scores = json.loads(model.vulca_scores_47d) if isinstance(model.vulca_scores_47d, str) else model.vulca_scores_47d
                assert len(scores) == 47, f"Model {model.name} has {len(scores)} dimensions"
                for key, value in scores.items():
                    assert isinstance(value, (int, float)), f"Invalid score type for {key}"
                    assert 0 <= value <= 150, f"Score {value} out of range for {key}"

            if model.vulca_cultural_perspectives:
                perspectives = json.loads(model.vulca_cultural_perspectives) if isinstance(model.vulca_cultural_perspectives, str) else model.vulca_cultural_perspectives
                expected = ["western", "eastern", "african", "indigenous", "latin_american", "middle_eastern", "south_asian", "oceanic"]
                for p in expected:
                    assert p in perspectives, f"Missing {p} perspective"
                    assert 0 <= perspectives[p] <= 100, f"Invalid score for {p}"


@needs_db
@pytest.mark.asyncio
async def test_batch_sync():
    """Test batch synchronization of pending models"""
    from app.core.database import AsyncSessionLocal
    from app.services.vulca_sync_service import VULCASyncService

    sync_service = VULCASyncService()
    result = await sync_service.batch_sync_pending(limit=5)

    synced_count = result.get("synced", result.get("total_synced"))
    assert synced_count is not None
    assert "failed" in result
    assert synced_count >= 0
    assert result["failed"] >= 0


@needs_db
@pytest.mark.asyncio
async def test_migration_rollback():
    """Test that migration can be rolled back safely"""
    from app.core.database import AsyncSessionLocal
    from app.models.ai_model import AIModel
    from app.services.vulca_migration_service import VULCAMigrationService
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        migration_service = VULCAMigrationService(db)

        result = await db.execute(select(AIModel).where(AIModel.vulca_sync_status == "completed").limit(1))
        model = result.scalar_one_or_none()

        if not model:
            pytest.skip("No models with completed VULCA data")

        original_data = {
            "scores_47d": model.vulca_scores_47d,
            "cultural_perspectives": model.vulca_cultural_perspectives,
            "evaluation_date": model.vulca_evaluation_date,
            "sync_status": model.vulca_sync_status,
        }

        model.vulca_scores_47d = None
        model.vulca_cultural_perspectives = None
        model.vulca_evaluation_date = None
        model.vulca_sync_status = "pending"
        await db.commit()

        success = await migration_service.sync_single_evaluation(
            model_id=model.id,
            evaluation={
                "scores_47d": original_data["scores_47d"],
                "cultural_perspectives": original_data["cultural_perspectives"],
            },
        )
        assert success

        await db.refresh(model)
        assert model.vulca_scores_47d is not None
        assert model.vulca_sync_status == "completed"
