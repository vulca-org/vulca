"""Tests for Studio CLI commands."""
from __future__ import annotations

import pytest
from click.testing import CliRunner


def test_cli_brief_create(tmp_path):
    from vulca.cli import cli
    runner = CliRunner()
    result = runner.invoke(cli, ["brief", str(tmp_path), "--intent", "水墨山水"])
    assert result.exit_code == 0
    assert "Brief created" in result.output or "brief.yaml" in result.output
    assert (tmp_path / "brief.yaml").exists()


def test_cli_brief_update(tmp_path):
    from vulca.cli import cli
    from vulca.studio.brief import Brief
    b = Brief.new("test")
    b.save(tmp_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["brief-update", str(tmp_path), "加入霓虹效果"])
    assert result.exit_code == 0


def test_cli_concept(tmp_path):
    from vulca.cli import cli
    from vulca.studio.brief import Brief
    b = Brief.new("test concept")
    b.save(tmp_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["concept", str(tmp_path), "--count", "2", "--mock"])
    assert result.exit_code == 0
    assert "concept" in result.output.lower()


def test_cli_brief_show(tmp_path):
    from vulca.cli import cli
    from vulca.studio.brief import Brief
    b = Brief.new("test show", mood="serene")
    b.save(tmp_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["brief", str(tmp_path)])
    assert result.exit_code == 0
    assert "test show" in result.output
