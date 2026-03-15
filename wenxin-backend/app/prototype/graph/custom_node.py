"""Custom node base class and registration decorator.

Provides BaseCustomNode — an extended BaseAgent with declarative
input_ports / output_ports that auto-register in both AgentRegistry
and the port contract system.

Usage::

    @register_custom_node("style_transfer", category="processing")
    class StyleTransferNode(BaseCustomNode):
        input_ports = [PortSpec("image_in", DataType.IMAGE, PortDirection.INPUT)]
        output_ports = [PortSpec("image_out", DataType.IMAGE, PortDirection.OUTPUT)]

        def execute(self, state):
            ...
"""

from __future__ import annotations

import logging
from typing import Any

from app.prototype.graph.base_agent import BaseAgent
from app.prototype.graph.registry import AgentRegistry
from app.prototype.pipeline.port_contract import (
    DataType,
    PortDirection,
    PortSpec,
    StageContract,
    register_contract,
)

logger = logging.getLogger(__name__)


class BaseCustomNode(BaseAgent):
    """Extended BaseAgent with declarative port specifications.

    Subclasses declare class-level ``input_ports`` and ``output_ports``
    lists of PortSpec.  The ``@register_custom_node`` decorator
    auto-registers both the agent and its port contract.
    """

    input_ports: list[PortSpec] = []
    output_ports: list[PortSpec] = []
    category: str = "custom"

    def validate_inputs(self, state: dict[str, Any]) -> list[str]:
        """Validate that required inputs are present in state."""
        errors: list[str] = []
        for port in self.input_ports:
            if port.required:
                key = port.name
                if key not in state or state[key] is None:
                    errors.append(f"Missing required input: {key}")
        return errors


def register_custom_node(name: str, category: str = "custom"):
    """Decorator to register a BaseCustomNode subclass.

    Registers in both AgentRegistry and port contract registry.
    """
    def decorator(cls: type[BaseCustomNode]):
        cls.name = name
        cls.category = category

        # Register in AgentRegistry
        AgentRegistry._agents[name] = cls

        # Register port contract
        contract = StageContract(
            stage_name=name,
            input_ports=list(cls.input_ports),
            output_ports=list(cls.output_ports),
            description=cls.description or f"Custom {category} node: {name}",
        )
        register_contract(contract)

        logger.debug("Registered custom node '%s' (category=%s)", name, category)
        return cls

    return decorator
