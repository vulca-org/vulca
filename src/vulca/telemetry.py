"""Privacy-safe, opt-in telemetry helpers for Vulca runtime surfaces."""

from __future__ import annotations

import json
import os
import platform as platform_mod
import sys
import time
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from vulca._version import __version__

try:
    from fastmcp.server.middleware import Middleware
except Exception:  # pragma: no cover - fastmcp is optional outside MCP installs
    class Middleware:  # type: ignore[no-redef]
        pass


TelemetrySink = Callable[[dict[str, Any]], object]

_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off"}
_ALLOWED_PROPERTY_KEYS = {
    "command",
    "duration_bucket_ms",
    "evaluation_error_present",
    "profile",
    "provider",
    "status",
    "step",
    "tool_name",
    "transport",
    "usage_present",
}
_CONFIG_FILE = "telemetry.json"
_INSTALL_ID_FILE = "anonymous_install_id"


def _config_dir() -> Path:
    raw = os.environ.get("VULCA_CONFIG_DIR")
    if raw:
        return Path(raw).expanduser()
    return Path.home() / ".config" / "vulca"


def _config_path() -> Path:
    return _config_dir() / _CONFIG_FILE


def _install_id_path() -> Path:
    return _config_dir() / _INSTALL_ID_FILE


def _env_bool(name: str) -> bool | None:
    raw = os.environ.get(name)
    if raw is None:
        return None
    value = raw.strip().lower()
    if value in _TRUE:
        return True
    if value in _FALSE:
        return False
    return None


def _load_config() -> dict[str, Any]:
    path = _config_path()
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_config(payload: dict[str, Any]) -> None:
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def set_telemetry_enabled(enabled: bool) -> None:
    config = _load_config()
    config["enabled"] = bool(enabled)
    _write_config(config)


def reset_anonymous_install_id() -> None:
    try:
        _install_id_path().unlink()
    except FileNotFoundError:
        pass


def _enabled_state() -> tuple[bool, str]:
    if _env_bool("DO_NOT_TRACK") is True:
        return False, "do-not-track"
    env_value = _env_bool("VULCA_TELEMETRY")
    if env_value is not None:
        return env_value, "env"
    config = _load_config()
    if isinstance(config.get("enabled"), bool):
        return bool(config["enabled"]), "config"
    return False, "default-off"


def _current_install_id(*, create: bool) -> str:
    path = _install_id_path()
    if path.exists():
        try:
            return path.read_text(encoding="utf-8").strip()
        except OSError:
            return ""
    if not create:
        return ""
    value = uuid.uuid4().hex
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value + "\n", encoding="utf-8")
    return value


def telemetry_status() -> dict[str, Any]:
    enabled, source = _enabled_state()
    return {
        "enabled": enabled,
        "source": source,
        "do_not_track": _env_bool("DO_NOT_TRACK") is True,
        "config_path": str(_config_path()),
        "anonymous_install_id": _current_install_id(create=False),
    }


def _scrub_properties(properties: dict[str, Any]) -> dict[str, Any]:
    scrubbed: dict[str, Any] = {}
    for key, value in properties.items():
        if key not in _ALLOWED_PROPERTY_KEYS:
            continue
        if isinstance(value, bool | int | float | str) or value is None:
            scrubbed[key] = value
    return scrubbed


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _default_sink(payload: dict[str, Any]) -> bool:
    endpoint = os.environ.get("VULCA_TELEMETRY_ENDPOINT", "").strip()
    if not endpoint:
        return False
    import httpx

    httpx.post(endpoint, json=payload, timeout=1.0)
    return True


class TelemetryClient:
    """Small opt-in telemetry client with no-op default behavior."""

    def __init__(
        self,
        *,
        interface: str,
        sink: TelemetrySink | None = None,
        session_id: str | None = None,
    ) -> None:
        enabled, source = _enabled_state()
        self.enabled = enabled
        self.source = source
        self.interface = interface
        self.session_id = session_id or uuid.uuid4().hex
        self._sink = sink or _default_sink

    def envelope(self, event: str, properties: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "event": event,
            "vulca_version": __version__,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform_mod.system().lower(),
            "interface": self.interface,
            "session_id": self.session_id,
            "anonymous_install_id": _current_install_id(create=True),
            "timestamp": _timestamp(),
            "properties": _scrub_properties(properties or {}),
        }

    def emit(self, event: str, properties: dict[str, Any] | None = None) -> bool:
        if not self.enabled:
            return False
        try:
            result = self._sink(self.envelope(event, properties))
        except Exception:
            return False
        return False if result is False else True


def _duration_bucket_ms(elapsed_ms: float) -> str:
    if elapsed_ms < 100:
        return "<100"
    if elapsed_ms < 500:
        return "100-500"
    if elapsed_ms < 1000:
        return "500-1000"
    if elapsed_ms < 5000:
        return "1000-5000"
    return "5000+"


class McpTelemetryMiddleware(Middleware):
    """FastMCP middleware that emits tool name/status without tool arguments."""

    def __init__(self, *, client: TelemetryClient | None = None) -> None:
        self.client = client or TelemetryClient(interface="mcp")

    async def on_call_tool(self, context: Any, call_next: Callable[[Any], Any]) -> Any:
        started = time.perf_counter()
        tool_name = getattr(getattr(context, "message", None), "name", "unknown")
        try:
            result = await call_next(context)
        except Exception:
            elapsed_ms = (time.perf_counter() - started) * 1000
            self.client.emit(
                "mcp_tool_called",
                {
                    "tool_name": tool_name,
                    "status": "error",
                    "duration_bucket_ms": _duration_bucket_ms(elapsed_ms),
                },
            )
            raise

        elapsed_ms = (time.perf_counter() - started) * 1000
        self.client.emit(
            "mcp_tool_called",
            {
                "tool_name": tool_name,
                "status": "ok",
                "duration_bucket_ms": _duration_bucket_ms(elapsed_ms),
            },
        )
        return result


def emit_cli_invoked(command: str) -> bool:
    return TelemetryClient(interface="cli").emit("cli_invoked", {"command": command})
