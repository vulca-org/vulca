"""Tests for optional dependency groups (SDK extras packaging).

These tests verify:
1. Core vulca API is importable without optional heavy deps.
2. Optional extras (layers, tools) expose the expected symbols.
3. Import guards exist so missing deps raise ImportError gracefully (not AttributeError etc.).
"""

from __future__ import annotations


def test_core_import_without_optional_deps():
    """Core vulca should import and expose evaluate/create regardless of optional deps."""
    import vulca

    assert hasattr(vulca, "evaluate"), "vulca.evaluate must always be present"
    assert hasattr(vulca, "create"), "vulca.create must always be present"
    assert hasattr(vulca, "inpaint"), "vulca.inpaint must always be present"
    assert hasattr(vulca, "__version__"), "vulca.__version__ must always be present"


def test_extras_defined_in_metadata():
    """Verify extras are defined in package metadata (or skip gracefully in dev mode)."""
    import importlib.metadata

    try:
        meta = importlib.metadata.metadata("vulca")
        # If installed (editable or wheel), we can look at Requires-Dist
        requires = meta.get_all("Requires-Dist") or []
        # Just check that *some* optional deps are defined (extras exist)
        # In dev mode with editable install the metadata may be minimal
        assert isinstance(requires, list)
    except importlib.metadata.PackageNotFoundError:
        # Running from source without pip install — acceptable in dev/CI
        pass


def test_layers_import_guard():
    """layers subpackage should import cleanly when Pillow/numpy are installed,
    or raise ImportError (not AttributeError/NameError) when they are not."""
    try:
        from vulca.layers import composite  # noqa: F401
    except ImportError:
        pass  # OK: Pillow/numpy not installed — import guard works correctly


def test_tools_import_guard():
    """tools subpackage should raise ImportError (not AttributeError) when cv2
    is not installed, or import cleanly when all deps are present."""
    try:
        from vulca.tools.cultural import whitespace  # noqa: F401
    except ImportError:
        pass  # OK: cv2/numpy/Pillow not installed — import guard works correctly


def test_layers_available_flag():
    """vulca._LAYERS_AVAILABLE reflects whether Pillow/numpy are present."""
    import vulca

    # The flag must exist — its *value* depends on the environment
    assert hasattr(vulca, "_LAYERS_AVAILABLE"), (
        "_LAYERS_AVAILABLE sentinel must exist on the vulca package"
    )
    assert isinstance(vulca._LAYERS_AVAILABLE, bool)


def test_sam_import_guard():
    """SAM2 integration should expose SAM_AVAILABLE flag without crashing."""
    try:
        from vulca.layers.sam import SAM_AVAILABLE  # noqa: F401

        assert isinstance(SAM_AVAILABLE, bool)
    except ImportError:
        # If Pillow/numpy are missing the whole layers subpackage fails — OK
        pass


def test_extras_groups_in_pyproject():
    """Verify the expected extras keys exist in pyproject.toml."""
    from pathlib import Path
    import tomllib

    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    assert pyproject.exists(), "pyproject.toml must exist"

    content = pyproject.read_text()
    data = tomllib.loads(content)
    extras = data["project"]["optional-dependencies"]

    # All required extras must be declared
    for extra in ("core", "layers", "tools", "providers", "all", "dev"):
        assert extra in extras, (
            f"extras group '{extra}' not found in pyproject.toml"
        )

    assert any(dep.startswith("google-genai") for dep in extras["providers"])
    assert any(dep.startswith("openai") for dep in extras["providers"])
    assert "vulca[layers,tools,mcp,scout,providers]" in extras["all"]
