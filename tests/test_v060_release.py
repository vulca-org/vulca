"""Tests for v0.6.0 release — version, exports, changelog, build."""
from __future__ import annotations

from pathlib import Path
import pytest


def test_version_is_current():
    """Version must match pyproject.toml."""
    from vulca._version import __version__
    assert __version__ == "0.9.1"


def test_pyproject_version_matches():
    """pyproject.toml version must match _version.py."""
    from vulca._version import __version__
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    content = pyproject.read_text()
    assert f'version = "{__version__}"' in content


def test_digestion_exports():
    """Digestion V2 modules must be importable from vulca.digestion."""
    from vulca.digestion import (
        JsonlStudioStorage,
        ArtifactAnalysis,
        SessionPreferences,
        LocalArchiver,
    )
    assert JsonlStudioStorage is not None
    assert ArtifactAnalysis is not None
    assert SessionPreferences is not None
    assert LocalArchiver is not None


def test_digestion_functions_importable():
    """Digestion V2 public functions must be importable."""
    from vulca.digestion import (
        extract_action_signal,
        accumulate_preferences,
        preload_intelligence,
        detect_patterns,
        evolve_weights,
        build_session_digest,
    )
    assert callable(extract_action_signal)
    assert callable(preload_intelligence)
    assert callable(detect_patterns)
    assert callable(build_session_digest)


def test_changelog_exists():
    """CHANGELOG.md must exist in the package root."""
    changelog = Path(__file__).resolve().parent.parent / "CHANGELOG.md"
    assert changelog.exists(), f"CHANGELOG.md not found at {changelog}"


def test_changelog_has_060_entry():
    """CHANGELOG.md must have a v0.6.0 section."""
    changelog = Path(__file__).resolve().parent.parent / "CHANGELOG.md"
    content = changelog.read_text()
    assert "0.6.0" in content
    assert "Digestion" in content or "digestion" in content


def test_description_updated():
    """pyproject.toml description should mention Studio + Digestion."""
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    content = pyproject.read_text()
    assert "Studio" in content or "studio" in content or "Brief" in content
