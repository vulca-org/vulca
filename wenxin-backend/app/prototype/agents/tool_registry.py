"""Tool Registry — defines callable tools for Critic Agents.

Each tool has a JSON schema (for LLM function calling) and an executor
that performs the actual operation using existing services.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)

__all__ = [
    "CHECK_CULTURAL_SENSITIVITY_SCHEMA",
    "LOOKUP_TERMINOLOGY_SCHEMA",
    "READ_LAYER_ANALYSIS_SCHEMA",
    "SEARCH_CULTURAL_REFERENCES_SCHEMA",
    "SUBMIT_EVALUATION_SCHEMA",
    "ToolDef",
    "ToolRegistry",
    "build_critic_tool_registry",
]


@dataclass
class ToolDef:
    """A single tool definition: schema (for LLM) + executor (for runtime)."""

    name: str
    description: str
    parameters: dict[str, Any]
    executor: Callable[..., Coroutine[Any, Any, Any]] | Callable[..., Any]

    def to_openai_schema(self) -> dict:
        """Return OpenAI-compatible function tool schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    """Registry of available tools for Agent runtime."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDef] = {}

    def register(self, tool: ToolDef) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDef | None:
        return self._tools.get(name)

    def all_schemas(self) -> list[dict]:
        """Return all tool schemas for LLM function calling."""
        return [t.to_openai_schema() for t in self._tools.values()]

    def tool_names(self) -> list[str]:
        return list(self._tools.keys())

    async def execute(self, name: str, arguments: dict) -> Any:
        """Execute a tool by name with the given arguments."""
        tool = self._tools.get(name)
        if tool is None:
            logger.warning("Tool not found: %s (available: %s)", name, list(self._tools.keys()))
            return {"error": f"Unknown tool: {name}"}
        try:
            import asyncio
            if asyncio.iscoroutinefunction(tool.executor):
                result = await tool.executor(**arguments)
            else:
                result = tool.executor(**arguments)
            logger.debug("Tool %s executed successfully (args=%s)", name, list(arguments.keys()))
            return result
        except Exception as exc:  # noqa: BLE001
            logger.error("Tool %s execution failed: %s", name, exc, exc_info=True)
            return {"error": f"Tool execution failed: {exc}"}


# ---------------------------------------------------------------------------
# Critic tool definitions (schemas only — executors bound at runtime)
# ---------------------------------------------------------------------------

SEARCH_CULTURAL_REFERENCES_SCHEMA: dict = {
    "type": "object",
    "required": ["query", "tradition"],
    "properties": {
        "query": {
            "type": "string",
            "description": "Search query for cultural reference works.",
        },
        "tradition": {
            "type": "string",
            "description": "Cultural tradition to search within.",
        },
        "top_k": {
            "type": "integer",
            "default": 5,
            "description": "Number of results to return.",
        },
    },
}

LOOKUP_TERMINOLOGY_SCHEMA: dict = {
    "type": "object",
    "required": ["term", "tradition"],
    "properties": {
        "term": {
            "type": "string",
            "description": "Cultural terminology term to look up.",
        },
        "tradition": {
            "type": "string",
            "description": "Cultural tradition context.",
        },
    },
}

CHECK_CULTURAL_SENSITIVITY_SCHEMA: dict = {
    "type": "object",
    "required": ["text", "tradition"],
    "properties": {
        "text": {
            "type": "string",
            "description": "Text to check for cultural sensitivity violations.",
        },
        "tradition": {
            "type": "string",
            "description": "Cultural tradition context.",
        },
    },
}

READ_LAYER_ANALYSIS_SCHEMA: dict = {
    "type": "object",
    "required": ["layer"],
    "properties": {
        "layer": {
            "type": "string",
            "enum": ["L1", "L2", "L3", "L4", "L5"],
            "description": "Layer whose prior analysis to retrieve.",
        },
    },
}

SUBMIT_EVALUATION_SCHEMA: dict = {
    "type": "object",
    "required": ["score", "confidence", "rationale", "evidence_refs"],
    "properties": {
        "score": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Layer score [0, 1].",
        },
        "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Assessment confidence [0, 1].",
        },
        "rationale": {
            "type": "string",
            "description": "Explanation of the score with evidence citations.",
        },
        "evidence_refs": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["source_id", "contribution"],
                "properties": {
                    "source_id": {"type": "string"},
                    "contribution": {"type": "string"},
                },
            },
            "description": "Evidence references supporting the evaluation.",
        },
    },
}


# ---------------------------------------------------------------------------
# Factory: build the Critic tool registry with bound executors
# ---------------------------------------------------------------------------

def build_critic_tool_registry(
    scout_service: Any = None,
    layer_results: dict[str, dict] | None = None,
    layer_states: dict | None = None,
) -> ToolRegistry:
    """Create a ToolRegistry with Critic tools bound to real services.

    Parameters
    ----------
    scout_service : ScoutService or compatible
        Service providing search_cultural_references, lookup_terminology,
        and check_cultural_sensitivity.
    layer_results : dict
        Previously computed layer analysis results keyed by layer ID.
    layer_states : dict
        L1-L5 LayerState objects (for read_layer_analysis with analysis_text).
    """
    registry = ToolRegistry()
    _layer_results = layer_results or {}
    _layer_states = layer_states or {}

    # --- search_cultural_references ---
    def _search_cultural_references(
        query: str, tradition: str, top_k: int = 5,
    ) -> dict:
        if scout_service is None:
            return {"matches": [], "note": "scout_service not available"}
        evidence = scout_service.gather_evidence(
            subject=query, cultural_tradition=tradition,
        )
        matches = evidence.to_dict().get("sample_matches", [])[:top_k]
        return {"matches": matches, "query": query, "tradition": tradition}

    registry.register(ToolDef(
        name="search_cultural_references",
        description=(
            "Search FAISS/sample index for cultural reference works "
            "matching a query within a tradition. Returns similarity-ranked matches."
        ),
        parameters=SEARCH_CULTURAL_REFERENCES_SCHEMA,
        executor=_search_cultural_references,
    ))

    # --- lookup_terminology ---
    def _lookup_terminology(term: str, tradition: str) -> dict:
        if scout_service is None:
            return {"term": term, "matched": False, "note": "scout_service not available"}
        evidence = scout_service.gather_evidence(
            subject=term, cultural_tradition=tradition,
        )
        hits = evidence.to_dict().get("terminology_hits", [])
        for hit in hits:
            if hit.get("term", "").lower() == term.lower():
                return hit
        return {"term": term, "matched": False, "tradition": tradition}

    registry.register(ToolDef(
        name="lookup_terminology",
        description=(
            "Look up a cultural terminology term in the VULCA terminology "
            "dictionaries. Returns definition, confidence, and layer relevance."
        ),
        parameters=LOOKUP_TERMINOLOGY_SCHEMA,
        executor=_lookup_terminology,
    ))

    # --- check_cultural_sensitivity ---
    def _check_cultural_sensitivity(text: str, tradition: str) -> dict:
        if scout_service is None:
            return {"violations": [], "note": "scout_service not available"}
        evidence = scout_service.gather_evidence(
            subject=text, cultural_tradition=tradition,
        )
        violations = evidence.to_dict().get("taboo_violations", [])
        return {"violations": violations, "text_length": len(text)}

    registry.register(ToolDef(
        name="check_cultural_sensitivity",
        description=(
            "Check text for cultural taboo violations or sensitivity issues. "
            "Returns violation details and severity levels."
        ),
        parameters=CHECK_CULTURAL_SENSITIVITY_SCHEMA,
        executor=_check_cultural_sensitivity,
    ))

    # --- read_layer_analysis ---
    _LAYER_MAP = {"L1": "visual_perception", "L2": "technical_analysis",
                  "L3": "cultural_context", "L4": "critical_interpretation",
                  "L5": "philosophical_aesthetic"}

    def _read_layer_analysis(layer: str) -> dict:
        dim_id = _LAYER_MAP.get(layer, layer)
        # First try LayerState.analysis_text (set by progressive deepening)
        ls = _layer_states.get(dim_id)
        if ls and hasattr(ls, "analysis_text") and ls.analysis_text:
            return {
                "layer": layer,
                "status": "completed",
                "score": round(ls.score, 4),
                "confidence": round(ls.confidence, 4),
                "analysis_text": ls.analysis_text[:500],
            }
        # Fallback to layer_results dict
        result = _layer_results.get(dim_id)
        if result is not None:
            return {"layer": layer, "status": "completed", "analysis": result}
        return {
            "layer": layer,
            "status": "not_yet_evaluated",
            "hint": (
                "No prior analysis available for this layer. "
                "Use search_cultural_references or lookup_terminology instead, "
                "then call submit_evaluation with your assessment."
            ),
        }

    registry.register(ToolDef(
        name="read_layer_analysis",
        description=(
            "Read the analysis results from a previously evaluated layer (L1-L5). "
            "Used for cross-layer reasoning — e.g., L3 reads L1/L2 findings."
        ),
        parameters=READ_LAYER_ANALYSIS_SCHEMA,
        executor=_read_layer_analysis,
    ))

    # --- submit_evaluation ---
    # This is a "terminal" tool — when the Agent calls it, the loop ends.
    def _submit_evaluation(
        score: float, confidence: float, rationale: str,
        evidence_refs: list[dict],
    ) -> dict:
        return {
            "status": "submitted",
            "score": score,
            "confidence": confidence,
            "rationale": rationale,
            "evidence_refs": evidence_refs,
        }

    registry.register(ToolDef(
        name="submit_evaluation",
        description=(
            "Submit the final evaluation for this layer. Must include score, "
            "confidence, rationale, and evidence references. Calling this "
            "tool ends the evaluation loop."
        ),
        parameters=SUBMIT_EVALUATION_SCHEMA,
        executor=_submit_evaluation,
    ))

    return registry
