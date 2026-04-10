"""Shared test fixtures for VULCA test suite."""

from __future__ import annotations

import os
import sys

import pytest

# Ensure vulca package is importable from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def pytest_addoption(parser):
    parser.addoption(
        "--run-real-provider",
        action="store_true",
        default=False,
        help="Run tests marked real_provider (hits live APIs, requires credentials)",
    )
    parser.addoption(
        "--run-local-provider",
        action="store_true",
        default=False,
        help="Run tests marked local_provider (requires local ComfyUI + Ollama)",
    )


def pytest_configure(config):
    config.addinivalue_line("markers",
                            "real_provider: test that hits a real image provider")
    config.addinivalue_line("markers",
                            "local_provider: test that requires local ComfyUI + Ollama")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-real-provider"):
        skip_real = pytest.mark.skip(reason="needs --run-real-provider")
        for item in items:
            if "real_provider" in item.keywords:
                item.add_marker(skip_real)
    if not config.getoption("--run-local-provider"):
        skip_local = pytest.mark.skip(reason="needs --run-local-provider")
        for item in items:
            if "local_provider" in item.keywords:
                item.add_marker(skip_local)
