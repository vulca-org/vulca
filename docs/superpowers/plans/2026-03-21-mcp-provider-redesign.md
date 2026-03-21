# MCP Server + Provider Abstraction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade VULCA's MCP server from 3 incomplete tools to 6 production-quality tools with view/format params, and add pluggable ImageProvider + VLMProvider protocols for custom model backends.

**Architecture:** Three-layer integration (CLI most complete, SDK wraps, MCP lightweight). Provider Protocol pattern with runtime_checkable interfaces. Built-in implementations for Gemini, OpenAI, ComfyUI, and Mock.

**Tech Stack:** Python 3.10+, FastMCP 3.x, LiteLLM, httpx, Protocol (typing)

**Spec:** `docs/superpowers/specs/2026-03-21-mcp-provider-redesign.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `src/vulca/providers/__init__.py` | Create | Re-exports: ImageProvider, VLMProvider, ImageResult, L1L5Scores |
| `src/vulca/providers/base.py` | Create | Protocol definitions + dataclasses |
| `src/vulca/providers/mock.py` | Create | MockImageProvider + MockVLMProvider (extract from generate.py + _vlm.py) |
| `src/vulca/providers/gemini.py` | Create | GeminiImageProvider (extract from generate.py) |
| `src/vulca/providers/openai_provider.py` | Create | OpenAIImageProvider (DALL-E 3) |
| `src/vulca/providers/comfyui.py` | Create | ComfyUIImageProvider (REST API) |
| `src/vulca/providers/vlm_litellm.py` | Create | LiteLLMVLMProvider (extract from _vlm.py) |
| `src/vulca/pipeline/nodes/generate.py` | Modify | Use ImageProvider protocol instead of hardcoded providers |
| `src/vulca/_vlm.py` | Modify | Use VLMProvider protocol, keep as default entry point |
| `src/vulca/mcp_server.py` | Rewrite | 6 tools with view/format params |
| `src/vulca/cli.py` | Modify | Add `tradition`, `evolution` commands + provider flags |
| `src/vulca/create.py` | Modify | Add `image_provider`, `vlm_provider` params |
| `src/vulca/evaluate.py` | Modify | Add `vlm_provider` param |
| `src/vulca/cultural/loader.py` | Modify | Add `get_tradition_guide()` public function |
| `tests/test_providers.py` | Create | Provider protocol + built-in implementation tests |
| `tests/test_mcp_v2.py` | Create | All 6 MCP tools with view/format combos |

---

## Task 1: Provider Protocol Definitions

**Files:**
- Create: `src/vulca/providers/__init__.py`
- Create: `src/vulca/providers/base.py`
- Test: `tests/test_providers.py`

- [ ] **Step 1: Write failing test for Protocol**

```python
# tests/test_providers.py
"""Tests for provider protocols and built-in implementations."""
import pytest
from vulca.providers.base import ImageProvider, VLMProvider, ImageResult, L1L5Scores


class TestImageResult:
    def test_defaults(self):
        r = ImageResult(image_b64="abc")
        assert r.image_b64 == "abc"
        assert r.mime == "image/png"
        assert r.metadata is None

    def test_custom(self):
        r = ImageResult(image_b64="x", mime="image/svg+xml", metadata={"w": 512})
        assert r.mime == "image/svg+xml"
        assert r.metadata["w"] == 512


class TestL1L5Scores:
    def test_defaults(self):
        s = L1L5Scores(L1=0.8, L2=0.7, L3=0.9, L4=0.75, L5=0.85)
        assert s.L1 == 0.8
        assert s.rationales is None

    def test_with_rationales(self):
        s = L1L5Scores(L1=0.8, L2=0.7, L3=0.9, L4=0.75, L5=0.85,
                       rationales={"L1": "Good composition"})
        assert s.rationales["L1"] == "Good composition"


class TestProtocolCompliance:
    def test_image_provider_protocol(self):
        """Any class with async generate() should satisfy ImageProvider."""
        class Custom:
            async def generate(self, prompt, **kwargs):
                return ImageResult(image_b64="test")
        assert isinstance(Custom(), ImageProvider)

    def test_vlm_provider_protocol(self):
        """Any class with async score() should satisfy VLMProvider."""
        class Custom:
            async def score(self, image_b64, **kwargs):
                return L1L5Scores(L1=0.5, L2=0.5, L3=0.5, L4=0.5, L5=0.5)
        assert isinstance(Custom(), VLMProvider)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/yhryzy/projects/website/vulca && .venv/bin/python -m pytest tests/test_providers.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'vulca.providers'`

- [ ] **Step 3: Create providers package**

```python
# src/vulca/providers/__init__.py
"""Pluggable provider interfaces for image generation and VLM scoring."""
from vulca.providers.base import ImageProvider, ImageResult, L1L5Scores, VLMProvider

__all__ = ["ImageProvider", "VLMProvider", "ImageResult", "L1L5Scores"]
```

```python
# src/vulca/providers/base.py
"""Protocol definitions for pluggable providers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable


@dataclass
class ImageResult:
    """Result from an image generation provider."""
    image_b64: str
    mime: str = "image/png"
    metadata: dict | None = None


@dataclass
class L1L5Scores:
    """L1-L5 dimension scores from a VLM provider."""
    L1: float
    L2: float
    L3: float
    L4: float
    L5: float
    rationales: dict[str, str] | None = None


@runtime_checkable
class ImageProvider(Protocol):
    """Protocol for image generation backends."""
    async def generate(
        self,
        prompt: str,
        *,
        tradition: str = "",
        subject: str = "",
        reference_image_b64: str = "",
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        **kwargs,
    ) -> ImageResult: ...


@runtime_checkable
class VLMProvider(Protocol):
    """Protocol for VLM scoring backends."""
    async def score(
        self,
        image_b64: str,
        *,
        tradition: str = "",
        subject: str = "",
        guidance: str = "",
        **kwargs,
    ) -> L1L5Scores: ...
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/yhryzy/projects/website/vulca && .venv/bin/python -m pytest tests/test_providers.py -v`
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
cd /home/yhryzy/projects/website/vulca
git add src/vulca/providers/__init__.py src/vulca/providers/base.py tests/test_providers.py
git commit -m "feat: add ImageProvider + VLMProvider protocol definitions"
```

---

## Task 2: Mock Provider Implementations

**Files:**
- Create: `src/vulca/providers/mock.py`
- Test: `tests/test_providers.py` (append)

- [ ] **Step 1: Write failing test**

```python
# Append to tests/test_providers.py
import asyncio

class TestMockImageProvider:
    def test_generates_svg(self):
        from vulca.providers.mock import MockImageProvider
        p = MockImageProvider()
        result = asyncio.run(p.generate("test prompt", tradition="chinese_xieyi"))
        assert result.mime == "image/svg+xml"
        assert "svg" in result.image_b64  # base64 of SVG
        assert result.metadata is not None

class TestMockVLMProvider:
    def test_returns_scores(self):
        from vulca.providers.mock import MockVLMProvider
        p = MockVLMProvider()
        result = asyncio.run(p.score("base64data", tradition="chinese_xieyi"))
        assert 0 < result.L1 <= 1
        assert 0 < result.L5 <= 1
        assert result.rationales is not None
        assert "L1" in result.rationales
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/yhryzy/projects/website/vulca && .venv/bin/python -m pytest tests/test_providers.py::TestMockImageProvider -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'vulca.providers.mock'`

- [ ] **Step 3: Create mock providers**

Extract mock logic from `src/vulca/pipeline/nodes/generate.py:80-138` (SVG generation) and `src/vulca/_vlm.py` (mock scoring) into `src/vulca/providers/mock.py`.

```python
# src/vulca/providers/mock.py
"""Mock providers for testing without API keys."""
from __future__ import annotations

import base64
import hashlib

from vulca.providers.base import ImageProvider, ImageResult, L1L5Scores, VLMProvider

# Tradition → background color for mock SVG placeholders
_TRADITION_COLORS: dict[str, str] = {
    "chinese_xieyi": "#3a3a3a",
    "chinese_gongbi": "#c43f2f",
    "japanese_traditional": "#264653",
    "islamic_geometric": "#2a9d8f",
    "watercolor": "#89c2d9",
    "western_academic": "#8a5a44",
    "african_traditional": "#bc6c25",
    "south_asian": "#e9c46a",
}


class MockImageProvider:
    """Generates deterministic SVG placeholder images."""

    async def generate(
        self,
        prompt: str,
        *,
        tradition: str = "",
        subject: str = "",
        reference_image_b64: str = "",
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        **kwargs,
    ) -> ImageResult:
        cid = hashlib.md5(f"{prompt}{tradition}".encode()).hexdigest()[:12]
        bg = _TRADITION_COLORS.get(tradition, "#5F8A50")
        tradition_display = tradition.replace("_", " ").title() if tradition else "Default"
        subject_display = (subject or prompt)[:50]
        for old, new in [("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), ('"', "&quot;")]:
            subject_display = subject_display.replace(old, new)
            tradition_display = tradition_display.replace(old, new)

        svg = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
            f'<rect width="{width}" height="{height}" fill="{bg}" rx="24"/>'
            f'<text x="50%" y="40%" text-anchor="middle" fill="white" font-size="18" font-family="Inter, sans-serif">{tradition_display}</text>'
            f'<text x="50%" y="55%" text-anchor="middle" fill="rgba(255,255,255,0.7)" font-size="14" font-family="Inter, sans-serif">{subject_display}</text>'
            f'<text x="50%" y="85%" text-anchor="middle" fill="rgba(255,255,255,0.3)" font-size="10" font-family="monospace">mock://{cid}</text>'
            f'</svg>'
        )
        img_b64 = base64.b64encode(svg.encode()).decode()
        return ImageResult(
            image_b64=img_b64,
            mime="image/svg+xml",
            metadata={"candidate_id": cid, "image_url": f"mock://{cid}.svg"},
        )


class MockVLMProvider:
    """Returns deterministic scores based on tradition weights."""

    async def score(
        self,
        image_b64: str,
        *,
        tradition: str = "",
        subject: str = "",
        guidance: str = "",
        **kwargs,
    ) -> L1L5Scores:
        seed = hash(f"{image_b64[:20]}{tradition}") % 100
        base = 0.65 + (seed % 20) / 100
        scores = {
            "L1": round(min(base + 0.10, 1.0), 2),
            "L2": round(min(base + 0.05, 1.0), 2),
            "L3": round(min(base + 0.15, 1.0), 2),
            "L4": round(min(base + 0.08, 1.0), 2),
            "L5": round(min(base + 0.13, 1.0), 2),
        }
        rationales = {
            "L1": "Mock: Visual composition assessment.",
            "L2": "Mock: Technical execution assessment.",
            "L3": "Mock: Cultural context assessment.",
            "L4": "Mock: Critical interpretation assessment.",
            "L5": "Mock: Philosophical aesthetics assessment.",
        }
        return L1L5Scores(**scores, rationales=rationales)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/yhryzy/projects/website/vulca && .venv/bin/python -m pytest tests/test_providers.py -v`
Expected: PASS (8 tests)

- [ ] **Step 5: Commit**

```bash
cd /home/yhryzy/projects/website/vulca
git add src/vulca/providers/mock.py tests/test_providers.py
git commit -m "feat: add MockImageProvider + MockVLMProvider"
```

---

## Task 3: Gemini Image Provider

**Files:**
- Create: `src/vulca/providers/gemini.py`
- Test: `tests/test_providers.py` (append)

- [ ] **Step 1: Write failing test**

```python
# Append to tests/test_providers.py
class TestGeminiImageProvider:
    def test_instantiation(self):
        from vulca.providers.gemini import GeminiImageProvider
        p = GeminiImageProvider(api_key="test-key")
        assert isinstance(p, ImageProvider)

    def test_no_key_raises(self):
        """Without API key or env var, should raise on generate."""
        import os
        from vulca.providers.gemini import GeminiImageProvider
        old = os.environ.pop("GOOGLE_API_KEY", None)
        old2 = os.environ.pop("GEMINI_API_KEY", None)
        try:
            p = GeminiImageProvider()
            with pytest.raises(ValueError, match="API key"):
                asyncio.run(p.generate("test"))
        finally:
            if old: os.environ["GOOGLE_API_KEY"] = old
            if old2: os.environ["GEMINI_API_KEY"] = old2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/yhryzy/projects/website/vulca && .venv/bin/python -m pytest tests/test_providers.py::TestGeminiImageProvider -v`
Expected: FAIL

- [ ] **Step 3: Extract Gemini provider from generate.py**

Extract the `_gemini_generate` method from `src/vulca/pipeline/nodes/generate.py:140-424` into `src/vulca/providers/gemini.py`. Keep the same Gemini API logic but wrap it in the `ImageProvider` protocol.

Key code to extract:
- Gemini API call with `google.genai.Client`
- Prompt construction with tradition/subject/feedback
- Reference image multimodal input
- Response parsing (image bytes extraction)
- Timeout handling

```python
# src/vulca/providers/gemini.py
"""Gemini image generation provider."""
from __future__ import annotations

import base64
import os
import time

from vulca.providers.base import ImageProvider, ImageResult


class GeminiImageProvider:
    """Image generation via Google Gemini API."""

    def __init__(
        self,
        api_key: str = "",
        model: str = "gemini-2.0-flash-exp-image-generation",
        timeout: int = 90,
    ):
        self.api_key = (
            api_key
            or os.environ.get("GOOGLE_API_KEY", "")
            or os.environ.get("GEMINI_API_KEY", "")
        )
        self.model = model
        self.timeout = timeout

    async def generate(
        self,
        prompt: str,
        *,
        tradition: str = "",
        subject: str = "",
        reference_image_b64: str = "",
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        **kwargs,
    ) -> ImageResult:
        if not self.api_key:
            raise ValueError(
                "Gemini API key required. Set GOOGLE_API_KEY env var "
                "or pass api_key to GeminiImageProvider()."
            )

        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.api_key)

        # Build prompt with cultural context
        full_prompt = self._build_prompt(prompt, tradition, subject, kwargs)

        # Build contents (text + optional reference image)
        contents: list = []
        if reference_image_b64:
            contents.append(types.Part.from_bytes(
                data=base64.b64decode(reference_image_b64),
                mime_type="image/png",
            ))
        contents.append(full_prompt)

        config = types.GenerateContentConfig(
            response_modalities=["Text", "Image"],
        )

        # Call with timeout
        import asyncio
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    client.models.generate_content,
                    model=self.model,
                    contents=contents,
                    config=config,
                ),
                timeout=self.timeout,
            )
        except asyncio.TimeoutError:
            raise TimeoutError(f"Gemini image generation timed out after {self.timeout}s")

        # Extract image from response
        if response.candidates:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith("image/"):
                    img_b64 = base64.b64encode(part.inline_data.data).decode()
                    return ImageResult(
                        image_b64=img_b64,
                        mime=part.inline_data.mime_type,
                        metadata={"model": self.model},
                    )

        raise RuntimeError("Gemini returned no image data")

    def _build_prompt(self, prompt: str, tradition: str, subject: str, kwargs: dict) -> str:
        parts = [f"Generate an artwork: {prompt}"]
        if tradition and tradition != "default":
            parts.append(f"Cultural tradition: {tradition.replace('_', ' ')}")
        if subject:
            parts.append(f"Subject: {subject}")
        # Refinement feedback from previous round
        improvement_focus = kwargs.get("improvement_focus", "")
        if improvement_focus:
            parts.append(f"Improvement focus:\n{improvement_focus}")
        return "\n".join(parts)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/yhryzy/projects/website/vulca && .venv/bin/python -m pytest tests/test_providers.py::TestGeminiImageProvider -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /home/yhryzy/projects/website/vulca
git add src/vulca/providers/gemini.py tests/test_providers.py
git commit -m "feat: add GeminiImageProvider"
```

---

## Task 4: OpenAI + ComfyUI Image Providers

**Files:**
- Create: `src/vulca/providers/openai_provider.py`
- Create: `src/vulca/providers/comfyui.py`
- Test: `tests/test_providers.py` (append)

- [ ] **Step 1: Write failing tests**

```python
# Append to tests/test_providers.py
class TestOpenAIImageProvider:
    def test_instantiation(self):
        from vulca.providers.openai_provider import OpenAIImageProvider
        p = OpenAIImageProvider(api_key="test-key")
        assert isinstance(p, ImageProvider)

class TestComfyUIImageProvider:
    def test_instantiation(self):
        from vulca.providers.comfyui import ComfyUIImageProvider
        p = ComfyUIImageProvider(base_url="http://localhost:8188")
        assert isinstance(p, ImageProvider)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/yhryzy/projects/website/vulca && .venv/bin/python -m pytest tests/test_providers.py::TestOpenAIImageProvider tests/test_providers.py::TestComfyUIImageProvider -v`
Expected: FAIL

- [ ] **Step 3: Implement OpenAI provider**

```python
# src/vulca/providers/openai_provider.py
"""OpenAI DALL-E image generation provider."""
from __future__ import annotations

import base64
import os

from vulca.providers.base import ImageProvider, ImageResult


class OpenAIImageProvider:
    """Image generation via OpenAI DALL-E 3 API."""

    def __init__(self, api_key: str = "", model: str = "dall-e-3"):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.model = model

    async def generate(
        self,
        prompt: str,
        *,
        tradition: str = "",
        subject: str = "",
        reference_image_b64: str = "",
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        **kwargs,
    ) -> ImageResult:
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var "
                "or pass api_key to OpenAIImageProvider()."
            )

        import httpx

        full_prompt = prompt
        if tradition and tradition != "default":
            full_prompt = f"{prompt} (cultural tradition: {tradition.replace('_', ' ')})"

        size = f"{width}x{height}" if width == height else "1024x1024"

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                "https://api.openai.com/v1/images/generations",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "n": 1,
                    "size": size,
                    "response_format": "b64_json",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        img_b64 = data["data"][0]["b64_json"]
        return ImageResult(
            image_b64=img_b64,
            mime="image/png",
            metadata={"model": self.model, "revised_prompt": data["data"][0].get("revised_prompt", "")},
        )
```

- [ ] **Step 4: Implement ComfyUI provider**

```python
# src/vulca/providers/comfyui.py
"""ComfyUI local image generation provider."""
from __future__ import annotations

import base64
import os

from vulca.providers.base import ImageProvider, ImageResult


class ComfyUIImageProvider:
    """Image generation via ComfyUI REST API (local deployment)."""

    def __init__(self, base_url: str = ""):
        self.base_url = (
            base_url
            or os.environ.get("VULCA_IMAGE_BASE_URL", "http://localhost:8188")
        )

    async def generate(
        self,
        prompt: str,
        *,
        tradition: str = "",
        subject: str = "",
        reference_image_b64: str = "",
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        **kwargs,
    ) -> ImageResult:
        import httpx

        full_prompt = prompt
        if tradition and tradition != "default":
            full_prompt = f"{prompt}, {tradition.replace('_', ' ')} style"

        # Minimal txt2img workflow for ComfyUI API
        workflow = {
            "prompt": {
                "3": {
                    "class_type": "KSampler",
                    "inputs": {"seed": 42, "steps": 20, "cfg": 7.0, "sampler_name": "euler",
                               "scheduler": "normal", "denoise": 1.0,
                               "model": ["4", 0], "positive": ["6", 0],
                               "negative": ["7", 0], "latent_image": ["5", 0]},
                },
                "4": {"class_type": "CheckpointLoaderSimple",
                      "inputs": {"ckpt_name": kwargs.get("checkpoint", "sd_xl_base_1.0.safetensors")}},
                "5": {"class_type": "EmptyLatentImage",
                      "inputs": {"width": width, "height": height, "batch_size": 1}},
                "6": {"class_type": "CLIPTextEncode",
                      "inputs": {"text": full_prompt, "clip": ["4", 1]}},
                "7": {"class_type": "CLIPTextEncode",
                      "inputs": {"text": negative_prompt or "", "clip": ["4", 1]}},
                "8": {"class_type": "VAEDecode",
                      "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
                "9": {"class_type": "SaveImage",
                      "inputs": {"filename_prefix": "vulca", "images": ["8", 0]}},
            }
        }

        async with httpx.AsyncClient(timeout=300) as client:
            # Queue prompt
            resp = await client.post(f"{self.base_url}/prompt", json=workflow)
            resp.raise_for_status()
            prompt_id = resp.json()["prompt_id"]

            # Poll for completion
            import asyncio
            for _ in range(60):
                hist = await client.get(f"{self.base_url}/history/{prompt_id}")
                if hist.status_code == 200:
                    data = hist.json()
                    if prompt_id in data:
                        outputs = data[prompt_id].get("outputs", {})
                        for node_out in outputs.values():
                            for img in node_out.get("images", []):
                                img_resp = await client.get(
                                    f"{self.base_url}/view",
                                    params={"filename": img["filename"], "subfolder": img.get("subfolder", ""), "type": img.get("type", "output")},
                                )
                                img_b64 = base64.b64encode(img_resp.content).decode()
                                return ImageResult(image_b64=img_b64, mime="image/png",
                                                   metadata={"prompt_id": prompt_id})
                await asyncio.sleep(5)

            raise TimeoutError("ComfyUI generation timed out after 5 minutes")
```

- [ ] **Step 5: Run tests and commit**

Run: `cd /home/yhryzy/projects/website/vulca && .venv/bin/python -m pytest tests/test_providers.py -v`
Expected: PASS

```bash
cd /home/yhryzy/projects/website/vulca
git add src/vulca/providers/openai_provider.py src/vulca/providers/comfyui.py tests/test_providers.py
git commit -m "feat: add OpenAI + ComfyUI image providers"
```

---

## Task 5: LiteLLM VLM Provider

**Files:**
- Create: `src/vulca/providers/vlm_litellm.py`
- Test: `tests/test_providers.py` (append)

- [ ] **Step 1: Write failing test**

```python
# Append to tests/test_providers.py
class TestLiteLLMVLMProvider:
    def test_instantiation(self):
        from vulca.providers.vlm_litellm import LiteLLMVLMProvider
        p = LiteLLMVLMProvider(model="gemini/gemini-2.5-flash")
        assert isinstance(p, VLMProvider)
```

- [ ] **Step 2: Run test to verify it fails**

- [ ] **Step 3: Extract VLM scoring logic from `_vlm.py` into provider**

Extract `score_image()` from `src/vulca/_vlm.py:196-250` into `src/vulca/providers/vlm_litellm.py`. Keep the prompt construction logic (tradition guidance, few-shot, evolved weights) in `_vlm.py` as a prompt builder, but make the actual LLM call go through the provider.

```python
# src/vulca/providers/vlm_litellm.py
"""LiteLLM-based VLM scoring provider."""
from __future__ import annotations

import json
import os
import re

from vulca.providers.base import L1L5Scores, VLMProvider


class LiteLLMVLMProvider:
    """VLM scoring via any LiteLLM-supported model."""

    def __init__(self, model: str = "", api_key: str = ""):
        self.model = model or os.environ.get("VULCA_VLM_MODEL", "gemini/gemini-2.5-flash")
        self.api_key = api_key

    async def score(
        self,
        image_b64: str,
        *,
        tradition: str = "",
        subject: str = "",
        guidance: str = "",
        **kwargs,
    ) -> L1L5Scores:
        import litellm

        prompt = guidance or self._default_prompt(tradition, subject)

        messages = [
            {"role": "system", "content": "You are VULCA, an AI art critic. Score the image on L1-L5 dimensions. Return JSON only."},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
                {"type": "text", "text": prompt},
            ]},
        ]

        call_kwargs = {"model": self.model, "messages": messages, "temperature": 0.3, "max_tokens": 2000}
        if self.api_key:
            call_kwargs["api_key"] = self.api_key

        response = await litellm.acompletion(**call_kwargs)
        text = response.choices[0].message.content or ""
        return self._parse_response(text)

    def _default_prompt(self, tradition: str, subject: str) -> str:
        parts = ["Score this image on five dimensions (0.0-1.0). Return JSON with keys L1-L5 and L1_rationale through L5_rationale."]
        if tradition:
            parts.append(f"Cultural tradition: {tradition}")
        if subject:
            parts.append(f"Subject: {subject}")
        return "\n".join(parts)

    def _parse_response(self, text: str) -> L1L5Scores:
        # Extract JSON from response
        json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if not json_match:
            raise ValueError(f"No JSON found in VLM response: {text[:200]}")
        data = json.loads(json_match.group())

        scores = {}
        rationales = {}
        for level in ("L1", "L2", "L3", "L4", "L5"):
            scores[level] = float(data.get(level, 0.5))
            rationales[level] = data.get(f"{level}_rationale", "")

        return L1L5Scores(**scores, rationales=rationales)
```

- [ ] **Step 4: Run test and commit**

```bash
cd /home/yhryzy/projects/website/vulca
git add src/vulca/providers/vlm_litellm.py tests/test_providers.py
git commit -m "feat: add LiteLLMVLMProvider"
```

---

## Task 6: Update providers/__init__.py with Registry

**Files:**
- Modify: `src/vulca/providers/__init__.py`

- [ ] **Step 1: Add provider registry**

```python
# src/vulca/providers/__init__.py
"""Pluggable provider interfaces for image generation and VLM scoring."""
from vulca.providers.base import ImageProvider, ImageResult, L1L5Scores, VLMProvider

_IMAGE_PROVIDERS: dict[str, type] = {}
_VLM_PROVIDERS: dict[str, type] = {}


def _lazy_load_providers():
    global _IMAGE_PROVIDERS, _VLM_PROVIDERS
    if _IMAGE_PROVIDERS:
        return
    from vulca.providers.mock import MockImageProvider, MockVLMProvider
    _IMAGE_PROVIDERS["mock"] = MockImageProvider
    _VLM_PROVIDERS["mock"] = MockVLMProvider
    try:
        from vulca.providers.gemini import GeminiImageProvider
        _IMAGE_PROVIDERS["gemini"] = GeminiImageProvider
        _IMAGE_PROVIDERS["nb2"] = GeminiImageProvider  # alias
    except ImportError:
        pass
    try:
        from vulca.providers.openai_provider import OpenAIImageProvider
        _IMAGE_PROVIDERS["openai"] = OpenAIImageProvider
    except ImportError:
        pass
    try:
        from vulca.providers.comfyui import ComfyUIImageProvider
        _IMAGE_PROVIDERS["comfyui"] = ComfyUIImageProvider
    except ImportError:
        pass
    try:
        from vulca.providers.vlm_litellm import LiteLLMVLMProvider
        _VLM_PROVIDERS["litellm"] = LiteLLMVLMProvider
    except ImportError:
        pass


def get_image_provider(name: str, **kwargs) -> ImageProvider:
    """Get an image provider by name."""
    _lazy_load_providers()
    cls = _IMAGE_PROVIDERS.get(name)
    if cls is None:
        raise ValueError(f"Unknown image provider: {name!r}. Available: {list(_IMAGE_PROVIDERS.keys())}")
    return cls(**kwargs)


def get_vlm_provider(name: str, **kwargs) -> VLMProvider:
    """Get a VLM provider by name."""
    _lazy_load_providers()
    cls = _VLM_PROVIDERS.get(name)
    if cls is None:
        raise ValueError(f"Unknown VLM provider: {name!r}. Available: {list(_VLM_PROVIDERS.keys())}")
    return cls(**kwargs)


__all__ = [
    "ImageProvider", "VLMProvider", "ImageResult", "L1L5Scores",
    "get_image_provider", "get_vlm_provider",
]
```

- [ ] **Step 2: Test and commit**

```bash
cd /home/yhryzy/projects/website/vulca && .venv/bin/python -c "
from vulca.providers import get_image_provider, get_vlm_provider
p = get_image_provider('mock')
print(f'Mock image: {type(p).__name__}')
v = get_vlm_provider('mock')
print(f'Mock VLM: {type(v).__name__}')
"
git add src/vulca/providers/__init__.py
git commit -m "feat: add provider registry with get_image_provider/get_vlm_provider"
```

---

## Task 7: Cultural Loader — get_tradition_guide()

**Files:**
- Modify: `src/vulca/cultural/loader.py`
- Test: `tests/test_providers.py` (or new file)

- [ ] **Step 1: Write failing test**

```python
# Append to tests/test_providers.py
class TestTraditionGuide:
    def test_returns_guide(self):
        from vulca.cultural.loader import get_tradition_guide
        guide = get_tradition_guide("chinese_xieyi")
        assert guide is not None
        assert guide["tradition"] == "chinese_xieyi"
        assert "weights" in guide
        assert "terminology" in guide
        assert "taboos" in guide
        assert len(guide["terminology"]) > 0

    def test_unknown_tradition(self):
        from vulca.cultural.loader import get_tradition_guide
        guide = get_tradition_guide("nonexistent")
        assert guide is None
```

- [ ] **Step 2: Implement get_tradition_guide()**

Add to `src/vulca/cultural/loader.py` after `get_all_weight_tables()`:

```python
def get_tradition_guide(tradition: str) -> dict | None:
    """Get full cultural guide for a tradition (for MCP/CLI).

    Returns dict with weights, evolved_weights, terminology, taboos, description.
    Returns None if tradition not found.
    """
    _ensure_loaded()
    tc = _traditions.get(tradition)
    if tc is None:
        return None

    evolved = _load_evolved_weights(tradition)

    # Count sessions from evolved context
    sessions_count = 0
    try:
        import json
        loader_path = Path(__file__).resolve()
        candidates = [
            loader_path.parent.parent.parent.parent.parent / "wenxin-backend" / "app" / "prototype" / "data" / "evolved_context.json",
        ]
        env_path = os.environ.get("VULCA_EVOLVED_CONTEXT")
        if env_path:
            candidates.insert(0, Path(env_path))
        for path in candidates:
            if path.is_file():
                with open(path, "r", encoding="utf-8") as f:
                    ctx = json.load(f)
                sessions_count = ctx.get("total_sessions", 0)
                break
    except Exception:
        pass

    # Build terminology list
    terms = []
    for t in tc.terminology:
        entry = {"term": t.term, "definition": t.definition}
        if t.term_zh:
            entry["translation"] = t.term_zh
        terms.append(entry)

    # Build taboos list
    taboos = [tb.rule for tb in tc.taboos if tb.rule]

    # Description from display name or generated
    desc = tc.display_name.get("en", tradition.replace("_", " ").title())

    # Emphasis (highest weighted dimension)
    dim_names = {"L1": "Visual", "L2": "Technical", "L3": "Cultural", "L4": "Critical", "L5": "Philosophical"}
    emphasis_dim = max(tc.weights_l, key=tc.weights_l.get) if tc.weights_l else "L3"
    emphasis = dim_names.get(emphasis_dim, emphasis_dim)

    return {
        "tradition": tradition,
        "description": desc,
        "emphasis": emphasis,
        "weights": dict(tc.weights_l),
        "evolved_weights": evolved,
        "sessions_count": sessions_count,
        "terminology": terms,
        "taboos": taboos,
    }
```

- [ ] **Step 3: Run test and commit**

```bash
cd /home/yhryzy/projects/website/vulca && .venv/bin/python -m pytest tests/test_providers.py::TestTraditionGuide -v
git add src/vulca/cultural/loader.py tests/test_providers.py
git commit -m "feat: add get_tradition_guide() for MCP/CLI"
```

---

## Task 8: MCP Server Rewrite (6 Tools)

**Files:**
- Rewrite: `src/vulca/mcp_server.py`
- Create: `tests/test_mcp_v2.py`

- [ ] **Step 1: Write failing tests for all 6 tools**

```python
# tests/test_mcp_v2.py
"""Tests for VULCA MCP Server v2 — 6 tools with view/format params."""
import asyncio
import pytest
from vulca.mcp_server import (
    create_artwork, evaluate_artwork, list_traditions,
    get_tradition_guide, resume_artwork, get_evolution_status,
)


class TestCreateArtwork:
    def test_summary_json(self):
        r = asyncio.run(create_artwork("test", provider="mock"))
        assert "session_id" in r
        assert "best_image_url" in r
        assert "weighted_total" in r
        assert "rationales" not in r  # summary excludes rationales

    def test_detailed_json(self):
        r = asyncio.run(create_artwork("test", provider="mock", view="detailed"))
        assert "rationales" in r
        assert "rounds" in r
        assert "scores" in r
        assert "best_image_url" in r

    def test_markdown_format(self):
        r = asyncio.run(create_artwork("test", provider="mock", view="detailed", format="markdown"))
        assert isinstance(r, str)
        assert "Weighted Total" in r or "weighted_total" in r.lower()

    def test_hitl_returns_session(self):
        r = asyncio.run(create_artwork("test", provider="mock", hitl=True))
        assert r["status"] == "waiting_human"
        assert r["session_id"]


class TestEvaluateArtwork:
    def test_summary_json(self):
        r = asyncio.run(evaluate_artwork("/dev/null", mock=True))
        assert "score" in r
        assert "tradition" in r

    def test_detailed_json(self):
        r = asyncio.run(evaluate_artwork("/dev/null", mock=True, view="detailed"))
        assert "rationales" in r
        assert "recommendations" in r


class TestListTraditions:
    def test_json(self):
        r = asyncio.run(list_traditions())
        assert "traditions" in r
        assert "chinese_xieyi" in r["traditions"]
        # Each tradition should have emphasis
        xieyi = r["traditions"]["chinese_xieyi"]
        assert "emphasis" in xieyi


class TestGetTraditionGuide:
    def test_returns_guide(self):
        r = asyncio.run(get_tradition_guide("chinese_xieyi"))
        assert r["tradition"] == "chinese_xieyi"
        assert "terminology" in r
        assert "taboos" in r
        assert "weights" in r

    def test_unknown_returns_error(self):
        r = asyncio.run(get_tradition_guide("nonexistent"))
        assert "error" in r


class TestGetEvolutionStatus:
    def test_returns_status(self):
        r = asyncio.run(get_evolution_status("chinese_xieyi"))
        assert "original_weights" in r
        assert "tradition" in r


class TestResumeArtwork:
    def test_accept(self):
        # Create HITL run first
        create_r = asyncio.run(create_artwork("test", provider="mock", hitl=True))
        session_id = create_r["session_id"]
        # Resume with accept
        r = asyncio.run(resume_artwork(session_id, "accept"))
        assert r["status"] in ("completed", "accepted")

    def test_invalid_session(self):
        r = asyncio.run(resume_artwork("nonexistent", "accept"))
        assert "error" in r
```

- [ ] **Step 2: Rewrite mcp_server.py with 6 tools**

Full rewrite of `src/vulca/mcp_server.py` (~250 lines). Key changes:
- All tools get `view` + `format` params
- `create_artwork` returns `best_image_url`, `rationales`, `rounds`
- `evaluate_artwork` returns `rationales`, `recommendations`
- `list_traditions` returns `emphasis` + `description` per tradition
- New: `get_tradition_guide`, `resume_artwork`, `get_evolution_status`
- `_format_markdown()` helper for markdown output
- `resume_artwork` creates a new pipeline run with feedback (same pattern as Canvas HITL rerun)

- [ ] **Step 3: Run tests and commit**

Run: `cd /home/yhryzy/projects/website/vulca && .venv/bin/python -m pytest tests/test_mcp_v2.py -v`
Expected: PASS

```bash
cd /home/yhryzy/projects/website/vulca
git add src/vulca/mcp_server.py tests/test_mcp_v2.py
git commit -m "feat: MCP server v2 — 6 tools with view/format params"
```

---

## Task 9: CLI Updates

**Files:**
- Modify: `src/vulca/cli.py`

- [ ] **Step 1: Add `tradition` and `evolution` subcommands**

Add to `src/vulca/cli.py` after the `traditions` subparser:

```python
# tradition detail command
trad_p = sub.add_parser("tradition", aliases=["td"], help="Get cultural tradition guide")
trad_p.add_argument("name", help="Tradition name (e.g. chinese_xieyi)")
trad_p.add_argument("--json", action="store_true", help="Output raw JSON")

# evolution status command
evo_p = sub.add_parser("evolution", aliases=["evo"], help="Get evolution status for a tradition")
evo_p.add_argument("name", help="Tradition name")
evo_p.add_argument("--json", action="store_true", help="Output raw JSON")
```

Add handler functions `_cmd_tradition(args)` and `_cmd_evolution(args)`.

- [ ] **Step 2: Add `--image-provider` and `--vlm-model` flags to create/evaluate**

Add to create subparser:
```python
create_p.add_argument("--image-provider", default="", help="Image provider: mock|gemini|openai|comfyui")
create_p.add_argument("--image-base-url", default="", help="Image provider base URL (for comfyui)")
```

Add to evaluate subparser:
```python
eval_p.add_argument("--vlm-model", default="", help="VLM model (LiteLLM format, e.g. ollama/llava)")
eval_p.add_argument("--vlm-base-url", default="", help="VLM base URL (for local models)")
```

- [ ] **Step 3: Test CLI manually and commit**

```bash
cd /home/yhryzy/projects/website/vulca
.venv/bin/vulca tradition chinese_xieyi
.venv/bin/vulca evolution chinese_xieyi
.venv/bin/vulca create "test" --provider mock --image-provider mock
git add src/vulca/cli.py
git commit -m "feat: CLI — add tradition/evolution commands + provider flags"
```

---

## Task 10: SDK Updates (create.py + evaluate.py)

**Files:**
- Modify: `src/vulca/create.py`
- Modify: `src/vulca/evaluate.py`

- [ ] **Step 1: Add provider params to create()**

Add `image_provider` and `vlm_provider` optional params to `acreate()` and `create()`. Pass through to pipeline engine via node_params or direct provider injection.

- [ ] **Step 2: Add vlm_provider param to evaluate()**

Add `vlm_provider` optional param to `aevaluate()` and `evaluate()`. Pass to Engine.

- [ ] **Step 3: Test and commit**

```bash
cd /home/yhryzy/projects/website/vulca
.venv/bin/python -c "
from vulca.providers.mock import MockImageProvider
import vulca
r = vulca.create('test', provider='mock')
print(f'Create: {r.status}')
"
git add src/vulca/create.py src/vulca/evaluate.py
git commit -m "feat: SDK — add image_provider + vlm_provider params"
```

---

## Task 11: Integration Test + Full Suite

**Files:**
- Run all tests

- [ ] **Step 1: Run full test suite**

```bash
cd /home/yhryzy/projects/website/vulca && .venv/bin/python -m pytest tests/ -v
```

Expected: 231+ existing tests PASS + ~20 new tests PASS

- [ ] **Step 2: Manual CLI integration test**

```bash
.venv/bin/vulca --version
.venv/bin/vulca traditions
.venv/bin/vulca tradition chinese_xieyi
.venv/bin/vulca evolution chinese_xieyi
.venv/bin/vulca evaluate /dev/null --mock --json
.venv/bin/vulca create "水墨山水" --provider mock --json
```

- [ ] **Step 3: Manual MCP integration test**

```bash
.venv/bin/python -c "
import asyncio
from vulca.mcp_server import create_artwork, evaluate_artwork, list_traditions, get_tradition_guide, get_evolution_status

async def test():
    print('1:', await list_traditions())
    print('2:', await get_tradition_guide('chinese_xieyi'))
    print('3:', await create_artwork('test', provider='mock', view='detailed'))
    print('4:', await evaluate_artwork('/dev/null', mock=True, view='detailed'))
    print('5:', await get_evolution_status('chinese_xieyi'))

asyncio.run(test())
"
```

- [ ] **Step 4: Rebuild package**

```bash
cd /home/yhryzy/projects/website/vulca
rm -rf dist/ && .venv/bin/python -m build
.venv/bin/twine check dist/*
```

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "feat: VULCA v0.3.0 — 6 MCP tools + Provider Protocol + CLI updates"
```
