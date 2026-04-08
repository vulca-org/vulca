"""Partial-failure e2e: inject a PNG-returning provider that fails on one
layer, run LAYERED through the full pipeline, and assert manifest.partial=True.
"""
from __future__ import annotations

import asyncio
import base64
import io
import json
from pathlib import Path

from PIL import Image

from vulca.pipeline.engine import execute
from vulca.pipeline.templates import LAYERED
from vulca.pipeline.types import PipelineInput


class _FlakyPNGProvider:
    """Returns a valid PNG for every call except when the prompt targets the
    layer whose USER INTENT contains `fail_token`."""

    id = "flaky"
    model = "flaky-1"

    def __init__(self, fail_token: str):
        self.fail_token = fail_token
        self.calls = 0

    async def generate(self, *, prompt, raw_prompt=False, reference_image_b64=None, **kw):
        self.calls += 1
        if self.fail_token and self.fail_token in prompt:
            raise RuntimeError("simulated provider failure")
        img = Image.new("RGB", (32, 32), (255, 255, 255))
        for y in range(8, 24):
            for x in range(8, 24):
                img.putpixel((x, y), (40, 40, 40))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return type("R", (), {"image_b64": base64.b64encode(buf.getvalue()).decode()})()


def test_layered_partial_failure_marks_manifest(tmp_path, monkeypatch):
    provider = _FlakyPNGProvider(fail_token="USER INTENT")  # fail every non-bg layer

    # Intercept get_image_provider so native path uses our flaky instance.
    import vulca.providers as providers_mod
    monkeypatch.setattr(providers_mod, "get_image_provider",
                        lambda *a, **kw: provider)

    inp = PipelineInput(
        subject="远山薄雾",
        intent="远山薄雾",
        tradition="chinese_xieyi",
        provider="flaky",
        layered=True,
        output_dir=str(tmp_path),
    )
    output = asyncio.run(execute(LAYERED, inp))
    # P0.1 #4: PipelineOutput exposes the partial flag directly.
    assert output.layered_partial is True
    assert output.to_dict()["layered_partial"] is True

    manifest = json.loads((Path(tmp_path) / "manifest.json").read_text())
    assert manifest["version"] == 3
    assert manifest["generation_path"] == "a"
    assert manifest["partial"] is True
    # At least one layer entry was recorded
    assert len(manifest.get("layers", [])) > 0
    # At least one provider call happened (we didn't just hit cache)
    assert provider.calls > 0

    # P0 #2: failed layers carry status=="failed" + reason in manifest extras,
    # so retry --all-failed can find them.
    failed_entries = [l for l in manifest["layers"] if l.get("status") == "failed"]
    assert len(failed_entries) > 0, "expected at least one failed layer in manifest"
    for entry in failed_entries:
        assert entry.get("source") == "a"
        assert entry.get("reason") in ("validation_failed", "generation_failed")

    from vulca.layers.retry import pick_targets
    targets = pick_targets(manifest, Path(tmp_path), all_failed=True)
    assert len(targets) == len(failed_entries)
