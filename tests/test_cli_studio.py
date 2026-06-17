"""Tests for Studio CLI commands."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

import pytest

VULCA = [sys.executable, "-m", "vulca.cli"]
ROOT = Path(__file__).resolve().parent.parent
CLI_ENV = dict(
    os.environ,
    PYTHONPATH=str(ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
)


def test_cli_brief_create(tmp_path):
    result = subprocess.run(
        VULCA + ["brief", str(tmp_path), "--intent", "水墨山水"],
        capture_output=True,
        text=True,
        timeout=15,
        env=CLI_ENV,
    )
    assert result.returncode == 0
    assert "Brief created" in result.stdout or "brief.yaml" in result.stdout
    assert (tmp_path / "brief.yaml").exists()


def test_cli_brief_update(tmp_path):
    from vulca.studio.brief import Brief

    b = Brief.new("test")
    b.save(tmp_path)

    result = subprocess.run(
        VULCA + ["brief-update", str(tmp_path), "加入霓虹效果"],
        capture_output=True,
        text=True,
        timeout=15,
        env=CLI_ENV,
    )
    assert result.returncode == 0


def test_cli_concept(tmp_path):
    from vulca.studio.brief import Brief

    b = Brief.new("test concept")
    b.save(tmp_path)

    result = subprocess.run(
        VULCA + ["concept", str(tmp_path), "--count", "2", "--provider", "mock"],
        capture_output=True,
        text=True,
        timeout=15,
        env=CLI_ENV,
    )
    assert result.returncode == 0
    assert "concept" in result.stdout.lower()


def test_cli_brief_show(tmp_path):
    from vulca.studio.brief import Brief

    b = Brief.new("test show", mood="serene")
    b.save(tmp_path)

    result = subprocess.run(
        VULCA + ["brief", str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=15,
        env=CLI_ENV,
    )
    assert result.returncode == 0
    assert "test show" in result.stdout
