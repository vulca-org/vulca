#!/usr/bin/env python3
"""Preflight checks for the Vulca ChatGPT App submission package."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


EXPECTED_TOOLS = [
    "compose_prompt_from_design",
    "evaluate_artwork",
    "get_tradition_guide",
    "list_traditions",
    "search_traditions",
]

EXPECTED_HINTS = {
    "readOnlyHint": True,
    "openWorldHint": False,
    "destructiveHint": False,
}

FORBIDDEN_RESPONSE_KEYS = {
    "source_design_path",
    "image_path",
    "latency_ms",
    "trace_id",
    "request_id",
    "session_id",
    "api_key",
    "token",
    "password",
}

SENSITIVE_FIELD_RE = re.compile(
    r"(password|token|api[_-]?key|secret|ssn|mfa|oauth|credit|card|"
    r"government|passport|health|biometric)",
    re.IGNORECASE,
)


def _load_submission(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise AssertionError("submission JSON root must be an object")
    return data


def _check_url(
    name: str,
    raw_url: str,
    *,
    require_mcp_path: bool = False,
    allow_protocol_rejection: bool = False,
) -> str:
    if not raw_url:
        return "skipped"

    parsed = urlparse(raw_url)
    if parsed.scheme != "https":
        raise AssertionError(f"{name} must use https: {raw_url}")
    if parsed.hostname in {"localhost", "127.0.0.1", "0.0.0.0"}:
        raise AssertionError(f"{name} must not use a local host: {raw_url}")
    if require_mcp_path and not parsed.path.rstrip("/").endswith("/mcp"):
        raise AssertionError(f"{name} should point at the MCP path ending in /mcp: {raw_url}")

    request = Request(raw_url, method="HEAD")
    try:
        with urlopen(request, timeout=15) as response:
            status = getattr(response, "status", 200)
    except HTTPError as exc:
        if allow_protocol_rejection and exc.code in {400, 405, 406, 415, 501}:
            return f"HTTP {exc.code}; endpoint reachable but rejects HEAD without MCP protocol headers"
        raise AssertionError(f"{name} returned HTTP {exc.code}: {raw_url}") from exc
    except URLError as exc:
        raise AssertionError(f"{name} is not reachable with HEAD: {raw_url} ({exc})") from exc

    if status >= 400:
        raise AssertionError(f"{name} returned HTTP {status}: {raw_url}")
    return f"HTTP {status}"


def _walk_keys(obj: Any, path: str = "") -> list[str]:
    hits: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_path = f"{path}.{key}" if path else str(key)
            if str(key) in FORBIDDEN_RESPONSE_KEYS:
                hits.append(key_path)
            hits.extend(_walk_keys(value, key_path))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            hits.extend(_walk_keys(value, f"{path}[{idx}]"))
    return hits


def _contains_home_path(obj: Any) -> bool:
    home = str(Path.home())
    if not home or home == "/":
        return False
    return home in json.dumps(obj, ensure_ascii=False, sort_keys=True)


def _write_design_fixture(workspace: Path) -> Path:
    design = workspace / "design.md"
    design.write_text(
        """---
status: resolved
tradition: chinese_xieyi
---

## A. Provider + generation params

```yaml
provider: mock
model: mock
```

## C. Prompt composition

```yaml
base_prompt: "misty mountain ink study"
negative_prompt: "photorealistic"
tradition_tokens:
  - "ink wash"
  - "negative space"
color_constraint_tokens:
  - "monochrome"
style_treatment: "xieyi brush rhythm"
```
""",
        encoding="utf-8",
    )
    return design


async def _inspect_remote_tools(submission: dict[str, Any]) -> list[str]:
    from vulca.mcp_remote import remote_mcp

    messages: list[str] = []
    submission_tools = submission.get("tools", {})
    if not isinstance(submission_tools, dict):
        raise AssertionError("submission.tools must be an object")

    tools = {tool.name: tool for tool in await remote_mcp.list_tools()}
    actual_names = sorted(tools)
    expected_names = sorted(EXPECTED_TOOLS)
    submitted_names = sorted(submission_tools)

    if actual_names != expected_names:
        raise AssertionError(f"remote tool list mismatch: {actual_names} != {expected_names}")
    if submitted_names != expected_names:
        raise AssertionError(f"submission tool list mismatch: {submitted_names} != {expected_names}")

    for name in expected_names:
        tool = tools[name]
        actual_hints = tool.annotations.model_dump() if tool.annotations else {}
        submitted_hints = submission_tools[name].get("annotations", {})

        for hint, expected in EXPECTED_HINTS.items():
            if actual_hints.get(hint) is not expected:
                raise AssertionError(f"{name}.{hint} runtime hint is {actual_hints.get(hint)!r}")
            if submitted_hints.get(hint) is not expected:
                raise AssertionError(f"{name}.{hint} submission hint is {submitted_hints.get(hint)!r}")

        parameters = tool.parameters or {}
        fields = sorted((parameters.get("properties") or {}).keys())
        sensitive_fields = [field for field in fields if SENSITIVE_FIELD_RE.search(field)]
        if sensitive_fields:
            raise AssertionError(f"{name} has sensitive-looking input fields: {sensitive_fields}")

        if not tool.output_schema:
            raise AssertionError(f"{name} is missing output_schema")

        messages.append(f"tool {name}: hints ok, fields={fields}, output_schema present")

    return messages


async def _inspect_representative_responses() -> list[str]:
    from vulca import mcp_remote

    messages: list[str] = []
    with tempfile.TemporaryDirectory(prefix="vulca-chatgpt-preflight-") as tmp:
        workspace = Path(tmp)
        _write_design_fixture(workspace)
        old_root = os.environ.get("VULCA_REMOTE_WORKSPACE_ROOT")
        os.environ["VULCA_REMOTE_WORKSPACE_ROOT"] = str(workspace)
        try:
            responses = {
                "list_traditions": await mcp_remote._remote_list_traditions(),
                "get_tradition_guide": await mcp_remote._remote_get_tradition_guide("chinese_xieyi"),
                "search_traditions": await mcp_remote._remote_search_traditions(
                    ["ink wash", "negative space"],
                    limit=3,
                ),
                "compose_prompt_from_design": await mcp_remote._remote_compose_prompt_from_design("design.md"),
                "evaluate_artwork": await mcp_remote._remote_evaluate_artwork(
                    "review-placeholder.png",
                    "chinese_xieyi",
                    "misty mountain ink study",
                ),
            }
        finally:
            if old_root is None:
                os.environ.pop("VULCA_REMOTE_WORKSPACE_ROOT", None)
            else:
                os.environ["VULCA_REMOTE_WORKSPACE_ROOT"] = old_root

    for name, response in responses.items():
        hits = _walk_keys(response)
        if hits:
            raise AssertionError(f"{name} response exposes forbidden keys: {hits}")
        if _contains_home_path(response):
            raise AssertionError(f"{name} response appears to include the local home path")
        if not isinstance(response, dict):
            raise AssertionError(f"{name} response must be an object")
        messages.append(f"response {name}: no forbidden keys, top_keys={sorted(response)[:8]}")

    return messages


async def _run(args: argparse.Namespace) -> int:
    submission_path = Path(args.submission)
    submission = _load_submission(submission_path)

    print(f"submission: {submission_path}")
    print(f"schema_version: {submission.get('schema_version')}")
    print(f"app: {submission.get('app_info', {}).get('display_name')}")

    if args.privacy_url:
        detail = _check_url("privacy URL", args.privacy_url)
        print(f"privacy URL: ok ({detail}; {args.privacy_url})")

    if args.mcp_url:
        detail = _check_url(
            "MCP URL",
            args.mcp_url,
            require_mcp_path=True,
            allow_protocol_rejection=True,
        )
        print(f"MCP URL: ok ({detail}; {args.mcp_url})")

    for message in await _inspect_remote_tools(submission):
        print(message)

    positive_cases = submission.get("test_cases", [])
    negative_cases = submission.get("negative_test_cases", [])
    if len(positive_cases) < 5:
        raise AssertionError("submission must include at least five positive test cases")
    if len(negative_cases) < 3:
        raise AssertionError("submission must include at least three negative test cases")
    print(f"test cases: {len(positive_cases)} positive, {len(negative_cases)} negative")

    for message in await _inspect_representative_responses():
        print(message)

    print("preflight: ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission", default="chatgpt-app-submission.json")
    parser.add_argument("--privacy-url", default="")
    parser.add_argument("--mcp-url", default="")
    args = parser.parse_args()

    try:
        return asyncio.run(_run(args))
    except Exception as exc:
        print(f"preflight: failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
