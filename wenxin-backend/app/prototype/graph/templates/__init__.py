"""Composable graph template system for VULCA pipeline variants."""

from app.prototype.graph.templates.node_spec import NodeSpec
from app.prototype.graph.templates.template_model import ConditionalEdge, GraphTemplate
from app.prototype.graph.templates.template_registry import TemplateRegistry

__all__ = ["ConditionalEdge", "GraphTemplate", "NodeSpec", "TemplateRegistry"]
