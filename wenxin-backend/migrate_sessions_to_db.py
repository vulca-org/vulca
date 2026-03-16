#!/usr/bin/env python3
"""Migrate sessions.jsonl data to Supabase PostgreSQL.

Usage:
    DATABASE_URL=postgresql://... python migrate_sessions_to_db.py

Reads from app/prototype/data/sessions.jsonl and inserts into prototype_sessions table.
"""

import json
import os
import sys
import uuid

# Ensure the app is importable
sys.path.insert(0, os.path.dirname(__file__))


def main():
    jsonl_path = os.path.join(
        os.path.dirname(__file__), "app", "prototype", "data", "sessions.jsonl"
    )
    if not os.path.exists(jsonl_path):
        print(f"ERROR: {jsonl_path} not found")
        sys.exit(1)

    # Read all sessions
    sessions = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                sessions.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"  WARN: skipping line {i+1}: {e}")

    print(f"Read {len(sessions)} sessions from {jsonl_path}")

    # Assign session_id to entries that don't have one
    for s in sessions:
        if not s.get("session_id"):
            s["session_id"] = f"sess-{uuid.uuid4().hex[:12]}"

    # Import DB machinery
    from app.core.database import Base, _sync_engine, SyncSessionLocal
    from app.models.prototype_session import PrototypeSession

    # Create table if not exists
    Base.metadata.create_all(_sync_engine)
    print("Table prototype_sessions ensured.")

    # Check existing count
    with SyncSessionLocal() as db:
        existing = db.query(PrototypeSession).count()
        print(f"Existing rows in DB: {existing}")

    # Insert in batches
    BATCH = 100
    inserted = 0
    skipped = 0
    for i in range(0, len(sessions), BATCH):
        batch = sessions[i:i + BATCH]
        with SyncSessionLocal() as db:
            for s in batch:
                # Check if already exists
                exists = db.query(PrototypeSession).filter(
                    PrototypeSession.session_id == s["session_id"]
                ).first()
                if exists:
                    skipped += 1
                    continue

                row = PrototypeSession(
                    session_id=s["session_id"],
                    mode=s.get("mode", "create"),
                    intent=s.get("intent", ""),
                    tradition=s.get("tradition", "default"),
                    subject=s.get("subject", ""),
                    user_type=s.get("user_type", "human"),
                    user_id=s.get("user_id", ""),
                    media_type=s.get("media_type", "image"),
                    rounds=s.get("rounds", []),
                    final_scores=s.get("final_scores", {}),
                    final_weighted_total=s.get("final_weighted_total", 0.0),
                    best_image_url=s.get("best_image_url", ""),
                    risk_flags=s.get("risk_flags", []),
                    recommendations=s.get("recommendations", []),
                    feedback=s.get("feedback", []),
                    cultural_features=s.get("cultural_features", {}),
                    critic_insights=s.get("critic_insights", []),
                    candidate_choice_index=s.get("candidate_choice_index", -1),
                    time_to_select_ms=s.get("time_to_select_ms", 0),
                    downloaded=s.get("downloaded", False),
                    published=s.get("published", False),
                    likes_count=s.get("likes_count", 0),
                    total_rounds=s.get("total_rounds", 0),
                    total_latency_ms=s.get("total_latency_ms", 0),
                    total_cost_usd=s.get("total_cost_usd", 0.0),
                    created_at=s.get("created_at", 0.0),
                )
                db.add(row)
                inserted += 1
            db.commit()
        print(f"  Batch {i//BATCH + 1}: {len(batch)} processed")

    print(f"\nDone: {inserted} inserted, {skipped} skipped (already existed)")

    # Verify
    with SyncSessionLocal() as db:
        total = db.query(PrototypeSession).count()
        with_images = db.query(PrototypeSession).filter(
            PrototypeSession.best_image_url != "",
            PrototypeSession.best_image_url.isnot(None),
        ).count()
        print(f"Final DB state: {total} sessions, {with_images} with images")


if __name__ == "__main__":
    main()
