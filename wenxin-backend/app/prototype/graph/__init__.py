"""LangGraph-based pipeline execution engine (**experimental**).

Orchestrator Architecture Decision (Route B+, 2026-03-10):
Status: EXPERIMENTAL — not used in production API routes by default.
Production orchestrator: app.prototype.orchestrator.PipelineOrchestrator

This package provides a composable, graph-based alternative to the
monolithic PipelineOrchestrator, with native support for multi-stage
HITL interrupts and configurable pipeline topologies (templates).

Activation: Set use_graph=True in POST /api/v1/prototype/runs to route
through GraphOrchestrator instead of PipelineOrchestrator.

If migrating to GraphOrchestrator as the production default:
1. Update app/prototype/api/create_routes.py to use GraphOrchestrator
2. Update app/prototype/api/routes.py default use_graph to True
3. Add comprehensive test coverage (currently zero test cases)
4. Verify SSE streaming event compatibility
"""
