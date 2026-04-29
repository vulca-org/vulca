import asyncio
import base64
import io
import sys
import types

from PIL import Image

from vulca.layers.manifest import write_manifest
from vulca.layers.types import LayerInfo
from vulca.providers.base import ImageEditCapabilities


def _run(coro):
    return asyncio.run(coro)


def _png_b64(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


class RecordingEditProvider:
    capabilities = frozenset({"raw_rgba"})

    def __init__(self):
        self.calls = []
        self.model = "gpt-image-2"

    def edit_capabilities(self):
        return ImageEditCapabilities(
            supports_edits=True,
            requires_mask_for_edits=True,
            supports_masked_edits=True,
            supports_unmasked_edits=False,
            supports_quality=True,
        )

    async def inpaint_with_mask(self, *, image_path, mask_path, prompt, **kwargs):
        with Image.open(image_path) as probe:
            size = probe.size
        self.calls.append(
            {
                "image_path": image_path,
                "mask_path": mask_path,
                "size": size,
                "prompt": prompt,
            }
        )
        return type(
            "Result",
            (),
            {
                "image_b64": _png_b64(Image.new("RGB", size, (240, 240, 210))),
                "mime": "image/png",
                "metadata": {},
            },
        )()

    async def generate(self, prompt, **kwargs):
        raise AssertionError("MCP sparse redraw must use masked edit")


def _stage_artwork(tmp_path):
    size = (1000, 1000)
    alpha = Image.new("L", size, 0)
    alpha.paste(Image.new("L", (80, 80), 255), (440, 440))
    rgb = Image.new("RGB", size, (120, 80, 60))
    Image.merge("RGBA", (*rgb.split(), alpha)).save(tmp_path / "fg.png")
    Image.new("RGB", size, (100, 100, 100)).save(tmp_path / "source.png")
    write_manifest(
        [
            LayerInfo(
                name="fg",
                description="foreground object",
                z_index=1,
                content_type="subject",
            )
        ],
        output_dir=str(tmp_path),
        width=size[0],
        height=size[1],
        source_image="source.png",
    )


class _FastMCPStub:
    def __init__(self, *args, **kwargs):
        pass

    def tool(self, *args, **kwargs):
        def decorator(fn):
            return fn

        return decorator

    def run(self):
        pass


def _install_fastmcp_stub(monkeypatch):
    module = types.ModuleType("fastmcp")
    module.FastMCP = _FastMCPStub
    monkeypatch.setitem(sys.modules, "fastmcp", module)


def test_layers_redraw_returns_route_and_quality_advisory(tmp_path, monkeypatch):
    _install_fastmcp_stub(monkeypatch)

    from vulca.mcp_server import layers_redraw
    import vulca.providers as providers_mod

    provider = RecordingEditProvider()
    monkeypatch.setattr(
        providers_mod, "get_image_provider", lambda name, api_key="": provider
    )
    _stage_artwork(tmp_path)

    result = _run(
        layers_redraw(
            artwork_dir=str(tmp_path),
            layer="fg",
            instruction="make it cleaner",
            provider="openai",
            route="auto",
            preserve_alpha=True,
        )
    )

    assert provider.calls
    assert result["name"] == "fg_redrawn"
    assert result["redraw_route"] == "sparse_bbox_crop"
    assert result["route_requested"] == "auto"
    assert result["route_chosen"] == "inpaint"
    assert result["sparse_detected"] is True
    assert result["provider_requires_mask_for_edits"] is True
    assert result["area_pct"] > 0
    assert result["bbox_fill"] > 0
    assert result["component_count"] == 1
    assert result["quality_gate_passed"] is True
    assert result["quality_failures"] == []
