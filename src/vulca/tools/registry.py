"""ToolRegistry — auto-discovery and query interface for VULCA tools.

Usage::

    from vulca.tools.registry import ToolRegistry

    registry = ToolRegistry()
    registry.discover()              # auto-scan built-in subpackages

    tool = registry.get("stub_cultural")
    all_tools = registry.list_all()
    cultural = registry.list_by_category(ToolCategory.CULTURAL_CHECK)
    replacements = registry.list_replacements()

The registry holds one instantiated tool per registered class, keyed by
``tool.name``.  Calling ``register()`` twice with the same class (or two
classes that share the same ``name``) silently overwrites the previous entry,
which is intentional — plugins can upgrade built-in tools by re-registering.
"""

from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
from typing import TYPE_CHECKING, Type

from vulca.tools.protocol import ToolCategory, VulcaTool

if TYPE_CHECKING:
    pass

logger = logging.getLogger("vulca.tools.registry")

# Subpackages that discover() scans automatically.
_DISCOVER_PACKAGES = [
    "vulca.tools.cultural",
    "vulca.tools.filters",
]


class ToolRegistry:
    """Registry of instantiated VulcaTool objects, keyed by tool name.

    Methods
    -------
    register(tool_cls)
        Register a VulcaTool subclass.  Instantiates it immediately.
    get(name)
        Return the instantiated tool for *name*; raise KeyError if absent.
    list_all()
        Return a list of all instantiated tools.
    list_by_category(category)
        Return tools whose ``category`` matches *category*.
    list_replacements()
        Return ``{tool_name: replaces_dict}`` for tools with non-empty ``replaces``.
    discover()
        Auto-scan ``vulca.tools.cultural`` and ``vulca.tools.filters``, find
        all concrete VulcaTool subclasses, and register them.
    """

    def __init__(self) -> None:
        # Maps tool.name → instantiated VulcaTool
        self._tools: dict[str, VulcaTool] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, tool_cls: Type[VulcaTool]) -> None:
        """Register *tool_cls* by its ``name`` class variable.

        The class is instantiated once and stored.  Re-registering the same
        name silently replaces the previous entry.

        Parameters
        ----------
        tool_cls:
            A concrete subclass of VulcaTool with a ``name`` class attribute.

        Raises
        ------
        TypeError
            If *tool_cls* is not a subclass of VulcaTool.
        AttributeError
            If *tool_cls* does not define a ``name`` class attribute.
        """
        if not (isinstance(tool_cls, type) and issubclass(tool_cls, VulcaTool)):
            raise TypeError(
                f"tool_cls must be a subclass of VulcaTool, got {tool_cls!r}"
            )
        name: str = tool_cls.name
        instance = tool_cls()
        self._tools[name] = instance
        logger.debug("Registered tool %r (%s)", name, tool_cls.__qualname__)

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, name: str) -> VulcaTool:
        """Return the instantiated tool registered under *name*.

        Raises
        ------
        KeyError
            If no tool with that name has been registered.
        """
        try:
            return self._tools[name]
        except KeyError:
            available = sorted(self._tools.keys())
            raise KeyError(
                f"No tool named {name!r} is registered.  "
                f"Available: {available}"
            ) from None

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def list_all(self) -> list[VulcaTool]:
        """Return a list of all registered tool instances."""
        return list(self._tools.values())

    def list_by_category(self, category: ToolCategory) -> list[VulcaTool]:
        """Return tools whose ``category`` attribute equals *category*.

        Parameters
        ----------
        category:
            A :class:`ToolCategory` enum value to filter by.

        Returns
        -------
        list[VulcaTool]
            Possibly empty list of matching tool instances.
        """
        return [t for t in self._tools.values() if t.category == category]

    def list_replacements(self) -> dict[str, dict[str, list[str]]]:
        """Return replacement metadata for tools with non-empty ``replaces``.

        Returns
        -------
        dict[str, dict[str, list[str]]]
            Mapping of ``{tool_name: replaces_dict}`` where *replaces_dict*
            is the tool's ``replaces`` class variable, e.g.
            ``{"evaluate": ["L1"]}``.  Tools with an empty ``replaces`` dict
            are excluded.
        """
        result: dict[str, dict[str, list[str]]] = {}
        for name, tool in self._tools.items():
            replaces = tool.__class__.replaces
            if replaces:
                result[name] = replaces
        return result

    # ------------------------------------------------------------------
    # Auto-discovery
    # ------------------------------------------------------------------

    def discover(self) -> None:
        """Auto-scan built-in subpackages and register all VulcaTool subclasses.

        Scans the following packages:
        - ``vulca.tools.cultural``
        - ``vulca.tools.filters``

        Concrete (non-abstract) VulcaTool subclasses found in those packages
        are registered automatically.  Abstract classes and VulcaTool itself
        are skipped.

        Safe to call on empty packages — no error is raised if a package
        contains no tool classes.
        """
        for package_name in _DISCOVER_PACKAGES:
            self._scan_package(package_name)

    def _scan_package(self, package_name: str) -> None:
        """Import *package_name* and all its modules, registering VulcaTool subclasses."""
        try:
            package = importlib.import_module(package_name)
        except ImportError as exc:
            logger.debug("Skipping package %r — import failed: %s", package_name, exc)
            return

        # Register any tool classes defined directly in the package __init__
        self._register_from_module(package)

        # Walk all submodules in the package
        package_path = getattr(package, "__path__", None)
        if package_path is None:
            return

        for module_info in pkgutil.iter_modules(package_path):
            full_module_name = f"{package_name}.{module_info.name}"
            try:
                module = importlib.import_module(full_module_name)
            except ImportError as exc:
                logger.warning(
                    "Could not import module %r during discover: %s",
                    full_module_name,
                    exc,
                )
                continue
            self._register_from_module(module)

    def _register_from_module(self, module) -> None:  # type: ignore[type-arg]
        """Find and register all concrete VulcaTool subclasses in *module*."""
        for _attr_name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                obj is not VulcaTool
                and issubclass(obj, VulcaTool)
                and not inspect.isabstract(obj)
                and hasattr(obj, "name")
                # Only register classes actually defined in this module to
                # avoid re-registering re-imported classes.
                and obj.__module__ == module.__name__
            ):
                self.register(obj)
