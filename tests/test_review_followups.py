"""Tests for the review-driven fixes in cli.py, layers/analyze.py,
providers/comfyui.py, providers/openai_provider.py, studio/phases/inpaint.py."""
from __future__ import annotations

import base64
import json
import os
from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest


# --- cli: --select validation + --provider choices ------------------------

def test_cli_inpaint_select_zero_is_rejected(capsys):
    """--select 0 must be rejected (1-based index)."""
    from vulca.cli import main

    with pytest.raises(SystemExit) as excinfo:
        main(["inpaint", "nonexistent.png",
              "--region", "0,0,50,50",
              "--instruction", "x",
              "--select", "0"])
    assert excinfo.value.code == 1
    assert "--select must be >= 1" in capsys.readouterr().err


def test_cli_inpaint_rejects_unknown_provider(capsys):
    """--provider choices are constrained by argparse."""
    from vulca.cli import main

    with pytest.raises(SystemExit):
        main(["inpaint", "nonexistent.png",
              "--region", "0,0,50,50",
              "--instruction", "x",
              "--provider", "bogus"])
    assert "invalid choice" in capsys.readouterr().err.lower()


# --- analyze.py: Ollama vs cloud wiring ----------------------------------

def _vlm_response(content: str) -> MagicMock:
    resp = MagicMock()
    resp.choices = [MagicMock()]
    resp.choices[0].message.content = content
    return resp


_LAYERS_JSON = json.dumps({"layers": [
    {"id": "L1", "name": "sky", "content_type": "background",
     "dominant_colors": ["#88aaff"], "regeneration_prompt": "blue sky"},
]})


async def _fake_load(_path):
    return ("AAAA", "image/png")


async def test_analyze_layers_passes_api_base_for_ollama():
    """analyze_layers() injects api_base + 300s timeout for Ollama and blanks api_key."""
    from vulca.layers import analyze as analyze_mod

    with patch.dict(os.environ, {
        "VULCA_VLM_MODEL": "ollama_chat/gemma3",
        "OLLAMA_API_BASE": "http://localhost:11434",
        "GOOGLE_API_KEY": "should-not-leak",
    }):
        with patch.object(analyze_mod.litellm, "acompletion",
                          new=AsyncMock(return_value=_vlm_response(_LAYERS_JSON))) as mock_call, \
             patch("vulca._image.load_image_base64", new=_fake_load):
            await analyze_mod.analyze_layers("dummy.png")
            call_kwargs = mock_call.call_args.kwargs
            assert call_kwargs.get("api_base") == "http://localhost:11434"
            assert call_kwargs.get("timeout") == 300
            assert call_kwargs.get("api_key") == ""


async def test_analyze_layers_no_api_base_for_cloud():
    """Cloud models: no api_base, 55s timeout, caller's api_key passes through."""
    from vulca.layers import analyze as analyze_mod

    with patch.dict(os.environ, {"VULCA_VLM_MODEL": "gemini/gemini-2.5-flash"}):
        with patch.object(analyze_mod.litellm, "acompletion",
                          new=AsyncMock(return_value=_vlm_response(_LAYERS_JSON))) as mock_call, \
             patch("vulca._image.load_image_base64", new=_fake_load):
            await analyze_mod.analyze_layers("dummy.png", api_key="fake")
            call_kwargs = mock_call.call_args.kwargs
            assert "api_base" not in call_kwargs
            assert call_kwargs.get("timeout") == 55
            assert call_kwargs.get("api_key") == "fake"


# --- ComfyUI: shared transport fixture ------------------------------------

@contextmanager
def _httpx_with_handler(handler, target: str = "httpx.AsyncClient"):
    """Route a module's httpx.AsyncClient through a MockTransport."""
    transport = httpx.MockTransport(handler)
    original = httpx.AsyncClient

    def factory(*args, **kwargs):
        kwargs["transport"] = transport
        return original(*args, **kwargs)

    with patch(target, side_effect=factory):
        yield


def _comfyui_with_handler(handler):
    return _httpx_with_handler(handler, "vulca.providers.comfyui.httpx.AsyncClient")


def _png_bytes(size: int = 2000) -> bytes:
    return b'\x89PNG\r\n\x1a\n' + (b'A' * (size - 8))


def _comfy_handler(pid: str, status: dict, *,
                   images: list[dict] | None = None,
                   view_bytes: bytes | None = None):
    """Build a ComfyUI /prompt + /history + /view mock handler."""
    def _handle(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/prompt":
            return httpx.Response(200, json={"prompt_id": pid})
        if request.url.path == f"/history/{pid}":
            outputs = {"9": {"images": images}} if images else {}
            return httpx.Response(200, json={pid: {"status": status, "outputs": outputs}})
        if request.url.path == "/view" and view_bytes is not None:
            return httpx.Response(200, content=view_bytes)
        return httpx.Response(404)
    return _handle


async def test_comfyui_raises_on_error_status():
    from vulca.providers.comfyui import ComfyUIImageProvider

    handler = _comfy_handler(
        "pid-err",
        {"status_str": "error", "completed": False,
         "messages": [["execution_error", {"node": "3"}]]},
    )
    with _comfyui_with_handler(handler):
        with pytest.raises(RuntimeError, match="ComfyUI execution failed"):
            await ComfyUIImageProvider(base_url="http://fake").generate(
                "test", width=64, height=64,
            )


async def test_comfyui_rejects_invalid_image_bytes():
    from vulca.providers.comfyui import ComfyUIImageProvider

    handler = _comfy_handler(
        "pid-bad",
        {"status_str": "success", "completed": True, "messages": []},
        images=[{"filename": "x.png", "subfolder": "", "type": "output"}],
        view_bytes=b"NOT-A-PNG",
    )
    with _comfyui_with_handler(handler):
        with pytest.raises(ValueError, match="invalid image"):
            await ComfyUIImageProvider(base_url="http://fake").generate(
                "test", width=64, height=64,
            )


async def test_comfyui_queued_prompt_not_in_history_does_not_trip_cap(monkeypatch):
    """ComfyUI returns {} until the job is queued into history; this MUST NOT count as failure."""
    from vulca.providers import comfyui as comfyui_mod
    from vulca.providers.comfyui import ComfyUIImageProvider

    monkeypatch.setattr(comfyui_mod, "_POLL_INTERVAL", 0)
    monkeypatch.setattr(comfyui_mod, "_MAX_CONSECUTIVE_POLL_FAILURES", 3)

    png = _png_bytes()
    hist_calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/prompt":
            return httpx.Response(200, json={"prompt_id": "pid-queued"})
        if request.url.path == "/history/pid-queued":
            hist_calls["n"] += 1
            if hist_calls["n"] <= 5:
                # Five polls with the prompt_id missing from the response — would
                # trip the 3-strike cap if this case were mis-classified as a failure.
                return httpx.Response(200, json={})
            return httpx.Response(200, json={"pid-queued": {
                "status": {"status_str": "success", "completed": True, "messages": []},
                "outputs": {"9": {"images": [
                    {"filename": "x.png", "subfolder": "", "type": "output"},
                ]}},
            }})
        if request.url.path == "/view":
            return httpx.Response(200, content=png)
        return httpx.Response(404)

    with _comfyui_with_handler(handler):
        result = await ComfyUIImageProvider(base_url="http://fake").generate(
            "test", width=64, height=64,
        )
    assert base64.b64decode(result.image_b64) == png


async def test_comfyui_fails_fast_on_persistent_errors(monkeypatch):
    """Sustained /history transport errors surface as RuntimeError, not a 10-min timeout."""
    from vulca.providers import comfyui as comfyui_mod
    from vulca.providers.comfyui import ComfyUIImageProvider

    monkeypatch.setattr(comfyui_mod, "_POLL_INTERVAL", 0)
    monkeypatch.setattr(comfyui_mod, "_MAX_CONSECUTIVE_POLL_FAILURES", 3)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/prompt":
            return httpx.Response(200, json={"prompt_id": "pid-down"})
        raise httpx.ConnectError("comfyui unreachable")

    with _comfyui_with_handler(handler):
        with pytest.raises(RuntimeError, match="ComfyUI unreachable"):
            await ComfyUIImageProvider(base_url="http://fake").generate(
                "test", width=64, height=64,
            )


async def test_comfyui_inprogress_polls_reset_failure_counter(monkeypatch):
    """Alternating transient errors + in-progress polls must not trip the failure cap."""
    from vulca.providers import comfyui as comfyui_mod
    from vulca.providers.comfyui import ComfyUIImageProvider

    monkeypatch.setattr(comfyui_mod, "_POLL_INTERVAL", 0)
    monkeypatch.setattr(comfyui_mod, "_MAX_CONSECUTIVE_POLL_FAILURES", 3)

    png = _png_bytes()
    call_log: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/prompt":
            return httpx.Response(200, json={"prompt_id": "pid-slow"})
        if request.url.path == "/history/pid-slow":
            call_log.append("hist")
            # Pattern: 2 errors, 1 in-progress (resets), 2 errors, 1 in-progress,
            # 2 errors, then success. Would trip a naive N=3 cap without reset.
            n = len(call_log)
            if n in (3, 6):
                return httpx.Response(200, json={"pid-slow": {
                    "status": {"status_str": "success", "completed": False, "messages": []},
                    "outputs": {},
                }})
            if n >= 7:
                return httpx.Response(200, json={"pid-slow": {
                    "status": {"status_str": "success", "completed": True, "messages": []},
                    "outputs": {"9": {"images": [
                        {"filename": "x.png", "subfolder": "", "type": "output"},
                    ]}},
                }})
            raise httpx.ConnectError("flap")
        if request.url.path == "/view":
            return httpx.Response(200, content=png)
        return httpx.Response(404)

    with _comfyui_with_handler(handler):
        result = await ComfyUIImageProvider(base_url="http://fake").generate(
            "test", width=64, height=64,
        )
    assert base64.b64decode(result.image_b64) == png


async def test_comfyui_returns_valid_png():
    from vulca.providers.comfyui import ComfyUIImageProvider

    png = _png_bytes()
    handler = _comfy_handler(
        "pid-ok",
        {"status_str": "success", "completed": True, "messages": []},
        images=[{"filename": "ok.png", "subfolder": "", "type": "output"}],
        view_bytes=png,
    )
    with _comfyui_with_handler(handler):
        result = await ComfyUIImageProvider(base_url="http://fake").generate(
            "test", width=64, height=64,
        )
        assert base64.b64decode(result.image_b64) == png
        assert result.metadata == {"prompt_id": "pid-ok"}


# --- Inpaint phase: raw_prompt propagation + provider key isolation ------

async def test_repaint_forwards_raw_prompt_true(tmp_path):
    """InpaintPhase.repaint() must pass raw_prompt=True to the provider."""
    from vulca.studio.phases.inpaint import InpaintPhase
    from vulca.providers.base import ImageResult

    original = tmp_path / "orig.png"
    original.write_bytes(_png_bytes())
    crop = tmp_path / "crop.png"
    crop.write_bytes(_png_bytes())

    captured = {}

    class FakeProvider:
        async def generate(self, prompt, **kwargs):
            captured.update(kwargs)
            return ImageResult(image_b64=base64.b64encode(_png_bytes()).decode(),
                               mime="image/png")

    import vulca.providers as providers_mod
    with patch.object(providers_mod, "get_image_provider",
                      return_value=FakeProvider()):
        await InpaintPhase().repaint(
            str(original), str(crop),
            instruction="fix", tradition="default",
            provider="gemini", count=1, output_dir=str(tmp_path),
        )
    assert captured.get("raw_prompt") is True


async def test_repaint_does_not_force_google_key_on_openai(tmp_path, monkeypatch):
    """When provider=openai with no explicit api_key, GOOGLE_API_KEY must NOT be injected."""
    from vulca.studio.phases.inpaint import InpaintPhase
    from vulca.providers.base import ImageResult
    import vulca.providers as providers_mod

    monkeypatch.setenv("GOOGLE_API_KEY", "google-only")
    captured_kwargs = {}

    def fake_get(name, **kwargs):
        captured_kwargs["name"] = name
        captured_kwargs["kwargs"] = kwargs

        class _P:
            async def generate(self, prompt, **kw):
                return ImageResult(image_b64=base64.b64encode(_png_bytes()).decode(),
                                   mime="image/png")
        return _P()

    original = tmp_path / "orig.png"
    original.write_bytes(_png_bytes())
    crop = tmp_path / "crop.png"
    crop.write_bytes(_png_bytes())

    with patch.object(providers_mod, "get_image_provider", side_effect=fake_get):
        await InpaintPhase().repaint(
            str(original), str(crop),
            instruction="fix", tradition="default",
            provider="openai", count=1, output_dir=str(tmp_path),
        )
    assert captured_kwargs["name"] == "openai"
    assert "api_key" not in captured_kwargs["kwargs"]


# --- OpenAI provider: raw_prompt suppression -----------------------------

async def test_repaint_uses_crop_as_reference(tmp_path):
    """InpaintPhase.repaint() must pass the CROP bytes as reference, not the original."""
    from vulca.studio.phases.inpaint import InpaintPhase
    from vulca.providers.base import ImageResult
    import vulca.providers as providers_mod

    original_bytes = _png_bytes(size=5000)
    crop_bytes = _png_bytes(size=3000)
    assert original_bytes != crop_bytes
    original = tmp_path / "orig.png"
    original.write_bytes(original_bytes)
    crop = tmp_path / "crop.png"
    crop.write_bytes(crop_bytes)

    captured_ref: dict = {}

    class FakeProvider:
        async def generate(self, prompt, **kwargs):
            captured_ref["b64"] = kwargs.get("reference_image_b64", "")
            return ImageResult(image_b64=base64.b64encode(_png_bytes()).decode(),
                               mime="image/png")

    with patch.object(providers_mod, "get_image_provider",
                      return_value=FakeProvider()):
        await InpaintPhase().repaint(
            str(original), str(crop),
            instruction="fix", tradition="default",
            provider="gemini", count=1, output_dir=str(tmp_path),
        )
    # The reference sent to the provider must be the crop, not the original.
    assert base64.b64decode(captured_ref["b64"]) == crop_bytes


async def test_openai_provider_uses_edits_endpoint_with_reference(monkeypatch):
    """When reference_image_b64 is set, OpenAI must hit /images/edits (multipart)."""
    from vulca.providers.openai_provider import OpenAIImageProvider

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        assert "multipart/form-data" in request.headers.get("content-type", "")
        return httpx.Response(200, json={"data": [{"b64_json": "AAAA"}]})

    ref_b64 = base64.b64encode(_png_bytes()).decode()
    with _httpx_with_handler(handler):
        result = await OpenAIImageProvider().generate(
            "regenerate this region",
            reference_image_b64=ref_b64,
        )
    assert calls == ["/v1/images/edits"]
    assert result.metadata["endpoint"] == "edits"


async def test_openai_provider_uses_generations_without_reference(monkeypatch):
    """Without a reference, OpenAI must still hit /images/generations (JSON)."""
    from vulca.providers.openai_provider import OpenAIImageProvider

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        assert request.headers.get("content-type") == "application/json"
        return httpx.Response(200, json={"data": [{"b64_json": "AAAA"}]})

    with _httpx_with_handler(handler):
        result = await OpenAIImageProvider().generate("a sunset")
    assert calls == ["/v1/images/generations"]
    assert result.metadata["endpoint"] == "generations"


@pytest.mark.parametrize("model", ["dall-e-3", "dall-e-2"])
async def test_openai_provider_rejects_edits_on_non_gpt_image(model):
    """Only gpt-image-* supports mask-less edits. dall-e-{2,3} must fail fast."""
    from vulca.providers.openai_provider import OpenAIImageProvider

    provider = OpenAIImageProvider(api_key="sk-test", model=model)
    with pytest.raises(ValueError, match="img2img"):
        await provider.generate(
            "x", reference_image_b64=base64.b64encode(_png_bytes()).decode(),
        )


async def test_repaint_raises_when_crop_unreadable(tmp_path):
    """If crop_path doesn't exist, repaint must raise — not silently fall back."""
    from vulca.studio.phases.inpaint import InpaintPhase

    original = tmp_path / "orig.png"
    original.write_bytes(_png_bytes())
    missing_crop = tmp_path / "does_not_exist.png"

    with pytest.raises(RuntimeError, match="Cannot read crop reference"):
        await InpaintPhase().repaint(
            str(original), str(missing_crop),
            instruction="fix", tradition="default",
            provider="gemini", count=1, output_dir=str(tmp_path),
        )


async def test_openai_provider_honors_raw_prompt(monkeypatch):
    """OpenAI provider must skip tradition wrapping when raw_prompt=True."""
    from vulca.providers.openai_provider import OpenAIImageProvider

    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    captured_payloads = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_payloads.append(json.loads(request.content.decode()))
        return httpx.Response(200, json={"data": [{"b64_json": "AAAA"}]})

    with _httpx_with_handler(handler):
        await OpenAIImageProvider().generate(
            "raw user text", tradition="chinese_xieyi", raw_prompt=True,
        )
    assert captured_payloads[0]["prompt"] == "raw user text"
