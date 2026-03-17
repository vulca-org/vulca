"""CLI tests -- run vulca CLI via subprocess to validate entry point."""

from __future__ import annotations

import subprocess
import sys

import pytest


def _run_cli(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Helper to invoke the vulca CLI via ``python -m vulca``."""
    return subprocess.run(
        [sys.executable, "-m", "vulca", *args],
        capture_output=True,
        text=True,
        timeout=15,
        check=check,
    )


# -- Help Output -----------------------------------------------------------


def test_cli_help():
    """``vulca --help`` exits 0 and prints usage info."""
    result = _run_cli("--help")
    assert result.returncode == 0
    assert "vulca" in result.stdout.lower()
    assert "evaluate" in result.stdout.lower() or "usage" in result.stdout.lower()


def test_cli_evaluate_help():
    """``vulca evaluate --help`` prints evaluate-specific options."""
    result = _run_cli("evaluate", "--help")
    assert result.returncode == 0
    assert "--intent" in result.stdout or "-i" in result.stdout
    assert "--tradition" in result.stdout or "-t" in result.stdout
    assert "image" in result.stdout.lower()


def test_cli_create_help():
    """``vulca create --help`` prints create-specific options."""
    result = _run_cli("create", "--help")
    assert result.returncode == 0
    assert "--tradition" in result.stdout or "-t" in result.stdout
    assert "intent" in result.stdout.lower()


def test_cli_traditions_help():
    """``vulca traditions --help`` prints traditions help."""
    result = _run_cli("traditions", "--help")
    assert result.returncode == 0


# -- Version ---------------------------------------------------------------


def test_cli_version():
    """``vulca --version`` prints the version string."""
    result = _run_cli("--version")
    assert result.returncode == 0
    assert "0.2.0" in result.stdout


# -- Traditions Command ----------------------------------------------------


def test_cli_traditions_output():
    """``vulca traditions`` lists all 9 traditions."""
    result = _run_cli("traditions")
    assert result.returncode == 0
    assert "chinese_xieyi" in result.stdout
    assert "western_academic" in result.stdout
    assert "islamic_geometric" in result.stdout
    assert "japanese_traditional" in result.stdout


# -- No-command Shows Help -------------------------------------------------


def test_cli_no_args():
    """Running vulca with no arguments shows help and exits with code 1."""
    result = _run_cli(check=False)
    # Should exit 1 (no command given) and print help to stdout
    assert result.returncode == 1
    assert "vulca" in result.stdout.lower() or "usage" in result.stdout.lower()


# -- Module Entry Point ----------------------------------------------------


def test_module_entry_point():
    """``python -m vulca --version`` works as module entry point."""
    result = subprocess.run(
        [sys.executable, "-m", "vulca", "--version"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0
    assert "vulca" in result.stdout.lower()


# -- Evaluate Without Image ------------------------------------------------


def test_cli_evaluate_missing_image():
    """``vulca evaluate`` without image argument should fail."""
    result = _run_cli("evaluate", check=False)
    assert result.returncode != 0
