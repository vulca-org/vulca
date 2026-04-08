import os
import subprocess
import sys


def _run(*argv):
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    return subprocess.run([sys.executable, "-m", "vulca", *argv],
                          capture_output=True, text=True, env=env)


def test_retry_subcommand_help():
    out = _run("layers", "retry", "--help")
    assert out.returncode == 0, out.stderr
    assert "--layer" in out.stdout
    assert "--all-failed" in out.stdout
    assert "artifact_dir" in out.stdout


def test_retry_preserves_partial_when_other_layers_still_failed(tmp_path, monkeypatch):
    """Retrying one layer must not mark the whole artifact healthy when
    other layers remain failed."""
    import asyncio
    import base64
    import io
    import json
    from pathlib import Path

    from PIL import Image

    from vulca.layers.retry import retry_layers
    import vulca.providers as providers_mod
    from vulca.pipeline.engine import execute
    from vulca.pipeline.templates import LAYERED
    from vulca.pipeline.types import PipelineInput

    class _FlakyPNG:
        id = "flaky"
        model = "flaky-1"

        def __init__(self, fail_token):
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

    # Initial run: fail every non-bg layer by matching "USER INTENT".
    flaky_all = _FlakyPNG("USER INTENT")
    monkeypatch.setattr(providers_mod, "get_image_provider", lambda *a, **k: flaky_all)
    inp = PipelineInput(subject="远山薄雾", intent="远山薄雾",
                        tradition="chinese_xieyi", provider="flaky",
                        layered=True, output_dir=str(tmp_path))
    asyncio.run(execute(LAYERED, inp))

    manifest = json.loads((tmp_path / "manifest.json").read_text())
    failed_names = [l["name"] for l in manifest["layers"]
                    if l.get("status") == "failed"]
    assert len(failed_names) >= 2, "need at least 2 failed layers for this test"

    # Retry only the FIRST failed layer. Use a provider that succeeds for that
    # layer's prompt but would still fail every other USER INTENT layer — which
    # we never ask it to regenerate here.
    target = failed_names[0]
    ok_provider = _FlakyPNG("")  # never fails
    result = asyncio.run(retry_layers(
        str(tmp_path),
        tradition_name="chinese_xieyi",
        layer_names=[target],
        provider=ok_provider,
    ))
    assert result.is_complete  # the subset we retried did succeed

    manifest2 = json.loads((tmp_path / "manifest.json").read_text())
    # The retried layer is now ok…
    retried_entry = next(l for l in manifest2["layers"] if l["name"] == target)
    assert retried_entry.get("status") == "ok"
    # …but the other failed layers are still failed, so partial stays True.
    assert manifest2["partial"] is True, (
        "retry must not mark artifact healthy while other layers still fail"
    )


def test_retry_helper_picks_targets(tmp_path):
    """pick_targets() returns files that are missing on disk when all_failed=True."""
    from vulca.layers.retry import pick_targets
    manifest = {
        "layers": [
            {"id": "a", "name": "bg", "file": "bg.png",
             "validation": {"ok": True, "warnings": []}},
            {"id": "b", "name": "far", "file": "far.png",
             "validation": {"ok": False, "warnings": [{"kind": "coverage"}]}},
        ]
    }
    (tmp_path / "bg.png").write_bytes(b"PNG")
    # far.png intentionally missing — should also be picked
    targets = pick_targets(manifest, tmp_path, all_failed=True)
    names = sorted(t["name"] for t in targets)
    assert names == ["far"]

    targets = pick_targets(manifest, tmp_path, layer_names=["bg"])
    assert [t["name"] for t in targets] == ["bg"]
