"""VULCA Tool Protocol — public API for the tools subsystem.

Tools are auto-discovered from:
  - vulca.tools.cultural (e.g. whitespace_analyze)
  - vulca.tools.filters  (e.g. color_correct)

SDK usage::

    from vulca.tools import whitespace_analyze, color_correct, list_tools

    result = whitespace_analyze("art.png", tradition="chinese_xieyi")
    tools  = list_tools()   # -> list of metadata dicts
"""

from vulca.tools.protocol import (
    ImageData,
    ToolCategory,
    ToolConfig,
    ToolSchema,
    VulcaTool,
    VisualEvidence,
)

__all__ = [
    "ImageData",
    "ToolCategory",
    "ToolConfig",
    "ToolSchema",
    "VulcaTool",
    "VisualEvidence",
    "list_tools",
]

# ---------------------------------------------------------------------------
# SDK function injection — auto-discover all tools and inject as module globals
# ---------------------------------------------------------------------------

from vulca.tools.adapters.sdk import list_tools, make_sdk_function  # noqa: E402
from vulca.tools.registry import ToolRegistry  # noqa: E402

_registry = ToolRegistry()
_registry.discover()

for _tool in _registry.list_all():
    _fn = make_sdk_function(type(_tool))
    globals()[_fn.__name__] = _fn
    __all__.append(_fn.__name__)
