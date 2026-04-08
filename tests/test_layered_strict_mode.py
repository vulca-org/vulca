"""P0 #4: --strict must fail the run when any native layer fails."""
from __future__ import annotations

import asyncio
import base64
import io

from PIL import Image

from vulca.pipeline.engine import execute
from vulca.pipeline.templates import LAYERED
from vulca.pipeline.types import PipelineInput, RunStatus


class _FlakyPNG:
    id = "flaky"
    model = "flaky-1"

    def __init__(self, fail_token: str):
        self.fail_token = fail_token

    async def generate(self, *, prompt, raw_prompt=False, reference_image_b64=None, **kw):
        if self.fail_token and self.fail_token in prompt:
            raise RuntimeError("simulated failure")
        img = Image.new("RGB", (32, 32), (255, 255, 255))
        for y in range(8, 24):
            for x in range(8, 24):
                img.putpixel((x, y), (40, 40, 40))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return type("R", (), {"image_b64": base64.b64encode(buf.getvalue()).decode()})()


def _run(tmp_path, *, strict, fail_all=True, monkeypatch):
    provider = _FlakyPNG("USER INTENT" if fail_all else "")
    import vulca.providers as providers_mod
    monkeypatch.setattr(providers_mod, "get_image_provider",
                        lambda *a, **k: provider)

    inp = PipelineInput(
        subject="远山薄雾", intent="远山薄雾",
        tradition="chinese_xieyi", provider="flaky",
        layered=True, output_dir=str(tmp_path),
        strict=strict,
    )
    return asyncio.run(execute(LAYERED, inp))


def test_strict_true_fails_run_when_any_layer_fails(tmp_path, monkeypatch):
    output = _run(tmp_path, strict=True, fail_all=True, monkeypatch=monkeypatch)
    assert output.status == RunStatus.FAILED


def test_strict_false_completes_with_partial_manifest(tmp_path, monkeypatch):
    output = _run(tmp_path, strict=False, fail_all=True, monkeypatch=monkeypatch)
    # Without --strict, partial failures do NOT fail the run.
    assert output.status != RunStatus.FAILED
