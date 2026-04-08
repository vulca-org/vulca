import asyncio

import pytest

pytest.importorskip("fastmcp")

from vulca.mcp_server import vulca_layered_create, vulca_layers_retry  # noqa: E402


def test_layered_create_runs_with_mock(tmp_path):
    out = asyncio.run(vulca_layered_create(
        intent="远山薄雾",
        tradition="chinese_xieyi",
        provider="mock",
        output_dir=str(tmp_path),
    ))
    # With mock provider every layer fails provider decoding, but the pipeline
    # still completes and CompositeNode writes manifest.json.
    assert isinstance(out, dict)
    assert (tmp_path / "manifest.json").exists()


def test_layers_retry_handles_missing_dir():
    out = asyncio.run(vulca_layers_retry(artifact_dir=""))
    assert out.get("error")

    out = asyncio.run(vulca_layers_retry(artifact_dir="/nonexistent/path/xyz"))
    assert out.get("error")
