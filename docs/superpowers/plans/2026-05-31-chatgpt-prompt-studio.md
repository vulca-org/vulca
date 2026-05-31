# ChatGPT Prompt Studio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a preview-gated ChatGPT Prompt Studio that lets Vulca package a prompt/rubric handoff and ask ChatGPT native image generation to continue, without exposing Vulca provider image generation.

**Architecture:** Keep the submitted remote profile unchanged by default. Add a pure prompt-package helper, a vanilla MCP Apps widget resource, and an `open_prompt_studio` render tool that is registered only when `VULCA_REMOTE_ENABLE_PROMPT_STUDIO=1` or when tests explicitly build the preview server.

**Tech Stack:** Python 3.10+, FastMCP 3, MCP Apps UI resources, vanilla HTML/CSS/JS, pytest, ruff.

---

## File Structure

- Create `src/vulca/chatgpt_prompt_studio.py`: pure Python prompt package builder, follow-up message formatter, widget URI constant.
- Create `src/vulca/chatgpt_prompt_studio_widget.py`: static HTML/CSS/JS widget string for the Prompt Studio UI.
- Modify `src/vulca/mcp_profiles.py`: add preview-only tool listing support and policy for `open_prompt_studio`.
- Modify `src/vulca/mcp_remote.py`: add a server builder, preview flag, widget resource registration, and render tool registration.
- Add `tests/test_chatgpt_prompt_studio.py`: pure helper tests.
- Add `tests/test_mcp_remote_prompt_studio.py`: preview-gated FastMCP registration, resource, metadata, and handler tests.
- Add `docs/platform/chatgpt-prompt-studio-preview.md`: operator note for running the preview safely.

## Scope Guard

This plan must not expose provider tools. The following tools stay denied in all
profiles: `generate_image`, `create_artwork`, `generate_concepts`,
`inpaint_artwork`, `layers_redraw`, `view_image`, and the rest of the current
`REMOTE_DENIED_TOOLS` set.

The default `remote_mcp` import must still expose the current five submitted
tools unless `VULCA_REMOTE_ENABLE_PROMPT_STUDIO=1` is set before import.

### Task 1: Prompt Package Builder

**Files:**
- Create: `src/vulca/chatgpt_prompt_studio.py`
- Test: `tests/test_chatgpt_prompt_studio.py`

- [ ] **Step 1: Write failing tests for package normalization and empty prompts**

Create `tests/test_chatgpt_prompt_studio.py`:

```python
from __future__ import annotations

import pytest

from vulca.chatgpt_prompt_studio import (
    PROMPT_STUDIO_WIDGET_URI,
    build_prompt_studio_package,
)


def test_build_prompt_studio_package_normalizes_fields():
    package = build_prompt_studio_package(
        prompt_title="  Ink mountain study  ",
        tradition=" chinese_xieyi ",
        final_prompt="  misty mountain ink study with negative space  ",
        negative_prompt=" photorealistic, glossy  ",
        generation_notes=" square composition ",
        rubric_summary=" L5: qi resonance; L3: composition rhythm ",
    )

    assert package["prompt_title"] == "Ink mountain study"
    assert package["tradition"] == "chinese_xieyi"
    assert package["final_prompt"] == "misty mountain ink study with negative space"
    assert package["negative_prompt"] == "photorealistic, glossy"
    assert package["generation_notes"] == "square composition"
    assert package["rubric_summary"] == "L5: qi resonance; L3: composition rhythm"
    assert package["widget_uri"] == PROMPT_STUDIO_WIDGET_URI
    assert package["followup_message"].startswith(
        "Generate an image in ChatGPT using this Vulca prompt."
    )
    assert "Title: Ink mountain study" in package["followup_message"]
    assert "Tradition: chinese_xieyi" in package["followup_message"]
    assert "Negative constraints: photorealistic, glossy" in package["followup_message"]


def test_build_prompt_studio_package_uses_safe_defaults():
    package = build_prompt_studio_package(
        prompt_title="",
        tradition="",
        final_prompt="misty mountain",
    )

    assert package["prompt_title"] == "Vulca image prompt"
    assert package["tradition"] == "unspecified"
    assert package["negative_prompt"] == ""
    assert "Negative constraints: none" in package["followup_message"]


def test_build_prompt_studio_package_rejects_empty_final_prompt():
    with pytest.raises(ValueError, match="final_prompt is required"):
        build_prompt_studio_package(
            prompt_title="Ink mountain",
            tradition="chinese_xieyi",
            final_prompt="   ",
        )
```

- [ ] **Step 2: Run the helper tests and verify they fail**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_chatgpt_prompt_studio.py -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vulca.chatgpt_prompt_studio'`.

- [ ] **Step 3: Add the prompt package helper**

Create `src/vulca/chatgpt_prompt_studio.py`:

```python
from __future__ import annotations

from typing import Any


PROMPT_STUDIO_WIDGET_URI = "ui://vulca/prompt-studio.html"


def _clean(value: str | None) -> str:
    return " ".join(str(value or "").split())


def build_followup_message(package: dict[str, Any]) -> str:
    negative_prompt = package["negative_prompt"] or "none"
    generation_notes = package["generation_notes"] or "none"
    rubric_summary = package["rubric_summary"] or "use Vulca's L1-L5 rubric"

    return (
        "Generate an image in ChatGPT using this Vulca prompt. "
        "Preserve the tradition, composition, negative constraints, and rubric "
        "priorities exactly.\n\n"
        f"Title: {package['prompt_title']}\n"
        f"Tradition: {package['tradition']}\n"
        f"Prompt: {package['final_prompt']}\n"
        f"Negative constraints: {negative_prompt}\n"
        f"Generation notes: {generation_notes}\n"
        f"Rubric priorities: {rubric_summary}"
    )


def build_prompt_studio_package(
    *,
    prompt_title: str = "",
    tradition: str = "",
    final_prompt: str,
    negative_prompt: str = "",
    generation_notes: str = "",
    rubric_summary: str = "",
) -> dict[str, Any]:
    final_prompt = _clean(final_prompt)
    if not final_prompt:
        raise ValueError("final_prompt is required for Prompt Studio")

    package: dict[str, Any] = {
        "prompt_title": _clean(prompt_title) or "Vulca image prompt",
        "tradition": _clean(tradition) or "unspecified",
        "final_prompt": final_prompt,
        "negative_prompt": _clean(negative_prompt),
        "generation_notes": _clean(generation_notes),
        "rubric_summary": _clean(rubric_summary),
        "widget_uri": PROMPT_STUDIO_WIDGET_URI,
    }
    package["followup_message"] = build_followup_message(package)
    return package
```

- [ ] **Step 4: Run the helper tests and verify they pass**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_chatgpt_prompt_studio.py -q
```

Expected: `3 passed`.

- [ ] **Step 5: Commit the helper**

```bash
git add src/vulca/chatgpt_prompt_studio.py tests/test_chatgpt_prompt_studio.py
git commit -m "feat: add ChatGPT prompt studio package builder"
```

### Task 2: Static Prompt Studio Widget

**Files:**
- Create: `src/vulca/chatgpt_prompt_studio_widget.py`
- Modify: `tests/test_chatgpt_prompt_studio.py`

- [ ] **Step 1: Add failing widget static checks**

Append to `tests/test_chatgpt_prompt_studio.py`:

```python
from vulca.chatgpt_prompt_studio_widget import PROMPT_STUDIO_WIDGET_HTML


def test_prompt_studio_widget_contains_bridge_and_fallbacks():
    assert "window.openai.sendFollowUpMessage" in PROMPT_STUDIO_WIDGET_HTML
    assert "window.openai.setWidgetState" in PROMPT_STUDIO_WIDGET_HTML
    assert "navigator.clipboard.writeText" in PROMPT_STUDIO_WIDGET_HTML
    assert "Generate in ChatGPT" in PROMPT_STUDIO_WIDGET_HTML
    assert "Copy prompt" in PROMPT_STUDIO_WIDGET_HTML
    assert "data-field=\"final_prompt\"" in PROMPT_STUDIO_WIDGET_HTML
```

- [ ] **Step 2: Run the widget test and verify it fails**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_chatgpt_prompt_studio.py::test_prompt_studio_widget_contains_bridge_and_fallbacks -q
```

Expected: FAIL with `ModuleNotFoundError: No module named 'vulca.chatgpt_prompt_studio_widget'`.

- [ ] **Step 3: Add the widget HTML constant**

Create `src/vulca/chatgpt_prompt_studio_widget.py`:

```python
from __future__ import annotations


PROMPT_STUDIO_WIDGET_HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Vulca Prompt Studio</title>
    <style>
      :root {
        color-scheme: light dark;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: Canvas;
        color: CanvasText;
      }
      * { box-sizing: border-box; }
      body { margin: 0; padding: 16px; }
      main { display: grid; gap: 12px; max-width: 760px; }
      header { display: grid; gap: 4px; }
      h1 { font-size: 18px; line-height: 1.25; margin: 0; }
      .meta { color: color-mix(in srgb, CanvasText 68%, transparent); font-size: 13px; }
      label { display: grid; gap: 6px; font-size: 13px; font-weight: 650; }
      textarea {
        width: 100%;
        min-height: 180px;
        resize: vertical;
        border: 1px solid color-mix(in srgb, CanvasText 22%, transparent);
        border-radius: 8px;
        padding: 10px;
        background: Canvas;
        color: CanvasText;
        font: 13px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      }
      .row { display: flex; flex-wrap: wrap; gap: 8px; }
      button {
        border: 1px solid color-mix(in srgb, CanvasText 22%, transparent);
        border-radius: 8px;
        padding: 8px 12px;
        background: Canvas;
        color: CanvasText;
        font: inherit;
        cursor: pointer;
      }
      button.primary {
        background: CanvasText;
        color: Canvas;
        border-color: CanvasText;
      }
      button:disabled { opacity: 0.45; cursor: not-allowed; }
      details {
        border-top: 1px solid color-mix(in srgb, CanvasText 14%, transparent);
        padding-top: 10px;
      }
      summary { cursor: pointer; font-weight: 650; }
      pre {
        margin: 8px 0 0;
        white-space: pre-wrap;
        font: 13px/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      }
      .status { min-height: 18px; font-size: 13px; color: color-mix(in srgb, CanvasText 72%, transparent); }
    </style>
  </head>
  <body>
    <main>
      <header>
        <h1 id="title">Vulca Prompt Studio</h1>
        <div class="meta" id="tradition"></div>
      </header>
      <label>
        Final prompt
        <textarea data-field="final_prompt" id="finalPrompt"></textarea>
      </label>
      <div class="row">
        <button class="primary" id="generateButton" type="button">Generate in ChatGPT</button>
        <button id="copyButton" type="button">Copy prompt</button>
      </div>
      <div class="status" id="status" role="status" aria-live="polite"></div>
      <details open>
        <summary>Negative constraints</summary>
        <pre id="negativePrompt"></pre>
      </details>
      <details>
        <summary>Generation notes</summary>
        <pre id="generationNotes"></pre>
      </details>
      <details>
        <summary>Rubric priorities</summary>
        <pre id="rubricSummary"></pre>
      </details>
    </main>
    <script>
      const openai = window.openai || {};
      const toolOutput = openai.toolOutput || {};
      const widgetState = openai.widgetState || {};
      const data = { ...toolOutput, ...widgetState };

      const title = document.getElementById("title");
      const tradition = document.getElementById("tradition");
      const finalPrompt = document.getElementById("finalPrompt");
      const negativePrompt = document.getElementById("negativePrompt");
      const generationNotes = document.getElementById("generationNotes");
      const rubricSummary = document.getElementById("rubricSummary");
      const generateButton = document.getElementById("generateButton");
      const copyButton = document.getElementById("copyButton");
      const status = document.getElementById("status");

      function valueOrNone(value) {
        const text = String(value || "").trim();
        return text || "none";
      }

      function buildFollowupMessage() {
        return [
          "Generate an image in ChatGPT using this Vulca prompt. Preserve the tradition, composition, negative constraints, and rubric priorities exactly.",
          "",
          `Title: ${valueOrNone(data.prompt_title)}`,
          `Tradition: ${valueOrNone(data.tradition)}`,
          `Prompt: ${finalPrompt.value.trim()}`,
          `Negative constraints: ${valueOrNone(data.negative_prompt)}`,
          `Generation notes: ${valueOrNone(data.generation_notes)}`,
          `Rubric priorities: ${valueOrNone(data.rubric_summary)}`
        ].join("\\n");
      }

      function syncDisabledState() {
        generateButton.disabled = finalPrompt.value.trim().length === 0;
      }

      async function saveState() {
        data.final_prompt = finalPrompt.value;
        if (window.openai && window.openai.setWidgetState) {
          await window.openai.setWidgetState({ final_prompt: finalPrompt.value });
        }
      }

      async function copyText(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(text);
          return;
        }
        finalPrompt.focus();
        finalPrompt.select();
        document.execCommand("copy");
      }

      title.textContent = valueOrNone(data.prompt_title);
      tradition.textContent = `Tradition: ${valueOrNone(data.tradition)}`;
      finalPrompt.value = data.final_prompt || "";
      negativePrompt.textContent = valueOrNone(data.negative_prompt);
      generationNotes.textContent = valueOrNone(data.generation_notes);
      rubricSummary.textContent = valueOrNone(data.rubric_summary);
      syncDisabledState();

      finalPrompt.addEventListener("input", async () => {
        syncDisabledState();
        await saveState();
      });

      copyButton.addEventListener("click", async () => {
        await copyText(buildFollowupMessage());
        status.textContent = "Prompt copied.";
      });

      generateButton.addEventListener("click", async () => {
        await saveState();
        const prompt = buildFollowupMessage();
        if (!(window.openai && window.openai.sendFollowUpMessage)) {
          await copyText(prompt);
          status.textContent = "ChatGPT follow-up is unavailable here. Prompt copied instead.";
          return;
        }
        try {
          await window.openai.sendFollowUpMessage({ prompt, scrollToBottom: true });
          status.textContent = "Sent to ChatGPT.";
        } catch (error) {
          await copyText(prompt);
          status.textContent = "Could not send follow-up. Prompt copied instead.";
        }
      });
    </script>
  </body>
</html>
"""
```

- [ ] **Step 4: Run helper and widget tests**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_chatgpt_prompt_studio.py -q
```

Expected: `4 passed`.

- [ ] **Step 5: Commit the widget**

```bash
git add src/vulca/chatgpt_prompt_studio_widget.py tests/test_chatgpt_prompt_studio.py
git commit -m "feat: add ChatGPT prompt studio widget"
```

### Task 3: Preview-Gated Remote Tool And Resource

**Files:**
- Modify: `src/vulca/mcp_profiles.py`
- Modify: `src/vulca/mcp_remote.py`
- Test: `tests/test_mcp_remote_profile.py`
- Create: `tests/test_mcp_remote_prompt_studio.py`

- [ ] **Step 1: Add failing profile tests for default and preview tool sets**

Append to `tests/test_mcp_remote_profile.py`:

```python
def test_remote_profile_can_list_prompt_studio_preview_tools():
    from vulca.mcp_profiles import list_remote_safe_tools

    assert list_remote_safe_tools(include_prompt_studio=True) == [
        "compose_prompt_from_design",
        "evaluate_artwork",
        "get_tradition_guide",
        "list_traditions",
        "open_prompt_studio",
        "search_traditions",
    ]


def test_remote_tool_policy_marks_prompt_studio_as_safe_preview_tool():
    policy = get_remote_tool_policy("open_prompt_studio")

    assert policy.name == "open_prompt_studio"
    assert policy.allowed is True
    assert policy.access == "read"
    assert policy.cost == "none"
    assert policy.image_exposure == "none"
    assert policy.requires_approval is False
```

- [ ] **Step 2: Add failing remote preview tests**

Create `tests/test_mcp_remote_prompt_studio.py`:

```python
from __future__ import annotations

import asyncio

from vulca.chatgpt_prompt_studio import PROMPT_STUDIO_WIDGET_URI
from vulca.mcp_remote import build_remote_mcp_server


def test_prompt_studio_preview_registers_tool_with_ui_metadata():
    server = build_remote_mcp_server(enable_prompt_studio=True)

    tools = asyncio.run(server.list_tools())
    by_name = {tool.name: tool for tool in tools}

    assert "open_prompt_studio" in by_name
    tool = by_name["open_prompt_studio"]
    assert tool.annotations is not None
    assert tool.annotations.readOnlyHint is True
    assert tool.annotations.destructiveHint is False
    assert tool.annotations.openWorldHint is False
    assert tool.meta == {
        "ui": {
            "resourceUri": PROMPT_STUDIO_WIDGET_URI,
            "visibility": ["model"],
            "prefersBorder": True,
        },
        "openai/toolInvocation/invoking": "Opening Vulca Prompt Studio",
        "openai/toolInvocation/invoked": "Vulca Prompt Studio ready",
    }


def test_prompt_studio_preview_registers_widget_resource():
    server = build_remote_mcp_server(enable_prompt_studio=True)

    resources = asyncio.run(server.list_resources())
    by_uri = {str(resource.uri): resource for resource in resources}

    assert PROMPT_STUDIO_WIDGET_URI in by_uri
    resource = by_uri[PROMPT_STUDIO_WIDGET_URI]
    assert resource.mime_type == "text/html;profile=mcp-app"
    assert resource.meta == {
        "ui": {
            "csp": {"connectDomains": [], "resourceDomains": []},
            "prefersBorder": True,
        }
    }

    result = asyncio.run(server.read_resource(PROMPT_STUDIO_WIDGET_URI))
    assert result.contents[0].mime_type == "text/html;profile=mcp-app"
    assert "Generate in ChatGPT" in result.contents[0].content


def test_prompt_studio_tool_returns_structured_content_and_output_template():
    server = build_remote_mcp_server(enable_prompt_studio=True)

    result = asyncio.run(
        server.call_tool(
            "open_prompt_studio",
            {
                "prompt_title": "Ink mountain",
                "tradition": "chinese_xieyi",
                "final_prompt": "misty mountain ink study",
                "negative_prompt": "photorealistic",
                "generation_notes": "square format",
                "rubric_summary": "L5 qi resonance",
            },
        )
    )

    assert result.structured_content["final_prompt"] == "misty mountain ink study"
    assert result.structured_content["negative_prompt"] == "photorealistic"
    assert result.structured_content["followup_message"].startswith(
        "Generate an image in ChatGPT using this Vulca prompt."
    )
    assert result.meta == {"openai/outputTemplate": PROMPT_STUDIO_WIDGET_URI}


def test_prompt_studio_tool_returns_structured_error_for_empty_prompt():
    server = build_remote_mcp_server(enable_prompt_studio=True)

    result = asyncio.run(
        server.call_tool(
            "open_prompt_studio",
            {
                "prompt_title": "Ink mountain",
                "tradition": "chinese_xieyi",
                "final_prompt": " ",
            },
        )
    )

    assert result.structured_content == {
        "error": "final_prompt is required for Prompt Studio",
        "widget_uri": PROMPT_STUDIO_WIDGET_URI,
    }
    assert result.meta == {"openai/outputTemplate": PROMPT_STUDIO_WIDGET_URI}
```

- [ ] **Step 3: Run the new remote tests and verify they fail**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_mcp_remote_profile.py::test_remote_profile_can_list_prompt_studio_preview_tools tests/test_mcp_remote_profile.py::test_remote_tool_policy_marks_prompt_studio_as_safe_preview_tool tests/test_mcp_remote_prompt_studio.py -q
```

Expected: FAIL because `include_prompt_studio` and `build_remote_mcp_server` do not exist yet.

- [ ] **Step 4: Add preview tool policy support**

Modify `src/vulca/mcp_profiles.py`:

```python
REMOTE_PROMPT_STUDIO_TOOLS = frozenset({"open_prompt_studio"})


def list_remote_safe_tools(*, include_prompt_studio: bool = False) -> list[str]:
    tools = set(REMOTE_SAFE_TOOLS)
    if include_prompt_studio:
        tools.update(REMOTE_PROMPT_STUDIO_TOOLS)
    return sorted(tools)
```

Add this policy entry to `_POLICIES`:

```python
    "open_prompt_studio": RemoteToolPolicy(
        name="open_prompt_studio",
        allowed=True,
        access="read",
        cost="none",
        image_exposure="none",
        requires_approval=False,
    ),
```

Keep `REMOTE_SAFE_TOOLS` as the existing five submitted tools. Do not add
`open_prompt_studio` to `REMOTE_DENIED_TOOLS`.

- [ ] **Step 5: Refactor remote server construction and register the preview UI**

Modify `src/vulca/mcp_remote.py`.

Add imports:

```python
from fastmcp.apps.config import AppConfig, ResourceCSP
from fastmcp.tools import ToolResult
from fastmcp.utilities.mime import UI_MIME_TYPE

from vulca.chatgpt_prompt_studio import (
    PROMPT_STUDIO_WIDGET_URI,
    build_prompt_studio_package,
)
from vulca.chatgpt_prompt_studio_widget import PROMPT_STUDIO_WIDGET_HTML
```

Replace the top-level `remote_mcp = FastMCP(...)` block and the direct
registration calls with these functions and assignments:

```python
def is_prompt_studio_preview_enabled() -> bool:
    return os.environ.get(
        "VULCA_REMOTE_ENABLE_PROMPT_STUDIO",
        "",
    ).lower() in {"1", "true", "yes", "on"}


def _remote_tool_annotations(tool_names: list[str]) -> dict[str, dict[str, bool]]:
    return {
        tool_name: {
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False,
            "idempotentHint": True,
        }
        for tool_name in tool_names
    }


async def _remote_open_prompt_studio(
    final_prompt: str,
    prompt_title: str = "",
    tradition: str = "",
    negative_prompt: str = "",
    generation_notes: str = "",
    rubric_summary: str = "",
) -> ToolResult:
    """Use this when the user wants a ChatGPT-native image generation handoff from a Vulca prompt package."""
    try:
        package = build_prompt_studio_package(
            prompt_title=prompt_title,
            tradition=tradition,
            final_prompt=final_prompt,
            negative_prompt=negative_prompt,
            generation_notes=generation_notes,
            rubric_summary=rubric_summary,
        )
        content = "Opened Vulca Prompt Studio for ChatGPT-native image generation."
    except ValueError as exc:
        package = {
            "error": str(exc),
            "widget_uri": PROMPT_STUDIO_WIDGET_URI,
        }
        content = f"Vulca Prompt Studio could not open: {exc}"

    return ToolResult(
        content=content,
        structured_content=package,
        meta={"openai/outputTemplate": PROMPT_STUDIO_WIDGET_URI},
    )


def _register_prompt_studio(server: FastMCP, annotations: dict[str, dict[str, bool]]) -> None:
    server.resource(
        PROMPT_STUDIO_WIDGET_URI,
        name="prompt_studio_widget",
        mime_type=UI_MIME_TYPE,
        app=AppConfig(
            prefersBorder=True,
            csp=ResourceCSP(connectDomains=[], resourceDomains=[]),
        ),
    )(lambda: PROMPT_STUDIO_WIDGET_HTML)

    server.tool(
        name="open_prompt_studio",
        annotations=annotations["open_prompt_studio"],
        app=AppConfig(
            resourceUri=PROMPT_STUDIO_WIDGET_URI,
            visibility=["model"],
            prefersBorder=True,
        ),
        meta={
            "openai/toolInvocation/invoking": "Opening Vulca Prompt Studio",
            "openai/toolInvocation/invoked": "Vulca Prompt Studio ready",
        },
    )(_remote_open_prompt_studio)


def build_remote_mcp_server(*, enable_prompt_studio: bool = False) -> FastMCP:
    server = FastMCP(
        "VULCA Remote",
        instructions=(
            "Remote-safe Vulca profile for ChatGPT and OpenAI Responses MCP. "
            "Only discovery, tradition lookup, prompt composition, and mock "
            "rubric evaluation tools are exposed."
        ),
    )
    tool_names = list_remote_safe_tools(include_prompt_studio=enable_prompt_studio)
    annotations = _remote_tool_annotations(tool_names)

    server.tool(
        name="list_traditions",
        annotations=annotations["list_traditions"],
    )(_remote_list_traditions)
    server.tool(
        name="get_tradition_guide",
        annotations=annotations["get_tradition_guide"],
    )(_remote_get_tradition_guide)
    server.tool(
        name="search_traditions",
        annotations=annotations["search_traditions"],
    )(_remote_search_traditions)
    server.tool(
        name="compose_prompt_from_design",
        annotations=annotations["compose_prompt_from_design"],
    )(_remote_compose_prompt_from_design)
    server.tool(
        name="evaluate_artwork",
        annotations=annotations["evaluate_artwork"],
    )(_remote_evaluate_artwork)

    if enable_prompt_studio:
        _register_prompt_studio(server, annotations)

    return server


REMOTE_APP_TOOL_ANNOTATIONS = _remote_tool_annotations(list_remote_safe_tools())
remote_mcp = build_remote_mcp_server(
    enable_prompt_studio=is_prompt_studio_preview_enabled()
)
```

Update `build_remote_mcp_server_summary`:

```python
def build_remote_mcp_server_summary(
    *,
    enable_prompt_studio: bool | None = None,
) -> dict[str, object]:
    if enable_prompt_studio is None:
        enable_prompt_studio = is_prompt_studio_preview_enabled()
    allowed_tools = list_remote_safe_tools(
        include_prompt_studio=enable_prompt_studio,
    )
    return {
        "profile": "chatgpt_remote_safe",
        "transport_status": "streamable_http_ready",
        "allowed_tools": allowed_tools,
        "policies": {
            tool_name: _policy_to_dict(tool_name)
            for tool_name in allowed_tools
        },
    }
```

- [ ] **Step 6: Run the focused remote tests and verify they pass**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_mcp_remote_profile.py tests/test_mcp_remote_prompt_studio.py -q
```

Expected: all tests in both files pass.

- [ ] **Step 7: Verify default import still exposes only the submitted five tools**

Run:

```bash
PYTHONPATH=src python3 - <<'PY'
import asyncio
from vulca.mcp_remote import remote_mcp

async def main():
    tools = sorted(tool.name for tool in await remote_mcp.list_tools())
    print(tools)

asyncio.run(main())
PY
```

Expected:

```text
['compose_prompt_from_design', 'evaluate_artwork', 'get_tradition_guide', 'list_traditions', 'search_traditions']
```

- [ ] **Step 8: Verify environment flag enables the preview tool**

Run:

```bash
VULCA_REMOTE_ENABLE_PROMPT_STUDIO=1 PYTHONPATH=src python3 - <<'PY'
import asyncio
from vulca.mcp_remote import remote_mcp

async def main():
    tools = sorted(tool.name for tool in await remote_mcp.list_tools())
    print(tools)

asyncio.run(main())
PY
```

Expected:

```text
['compose_prompt_from_design', 'evaluate_artwork', 'get_tradition_guide', 'list_traditions', 'open_prompt_studio', 'search_traditions']
```

- [ ] **Step 9: Commit the remote preview registration**

```bash
git add src/vulca/mcp_profiles.py src/vulca/mcp_remote.py tests/test_mcp_remote_profile.py tests/test_mcp_remote_prompt_studio.py
git commit -m "feat: add preview-gated ChatGPT prompt studio tool"
```

### Task 4: Preview Documentation And Submission Guardrails

**Files:**
- Create: `docs/platform/chatgpt-prompt-studio-preview.md`
- Modify: `tests/test_mcp_remote_prompt_studio.py`

- [ ] **Step 1: Add guardrail test that provider tools remain denied in preview**

Append to `tests/test_mcp_remote_prompt_studio.py`:

```python
from vulca.mcp_profiles import REMOTE_DENIED_TOOLS, REMOTE_SAFE_TOOLS


def test_prompt_studio_preview_does_not_enable_provider_tools():
    unsafe = {
        "generate_image",
        "create_artwork",
        "generate_concepts",
        "inpaint_artwork",
        "layers_redraw",
        "view_image",
    }

    assert unsafe <= REMOTE_DENIED_TOOLS
    assert "open_prompt_studio" not in REMOTE_SAFE_TOOLS
```

- [ ] **Step 2: Run the guardrail test and verify it passes**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_mcp_remote_prompt_studio.py::test_prompt_studio_preview_does_not_enable_provider_tools -q
```

Expected: `1 passed`.

- [ ] **Step 3: Add preview operator documentation**

Create `docs/platform/chatgpt-prompt-studio-preview.md`:

```markdown
# ChatGPT Prompt Studio Preview

Date: 2026-05-31

Prompt Studio is a preview-gated ChatGPT App flow. It lets Vulca package a
prompt, negative constraints, generation notes, and L1-L5 rubric priorities for
ChatGPT native image generation. It does not call Vulca provider image
generation.

## Enable Preview

Run the remote MCP server with:

```bash
VULCA_REMOTE_ENABLE_PROMPT_STUDIO=1 PYTHONPATH=src python3 -m vulca.mcp_remote
```

The default remote profile remains the submitted five-tool profile when the
environment variable is absent.

## Expected Preview Tools

- `list_traditions`
- `search_traditions`
- `get_tradition_guide`
- `compose_prompt_from_design`
- `evaluate_artwork`
- `open_prompt_studio`

## Boundary

Prompt Studio is a handoff UI. The widget calls the ChatGPT Apps bridge with
`sendFollowUpMessage` when the user presses `Generate in ChatGPT`. Vulca does not
receive generated image bytes and does not invoke OpenAI Image API, Responses API
image generation, Gemini, ComfyUI, or local image providers.

## Deployment Note

Do not deploy this preview to the submitted production MCP endpoint until the app
review risk is acceptable and the submission JSON is updated to match the new
tool surface.
```

- [ ] **Step 4: Run docs and test checks**

Run:

```bash
git diff --check
PYTHONPATH=src python3 -m pytest tests/test_chatgpt_prompt_studio.py tests/test_mcp_remote_profile.py tests/test_mcp_remote_prompt_studio.py -q
```

Expected: `git diff --check` exits 0 and pytest reports all tests passed.

- [ ] **Step 5: Commit the docs and guardrail**

```bash
git add docs/platform/chatgpt-prompt-studio-preview.md tests/test_mcp_remote_prompt_studio.py
git commit -m "docs: document ChatGPT prompt studio preview"
```

### Task 5: Final Verification

**Files:**
- No file changes expected.

- [ ] **Step 1: Run lint on changed Python files**

Run:

```bash
ruff check src/vulca/chatgpt_prompt_studio.py src/vulca/chatgpt_prompt_studio_widget.py src/vulca/mcp_profiles.py src/vulca/mcp_remote.py tests/test_chatgpt_prompt_studio.py tests/test_mcp_remote_prompt_studio.py tests/test_mcp_remote_profile.py
```

Expected: `All checks passed!`

- [ ] **Step 2: Run focused tests**

Run:

```bash
PYTHONPATH=src python3 -m pytest tests/test_chatgpt_prompt_studio.py tests/test_mcp_remote_profile.py tests/test_mcp_remote_prompt_studio.py -q
```

Expected: all tests pass.

- [ ] **Step 3: Run existing ChatGPT submission preflight without preview**

Run:

```bash
PYTHONPATH=src python3 scripts/chatgpt_app_preflight.py --submission chatgpt-app-submission.json
```

Expected: preflight reports the existing five submitted tools and exits 0.

- [ ] **Step 4: Confirm the working tree only contains intended changes**

Run:

```bash
git status --short
```

Expected: no tracked or untracked implementation files remain after commits.
