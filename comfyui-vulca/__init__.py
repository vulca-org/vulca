"""VULCA custom nodes for ComfyUI.

Install: Copy this directory to ComfyUI/custom_nodes/comfyui-vulca/
Requires: pip install vulca
"""
try:
    from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
except ImportError:
    # Fallback for direct execution / testing outside a package context
    from nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS  # type: ignore[no-redef]

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

WEB_DIRECTORY = None
