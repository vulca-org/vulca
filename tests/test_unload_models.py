"""Unit test for unload_models MCP tool."""
import asyncio
from unittest.mock import MagicMock


def test_unload_models_calls_all_four_cache_clears(monkeypatch):
    """Mock the 4 loaders, call unload_models, assert all cache_clears fired."""
    from vulca.pipeline.segment.orchestrator import _import_cop
    from vulca import mcp_server

    cop = _import_cop()

    # Build a mock for each loader's cache_clear
    mock_cc = {
        "load_grounding_dino": MagicMock(),
        "load_yolo": MagicMock(),
        "load_face_parser": MagicMock(),
        "_load_sam_model": MagicMock(),
    }
    for name, mock in mock_cc.items():
        loader = getattr(cop, name)
        monkeypatch.setattr(loader, "cache_clear", mock)

    result = asyncio.run(mcp_server.unload_models())

    assert result.get("status") == "ok", result
    assert result.get("cleared") == 4, result
    for name, mock in mock_cc.items():
        mock.assert_called_once(), f"{name}.cache_clear not invoked"


def test_unload_models_survives_torch_missing(monkeypatch):
    """If torch import fails inside unload_models, 4 clears still complete.

    Uses sys.modules[name] = None trick: Python treats None in sys.modules
    as 'this module cannot be imported', raising ImportError on re-import.
    This is the standard way to simulate a missing optional dep.
    """
    import sys

    from vulca.pipeline.segment.orchestrator import _import_cop
    from vulca import mcp_server

    cop = _import_cop()
    mocks = {}
    for name in ("load_grounding_dino", "load_yolo",
                 "load_face_parser", "_load_sam_model"):
        m = MagicMock()
        monkeypatch.setattr(getattr(cop, name), "cache_clear", m)
        mocks[name] = m

    # Force torch import to raise ImportError inside unload_models
    monkeypatch.setitem(sys.modules, "torch", None)

    result = asyncio.run(mcp_server.unload_models())

    assert result.get("status") == "ok", result
    assert result.get("cleared") == 4, result
    for name, m in mocks.items():
        m.assert_called_once(), f"{name}.cache_clear not invoked after torch failure"
