"""v0.20.1 — wire-level invocation contract tests for layers_redraw.

Reviewer round-4 process audit (2026-04-27) found that 4 review rounds
shipped a CHANGELOG that claimed "gpt-image-2 high" while the actual
HTTP request to OpenAI used gpt-image-1 default. The bug-shape:
    spec/CHANGELOG → soft prose claim
    unit tests → assert pixel/topology outcomes
    real-provider tests → assert hue/saturation, NOT invocation contract

Recovery: assert what's literally on the wire. This file is the
wire-contract guard. Any future param-drift bug in this category
(model / quality / input_fidelity / output_format) breaks here loudly.
"""
from __future__ import annotations

import asyncio
import base64
import io
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PIL import Image

from vulca.layers.manifest import write_manifest
from vulca.layers.types import LayerInfo


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _png_bytes(size=(1024, 1024), color=(255, 255, 255)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return buf.getvalue()


class _RecordingHTTPClient:
    """Async-context wrapper that records POST args + returns canned PNG."""

    CALLS: list[dict] = []

    def __init__(self, *args, **kwargs):
        pass

    @classmethod
    def reset(cls):
        cls.CALLS = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return None

    async def post(self, url, headers=None, files=None, data=None, json=None):
        _RecordingHTTPClient.CALLS.append(
            {
                "url": url,
                "data": dict(data) if data else None,
                "files_keys": list(files.keys()) if files else None,
                "json": json,
            }
        )
        png_b64 = base64.b64encode(_png_bytes()).decode()
        resp = MagicMock()
        resp.status_code = 200
        resp.text = ""
        resp.json = MagicMock(
            return_value={
                "data": [{"b64_json": png_b64}],
                "usage": {"input_tokens": 1, "output_tokens": 1},
            }
        )
        resp.raise_for_status = MagicMock(return_value=None)
        return resp


def _setup_layer(tmp_path: Path, canvas_size=(256, 256), sparse_pct=0.18):
    w, h = canvas_size
    alpha = Image.new("L", canvas_size, 0)
    alpha.paste(
        Image.new("L", (int(w * sparse_pct), int(h * sparse_pct)), 255),
        (int(w * 0.4), int(h * 0.4)),
    )
    rgb = Image.new("RGB", canvas_size, (180, 64, 32))
    rgba = Image.merge("RGBA", (*rgb.split(), alpha))
    rgba.save(str(tmp_path / "fg.png"))
    Image.new("RGB", canvas_size, (100, 100, 100)).save(str(tmp_path / "source.png"))
    fg = LayerInfo(
        name="fg", description="foreground subject",
        z_index=1, content_type="subject",
    )
    write_manifest(
        [fg],
        output_dir=str(tmp_path),
        width=w, height=h,
        source_image="source.png",
    )


@pytest.fixture(autouse=True)
def _stub_openai_key(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake-for-wire-contract-check")


@pytest.fixture(autouse=True)
def _replace_httpx_async_client(monkeypatch):
    import httpx

    _RecordingHTTPClient.reset()
    monkeypatch.setattr(httpx, "AsyncClient", _RecordingHTTPClient)


class TestInpaintWireContract:
    def test_model_kwarg_reaches_wire_form_data(self, tmp_path):
        """SAFEGUARD #1 — pins the v0.20 PR audit finding.

        Without this assertion, layers_redraw silently defaults to
        gpt-image-1 even when caller passes model="gpt-image-2".
        """
        from vulca.layers import redraw as redraw_module
        from vulca.layers.manifest import load_manifest

        _setup_layer(tmp_path)
        artwork = load_manifest(str(tmp_path))

        _run(
            redraw_module.redraw_layer(
                artwork, layer_name="fg", instruction="cartoon",
                provider="openai", artwork_dir=str(tmp_path),
                route="inpaint",
                model="gpt-image-2", quality="high",
            )
        )

        edits = [c for c in _RecordingHTTPClient.CALLS if "edits" in c["url"]]
        assert edits, f"expected /v1/images/edits POST; recorded={_RecordingHTTPClient.CALLS}"
        form = edits[0]["data"]
        assert form, f"empty form-data; full call: {edits[0]}"
        assert form.get("model") == "gpt-image-2", (
            f"WIRE-CONTRACT VIOLATION: form['model']={form.get('model')!r}; "
            f"expected 'gpt-image-2'. This is the bug-shape v0.20 PR audit "
            f"surfaced. Full form: {form}"
        )
        assert form.get("quality") == "high", (
            f"quality not plumbed; form.quality={form.get('quality')!r}; full: {form}"
        )

    def test_default_model_unchanged_when_kwarg_omitted(self, tmp_path):
        """Backwards-compat: omit model → provider default lands on wire."""
        from vulca.layers import redraw as redraw_module
        from vulca.layers.manifest import load_manifest

        _setup_layer(tmp_path)
        artwork = load_manifest(str(tmp_path))

        _run(
            redraw_module.redraw_layer(
                artwork, layer_name="fg", instruction="cartoon",
                provider="openai", artwork_dir=str(tmp_path),
                route="inpaint",
            )
        )

        edits = [c for c in _RecordingHTTPClient.CALLS if "edits" in c["url"]]
        assert edits
        form = edits[0]["data"]
        # Provider default is gpt-image-1 (openai_provider.py:147). If the
        # default flips, this assertion documents the change.
        assert form.get("model") == "gpt-image-1", (
            f"unexpected default; form.model={form.get('model')!r}"
        )


class TestImg2ImgWireContract:
    def test_model_kwarg_reaches_wire_on_img2img_path(self, tmp_path):
        from vulca.layers import redraw as redraw_module
        from vulca.layers.manifest import load_manifest

        _setup_layer(tmp_path)
        artwork = load_manifest(str(tmp_path))

        _run(
            redraw_module.redraw_layer(
                artwork, layer_name="fg", instruction="cartoon",
                provider="openai", artwork_dir=str(tmp_path),
                route="img2img",
                model="gpt-image-2", quality="high",
            )
        )

        edits = [c for c in _RecordingHTTPClient.CALLS if "edits" in c["url"]]
        assert edits
        form = edits[0]["data"]
        assert form.get("model") == "gpt-image-2", (
            f"img2img wire violation: form.model={form.get('model')!r}; full: {form}"
        )
        assert form.get("quality") == "high", (
            f"img2img quality drop: form.quality={form.get('quality')!r}; full: {form}"
        )


class TestUnsupportedParamsAreSilentlyDropped:
    """Verify _drop_unsupported_params hides model-incompatible knobs."""

    def test_input_fidelity_dropped_for_gpt_image_2(self, tmp_path):
        """gpt-image-2 capability table marks input_fidelity=False;
        param must be silently dropped at the wire (not 400 from OpenAI)."""
        from vulca.layers import redraw as redraw_module
        from vulca.layers.manifest import load_manifest

        _setup_layer(tmp_path)
        artwork = load_manifest(str(tmp_path))

        _run(
            redraw_module.redraw_layer(
                artwork, layer_name="fg", instruction="cartoon",
                provider="openai", artwork_dir=str(tmp_path),
                route="inpaint",
                model="gpt-image-2",
                input_fidelity="high",
            )
        )

        edits = [c for c in _RecordingHTTPClient.CALLS if "edits" in c["url"]]
        form = edits[0]["data"]
        assert "input_fidelity" not in form, (
            f"input_fidelity leaked to wire for gpt-image-2; full: {form}"
        )

    def test_input_fidelity_kept_for_gpt_image_1_5(self, tmp_path):
        from vulca.layers import redraw as redraw_module
        from vulca.layers.manifest import load_manifest

        _setup_layer(tmp_path)
        artwork = load_manifest(str(tmp_path))

        _run(
            redraw_module.redraw_layer(
                artwork, layer_name="fg", instruction="cartoon",
                provider="openai", artwork_dir=str(tmp_path),
                route="inpaint",
                model="gpt-image-1.5",
                input_fidelity="high",
            )
        )

        edits = [c for c in _RecordingHTTPClient.CALLS if "edits" in c["url"]]
        form = edits[0]["data"]
        assert form.get("input_fidelity") == "high", (
            f"input_fidelity should be kept for gpt-image-1.5; full: {form}"
        )
