#!/usr/bin/env python3
"""Seed prototype data files for cold start.

Idempotent: skips files that already exist.
Creates:
  - app/prototype/data/skills_marketplace.jsonl
  - app/prototype/data/skills_votes.jsonl
  - app/prototype/data/feedback.jsonl
  - app/prototype/data/evolved_context.json
  - app/prototype/data/quality_baseline.json
  - data/agent_logs/  (directory)
"""

import json
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent

PROTO_DATA = BASE / "app" / "prototype" / "data"
AGENT_LOGS = BASE / "data" / "agent_logs"

SEED_SKILLS = [
    {"id": "1", "name": "Brand Consistency", "description": "Evaluate visual consistency with brand guidelines including logo usage, typography, and color palette adherence.", "tags": ["brand", "design"], "author": "vulca", "version": "1.0.0", "created_at": "2026-01-01T00:00:00+00:00", "upvotes": 42, "downvotes": 3},
    {"id": "2", "name": "Audience Fit", "description": "Score content for target demographic appeal across 12 audience segments with cultural sensitivity.", "tags": ["audience", "marketing"], "author": "vulca", "version": "1.0.0", "created_at": "2026-01-01T00:00:00+00:00", "upvotes": 38, "downvotes": 5},
    {"id": "3", "name": "Trend Alignment", "description": "Match against current aesthetic trends with weekly sync from design trend databases.", "tags": ["trends", "design"], "author": "vulca", "version": "1.0.0", "created_at": "2026-01-01T00:00:00+00:00", "upvotes": 29, "downvotes": 2},
    {"id": "4", "name": "Accessibility Check", "description": "Verify content meets WCAG 2.1 AA standards for color contrast, text size, and interactive elements.", "tags": ["accessibility", "quality"], "author": "community", "version": "1.0.0", "created_at": "2026-01-01T00:00:00+00:00", "upvotes": 55, "downvotes": 1},
    {"id": "5", "name": "Emotional Resonance", "description": "Analyze the emotional impact of visual content across 8 dimensions including warmth, trust, and excitement.", "tags": ["emotion", "audience"], "author": "vulca", "version": "1.0.0", "created_at": "2026-01-01T00:00:00+00:00", "upvotes": 33, "downvotes": 4},
    {"id": "6", "name": "Performance Benchmark", "description": "Measure inference latency and resource consumption for model evaluation pipelines.", "tags": ["performance", "quality"], "author": "community", "version": "1.2.0", "created_at": "2026-01-01T00:00:00+00:00", "upvotes": 21, "downvotes": 0},
]

DEFAULT_EVOLVED_CONTEXT = {
    "creativity_weight": 0.20,
    "technique_weight": 0.20,
    "emotion_weight": 0.15,
    "context_weight": 0.15,
    "innovation_weight": 0.15,
    "impact_weight": 0.15,
    "evolved_at": None,
    "generation": 0,
}

DEFAULT_QUALITY_BASELINE = {
    "avg_score": 0.0,
    "total_evaluations": 0,
    "dimension_scores": {},
    "updated_at": None,
}


def write_jsonl(path: Path, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def write_json(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main() -> None:
    PROTO_DATA.mkdir(parents=True, exist_ok=True)
    AGENT_LOGS.mkdir(parents=True, exist_ok=True)

    files = {
        PROTO_DATA / "skills_marketplace.jsonl": lambda p: write_jsonl(p, SEED_SKILLS),
        PROTO_DATA / "skills_votes.jsonl": lambda p: write_jsonl(p, []),
        PROTO_DATA / "skills_discussions.jsonl": lambda p: write_jsonl(p, []),
        PROTO_DATA / "skills_discussion_votes.jsonl": lambda p: write_jsonl(p, []),
        PROTO_DATA / "feedback.jsonl": lambda p: write_jsonl(p, []),
        PROTO_DATA / "evolved_context.json": lambda p: write_json(p, DEFAULT_EVOLVED_CONTEXT),
        PROTO_DATA / "quality_baseline.json": lambda p: write_json(p, DEFAULT_QUALITY_BASELINE),
    }

    for path, writer in files.items():
        if path.exists():
            print(f"  SKIP {path.relative_to(BASE)} (already exists)")
        else:
            writer(path)
            print(f"  SEED {path.relative_to(BASE)}")

    print(f"  DIR  {AGENT_LOGS.relative_to(BASE)}")
    print("Done.")


if __name__ == "__main__":
    main()
