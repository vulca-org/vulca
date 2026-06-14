from __future__ import annotations

import os
import subprocess
import sys
from types import SimpleNamespace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VULCA = [sys.executable, "-m", "vulca"]


def test_default_telemetry_is_noop(monkeypatch, tmp_path):
    monkeypatch.delenv("VULCA_TELEMETRY", raising=False)
    monkeypatch.delenv("DO_NOT_TRACK", raising=False)
    monkeypatch.setenv("VULCA_CONFIG_DIR", str(tmp_path / "config"))
    sent = []

    from vulca.telemetry import TelemetryClient

    client = TelemetryClient(interface="sdk", sink=sent.append)

    assert client.enabled is False
    assert client.emit(
        "cli_invoked",
        {
            "command": "evaluate",
            "prompt": "secret prompt",
            "image_path": "/Users/me/private/art.png",
        },
    ) is False
    assert sent == []


def test_opt_in_telemetry_scrubs_sensitive_payload(monkeypatch, tmp_path):
    monkeypatch.setenv("VULCA_TELEMETRY", "1")
    monkeypatch.delenv("DO_NOT_TRACK", raising=False)
    monkeypatch.setenv("VULCA_CONFIG_DIR", str(tmp_path / "config"))
    sent = []

    from vulca.telemetry import TelemetryClient

    client = TelemetryClient(interface="mcp", sink=sent.append)

    assert client.emit(
        "mcp_tool_called",
        {
            "tool_name": "layers_split",
            "status": "ok",
            "duration_bucket_ms": "100-500",
            "provider": "mock",
            "prompt": "do not send",
            "image_path": "/tmp/private.png",
            "api_key": "secret",
        },
    ) is True

    assert len(sent) == 1
    payload = sent[0]
    assert payload["event"] == "mcp_tool_called"
    assert payload["interface"] == "mcp"
    assert payload["anonymous_install_id"]
    assert payload["properties"] == {
        "tool_name": "layers_split",
        "status": "ok",
        "duration_bucket_ms": "100-500",
        "provider": "mock",
    }


def test_do_not_track_disables_even_when_opted_in(monkeypatch, tmp_path):
    monkeypatch.setenv("VULCA_TELEMETRY", "1")
    monkeypatch.setenv("DO_NOT_TRACK", "1")
    monkeypatch.setenv("VULCA_CONFIG_DIR", str(tmp_path / "config"))
    sent = []

    from vulca.telemetry import TelemetryClient

    client = TelemetryClient(interface="sdk", sink=sent.append)

    assert client.enabled is False
    assert client.emit("cli_invoked", {"command": "create"}) is False
    assert sent == []


def test_sink_failure_is_silent(monkeypatch, tmp_path):
    monkeypatch.setenv("VULCA_TELEMETRY", "1")
    monkeypatch.delenv("DO_NOT_TRACK", raising=False)
    monkeypatch.setenv("VULCA_CONFIG_DIR", str(tmp_path / "config"))

    from vulca.telemetry import TelemetryClient

    def broken_sink(payload):
        raise RuntimeError("network down")

    client = TelemetryClient(interface="sdk", sink=broken_sink)

    assert client.emit("provider_generate_called", {"provider": "mock"}) is False


def test_mcp_telemetry_middleware_emits_tool_status(monkeypatch, tmp_path):
    monkeypatch.setenv("VULCA_TELEMETRY", "1")
    monkeypatch.delenv("DO_NOT_TRACK", raising=False)
    monkeypatch.setenv("VULCA_CONFIG_DIR", str(tmp_path / "config"))
    sent = []

    from vulca.telemetry import McpTelemetryMiddleware, TelemetryClient

    middleware = McpTelemetryMiddleware(
        client=TelemetryClient(interface="mcp", sink=sent.append)
    )
    context = SimpleNamespace(
        message=SimpleNamespace(
            name="layers_split",
            arguments={"image_path": "/tmp/private.png", "prompt": "secret"},
        )
    )

    async def call_next(_context):
        return {"status": "ok"}

    import asyncio

    assert asyncio.run(middleware.on_call_tool(context, call_next)) == {"status": "ok"}
    assert sent[0]["properties"]["tool_name"] == "layers_split"
    assert sent[0]["properties"]["status"] == "ok"
    assert "image_path" not in sent[0]["properties"]
    assert "prompt" not in sent[0]["properties"]


def test_cli_telemetry_status_enable_disable(tmp_path):
    env = {
        **os.environ,
        "PYTHONPATH": str(ROOT / "src"),
        "VULCA_CONFIG_DIR": str(tmp_path / "config"),
    }
    env.pop("VULCA_TELEMETRY", None)
    env.pop("DO_NOT_TRACK", None)

    status = subprocess.run(
        VULCA + ["telemetry", "status"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert status.returncode == 0
    assert "enabled: false" in status.stdout
    assert "default-off" in status.stdout

    enabled = subprocess.run(
        VULCA + ["telemetry", "enable"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert enabled.returncode == 0
    assert "enabled: true" in enabled.stdout

    disabled = subprocess.run(
        VULCA + ["telemetry", "disable"],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert disabled.returncode == 0
    assert "enabled: false" in disabled.stdout


def test_telemetry_policy_doc_names_default_off_and_forbidden_fields():
    policy = (ROOT / "docs" / "platform" / "telemetry-policy.md").read_text(
        encoding="utf-8"
    )

    assert "off by default" in policy.lower()
    assert "DO_NOT_TRACK=1" in policy
    assert "prompts" in policy
    assert "image paths" in policy
    assert "image bytes" in policy
    assert "API keys" in policy
    assert "mcp_tool_called" in policy
