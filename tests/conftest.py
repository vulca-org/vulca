"""Shared test fixtures for VULCA test suite."""

from __future__ import annotations

import os
import sys

import pytest

# Ensure vulca package is importable from src/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
