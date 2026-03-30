"""SDK adapter for the VULCA Tool Protocol.

Wraps VulcaTool subclasses into plain Python functions:

    from vulca.tools import whitespace_analyze
    result = whitespace_analyze("art.png", tradition="chinese_xieyi")

    from vulca.tools import list_tools
    tools = list_tools()  # -> list of metadata dicts

Functions created by ``make_sdk_function`` accept *image* as:
  - str: interpreted as a file path
  - bytes: raw image bytes (PNG/JPEG/etc.)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Type

if TYPE_CHECKING:
    from vulca.tools.protocol import VulcaTool
    from vulca.tools.registry import ToolRegistry


def make_sdk_function(tool_cls: "Type[VulcaTool]") -> Callable:
    """Create a plain Python function that wraps *tool_cls*.

    The returned function has this effective signature::

        def <tool_name>(image, tradition="", mode="check", **kwargs) -> Output

    Parameters
    ----------
    tool_cls:
        A concrete VulcaTool subclass (not an instance).

    Returns
    -------
    callable
        A function named after ``tool_cls.name`` that instantiates the tool,
        builds Input, calls safe_execute, and returns the Output.
    """
    from vulca.tools.protocol import ToolConfig

    tool_name = tool_cls.name

    def _sdk_fn(
        image: "str | bytes",
        tradition: str = "",
        mode: str = "check",
        **kwargs: Any,
    ) -> Any:
        """Auto-generated SDK wrapper for the VULCA tool: {tool_name}.

        Parameters
        ----------
        image:
            File path (str) or raw PNG/JPEG bytes.
        tradition:
            Cultural tradition name (e.g. "chinese_xieyi").  Optional.
        mode:
            Tool execution mode: "check" (default), "fix", or "suggest".
        **kwargs:
            Extra ToolConfig.params entries (passed as ``params`` dict).
        """
        # --- Resolve image bytes ---
        if isinstance(image, (bytes, bytearray)):
            image_bytes = bytes(image)
        elif isinstance(image, str):
            with open(image, "rb") as fh:
                image_bytes = fh.read()
        else:
            raise TypeError(
                f"image must be a file path (str) or bytes, got {type(image).__name__}"
            )

        # --- Build config ---
        config = ToolConfig(
            mode=mode,  # type: ignore[arg-type]
            params=kwargs,
        )

        # --- Instantiate and execute ---
        tool_instance = tool_cls()
        input_data = tool_instance.Input(image=image_bytes, tradition=tradition)
        return tool_instance.safe_execute(input_data, config)

    # Give the wrapper a useful __name__ and __doc__
    _sdk_fn.__name__ = tool_name
    _sdk_fn.__qualname__ = tool_name
    _sdk_fn.__doc__ = (
        f"VULCA tool: {tool_cls.display_name}\n\n"
        f"{tool_cls.description}\n\n"
        f"Parameters\n----------\n"
        f"image : str | bytes\n"
        f"    File path or raw bytes.\n"
        f"tradition : str\n"
        f"    Cultural tradition name (optional).\n"
        f"mode : str\n"
        f"    'check' (default), 'fix', or 'suggest'.\n"
    )

    return _sdk_fn


def list_tools() -> "list[dict[str, Any]]":
    """Return metadata for all auto-discovered VULCA tools.

    Returns
    -------
    list[dict]
        Each dict contains: name, display_name, description, category,
        max_seconds, replaces.
    """
    from vulca.tools.registry import ToolRegistry

    reg = ToolRegistry()
    reg.discover()

    return [
        {
            "name": t.name,
            "display_name": t.display_name,
            "description": t.description,
            "category": t.category.value,
            "max_seconds": t.max_seconds,
            "replaces": t.__class__.replaces,
        }
        for t in reg.list_all()
    ]
