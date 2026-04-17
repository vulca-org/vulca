"""In-process orchestrated segmentation pipeline.

Typed replacement for scripts/claude_orchestrated_pipeline.py. Designed for
import by MCP tools, tests, and other callers without subprocess overhead.

Main entrypoint: `run(plan: Plan | dict, image_path: str | Path, output_dir: str | Path) -> PipelineResult`
"""
from __future__ import annotations

from vulca.pipeline.segment.plan import Plan, PlanEntity, DEFAULT_PLAN_VERSION
from vulca.pipeline.segment.context import PipelineContext, PipelineResult, DetectionRecord
from vulca.pipeline.segment.orchestrator import run

__all__ = [
    "Plan", "PlanEntity", "DEFAULT_PLAN_VERSION",
    "PipelineContext", "PipelineResult", "DetectionRecord",
    "run",
]
