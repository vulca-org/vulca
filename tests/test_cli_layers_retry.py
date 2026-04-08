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


def test_cli_retry_unknown_layer_exits_with_error(tmp_path):
    """CLI end-to-end: bad --layer name must exit non-zero and mention the name."""
    import json as _json
    manifest = {
        "version": 3, "width": 256, "height": 256, "source_image": "",
        "split_mode": "", "generation_path": "a", "layerability": "native",
        "partial": False, "warnings": [], "created_at": "2026-04-08T00:00:00Z",
        "layers": [
            {"id": "layer_a", "name": "bg", "description": "", "z_index": 0,
             "blend_mode": "normal", "content_type": "background",
             "visible": True, "locked": False, "file": "bg.png",
             "dominant_colors": [], "regeneration_prompt": "", "opacity": 1.0,
             "x": 0, "y": 0, "width": 100, "height": 100, "rotation": 0,
             "content_bbox": None, "status": "ok", "source": "a"},
        ],
    }
    (tmp_path / "manifest.json").write_text(_json.dumps(manifest))
    (tmp_path / "bg.png").write_bytes(b"PNG")

    out = _run("layers", "retry", str(tmp_path), "--layer", "nope",
               "--tradition", "chinese_xieyi")
    assert out.returncode != 0
    assert "nope" in (out.stderr + out.stdout)


def test_retry_preserves_canvas_color_and_key_strategy(tmp_path, monkeypatch):
    """Retrying a layer must keep canvas_color/key_strategy in the overlay."""
    import asyncio
    import base64
    import io
    import json as _json
    from pathlib import Path

    from PIL import Image

    import vulca.providers as providers_mod
    from vulca.layers.retry import retry_layers
    from vulca.pipeline.engine import execute
    from vulca.pipeline.templates import LAYERED
    from vulca.pipeline.types import PipelineInput

    class _OK:
        id = "ok"
        model = "ok-1"

        async def generate(self, *, prompt, raw_prompt=False, **kw):
            img = Image.new("RGB", (32, 32), (255, 255, 255))
            for y in range(8, 24):
                for x in range(8, 24):
                    img.putpixel((x, y), (40, 40, 40))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return type("R", (), {"image_b64": base64.b64encode(buf.getvalue()).decode()})()

    monkeypatch.setattr(providers_mod, "get_image_provider", lambda *a, **k: _OK())
    inp = PipelineInput(subject="远山薄雾", intent="远山薄雾",
                        tradition="chinese_xieyi", provider="ok",
                        layered=True, output_dir=str(tmp_path))
    asyncio.run(execute(LAYERED, inp))

    manifest = _json.loads((tmp_path / "manifest.json").read_text())
    target_name = manifest["layers"][1]["name"]

    asyncio.run(retry_layers(
        str(tmp_path), tradition_name="chinese_xieyi",
        layer_names=[target_name], provider=_OK(),
    ))

    manifest2 = _json.loads((tmp_path / "manifest.json").read_text())
    retried = next(l for l in manifest2["layers"] if l["name"] == target_name)
    assert retried.get("canvas_color") == "#ffffff"
    assert retried.get("key_strategy") == "luminance"


def test_retry_unknown_layer_name_hard_fails():
    """P0.1 #2: requesting a layer name that doesn't exist must raise
    UnknownLayerError rather than silently returning zero targets."""
    from pathlib import Path as _P

    from vulca.layers.retry import UnknownLayerError, pick_targets
    manifest = {"layers": [
        {"id": "a", "name": "bg", "file": "bg.png"},
        {"id": "b", "name": "far", "file": "far.png"},
    ]}
    try:
        pick_targets(manifest, _P("/nonexistent"), layer_names=["nope"])
    except UnknownLayerError as exc:
        assert "nope" in str(exc)
        assert exc.unknown == ["nope"]
        assert set(exc.available) == {"bg", "far"}
    else:
        raise AssertionError("expected UnknownLayerError")


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
