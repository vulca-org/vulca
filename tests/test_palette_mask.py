from __future__ import annotations

import asyncio
import argparse
import base64
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
from PIL import Image

from vulca.layers.types import LayerInfo


def _layer(name: str, z: int, *, content_type: str = "subject") -> LayerInfo:
    return LayerInfo(
        name=name,
        id=f"layer_{name}",
        description=f"the {name} region",
        z_index=z,
        content_type=content_type,
    )


def _image_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _source_image() -> Image.Image:
    img = Image.new("RGB", (6, 4), (240, 240, 240))
    pixels = img.load()
    for y in range(4):
        for x in range(3):
            pixels[x, y] = (200, 80, 80)
        for x in range(3, 6):
            pixels[x, y] = (80, 120, 200)
    return img


def _palette_mask(*, fuzzy: bool = False) -> Image.Image:
    img = Image.new("RGB", (6, 4), (0, 0, 0))
    pixels = img.load()
    left = (255, 0, 0) if not fuzzy else (248, 5, 3)
    right = (0, 255, 0) if not fuzzy else (4, 247, 8)
    for y in range(4):
        for x in range(3):
            pixels[x, y] = left
        for x in range(3, 6):
            pixels[x, y] = right
    return img


def _palette_mask_missing_icon() -> Image.Image:
    return Image.new("RGB", (6, 4), (255, 0, 0))


def _mock_provider(mask: Image.Image) -> MagicMock:
    result = MagicMock()
    result.image_b64 = _image_to_b64(mask)
    result.mime = "image/png"
    provider = MagicMock()
    provider.generate = AsyncMock(return_value=result)
    return provider


def test_build_palette_mask_prompt_contains_contract_and_colors():
    from vulca.layers.palette_mask import build_palette_mask_prompt

    prompt, palette = build_palette_mask_prompt([
        _layer("product", 2),
        _layer("background", 0, content_type="background"),
    ])

    assert "pure flat RGB palette mask" in prompt
    assert "Do not generate a normal image" in prompt
    assert "product" in prompt
    assert palette["product"] == "#ff0000"
    assert palette["background"] == "#000000"


def test_decode_palette_mask_exact_colors():
    from vulca.layers.palette_mask import decode_palette_mask

    product = _layer("product", 2)
    icon = _layer("icon", 1)
    masks = decode_palette_mask(
        _palette_mask(),
        [product, icon],
        palette={"product": "#ff0000", "icon": "#00ff00"},
    )

    product_arr = np.array(masks[product.id])
    icon_arr = np.array(masks[icon.id])
    assert product_arr[:, :3].min() == 255
    assert product_arr[:, 3:].max() == 0
    assert icon_arr[:, :3].max() == 0
    assert icon_arr[:, 3:].min() == 255


def test_decode_palette_mask_nearest_color_tolerance():
    from vulca.layers.palette_mask import decode_palette_mask

    product = _layer("product", 2)
    icon = _layer("icon", 1)
    masks = decode_palette_mask(
        _palette_mask(fuzzy=True),
        [product, icon],
        palette={"product": "#ff0000", "icon": "#00ff00"},
        tolerance=24,
    )

    assert np.array(masks[product.id])[:, :3].min() == 255
    assert np.array(masks[icon.id])[:, 3:].min() == 255


def test_split_palette_calls_provider_once_and_writes_layers():
    from vulca.layers.palette_mask import split_palette

    product = _layer("product", 2)
    icon = _layer("icon", 1)
    provider = _mock_provider(_palette_mask())

    with tempfile.TemporaryDirectory() as td:
        source_path = Path(td) / "source.png"
        _source_image().save(source_path)

        with patch("vulca.providers.get_image_provider", return_value=provider):
            results = asyncio.run(
                split_palette(
                    str(source_path),
                    [product, icon],
                    output_dir=td,
                    provider="nb2",
                    palette={"product": "#ff0000", "icon": "#00ff00"},
                )
            )

        assert provider.generate.call_count == 1
        call = provider.generate.call_args
        assert call.kwargs["raw_prompt"] is True
        assert call.kwargs["reference_image_b64"]

        by_name = {r.info.name: r for r in results}
        product_img = Image.open(by_name["product"].image_path)
        icon_img = Image.open(by_name["icon"].image_path)
        assert product_img.mode == "RGBA"
        assert icon_img.mode == "RGBA"
        assert np.array(product_img)[:, :3, 3].min() == 255
        assert np.array(product_img)[:, 3:, 3].max() == 0
        assert np.array(icon_img)[:, :3, 3].max() == 0
        assert np.array(icon_img)[:, 3:, 3].min() == 255

        manifest = json.loads((Path(td) / "manifest.json").read_text())
        assert manifest["split_mode"] == "palette"


def test_split_palette_writes_quantized_mask_for_exact_colors():
    from vulca.layers.palette_mask import split_palette

    product = _layer("product", 2)
    icon = _layer("icon", 1)
    provider = _mock_provider(_palette_mask())

    with tempfile.TemporaryDirectory() as td:
        source_path = Path(td) / "source.png"
        _source_image().save(source_path)

        with patch("vulca.providers.get_image_provider", return_value=provider):
            asyncio.run(
                split_palette(
                    str(source_path),
                    [product, icon],
                    output_dir=td,
                    provider="nb2",
                    palette={"product": "#ff0000", "icon": "#00ff00"},
                )
            )

        quantized = Image.open(Path(td) / "palette_mask_quantized.png").convert("RGB")
        assert quantized.size == (6, 4)
        colors = set(map(tuple, np.array(quantized).reshape(-1, 3)))
        assert colors == {(255, 0, 0), (0, 255, 0)}


def test_split_palette_quantizes_near_color_mask():
    from vulca.layers.palette_mask import split_palette

    product = _layer("product", 2)
    icon = _layer("icon", 1)
    provider = _mock_provider(_palette_mask(fuzzy=True))

    with tempfile.TemporaryDirectory() as td:
        source_path = Path(td) / "source.png"
        _source_image().save(source_path)

        with patch("vulca.providers.get_image_provider", return_value=provider):
            asyncio.run(
                split_palette(
                    str(source_path),
                    [product, icon],
                    output_dir=td,
                    provider="nb2",
                    palette={"product": "#ff0000", "icon": "#00ff00"},
                    tolerance=24,
                )
            )

        quantized = Image.open(Path(td) / "palette_mask_quantized.png").convert("RGB")
        colors = set(map(tuple, np.array(quantized).reshape(-1, 3)))
        assert colors == {(255, 0, 0), (0, 255, 0)}


def test_split_palette_decode_report_and_manifest_include_layer_quality():
    from vulca.layers.palette_mask import split_palette

    product = _layer("product", 2)
    icon = _layer("icon", 1)
    provider = _mock_provider(_palette_mask())

    with tempfile.TemporaryDirectory() as td:
        source_path = Path(td) / "source.png"
        _source_image().save(source_path)

        with patch("vulca.providers.get_image_provider", return_value=provider):
            asyncio.run(
                split_palette(
                    str(source_path),
                    [product, icon],
                    output_dir=td,
                    provider="nb2",
                    palette={"product": "#ff0000", "icon": "#00ff00"},
                )
            )

        report = json.loads((Path(td) / "decode_report.json").read_text())
        by_name = {item["name"]: item for item in report["layers"]}
        assert report["unmatched_pct"] == 0.0
        assert by_name["product"]["palette_color"] == "#ff0000"
        assert by_name["product"]["pixel_count"] == 12
        assert by_name["product"]["area_pct"] == 50.0
        assert by_name["product"]["bbox"] == {"x": 0, "y": 0, "w": 3, "h": 4}
        assert by_name["product"]["quality_status"] == "detected"

        manifest = json.loads((Path(td) / "manifest.json").read_text())
        manifest_by_name = {item["name"]: item for item in manifest["layers"]}
        assert manifest_by_name["product"]["content_bbox"] == {"x": 0, "y": 0, "w": 3, "h": 4}
        assert manifest_by_name["product"]["area_pct"] == 50.0
        assert manifest_by_name["product"]["quality_status"] == "detected"
        assert manifest_by_name["product"]["dominant_colors"] == ["#ff0000"]


def test_split_palette_empty_layer_is_reported_as_missed():
    from vulca.layers.palette_mask import split_palette

    product = _layer("product", 2)
    icon = _layer("icon", 1)
    provider = _mock_provider(_palette_mask_missing_icon())

    with tempfile.TemporaryDirectory() as td:
        source_path = Path(td) / "source.png"
        _source_image().save(source_path)

        with patch("vulca.providers.get_image_provider", return_value=provider):
            asyncio.run(
                split_palette(
                    str(source_path),
                    [product, icon],
                    output_dir=td,
                    provider="nb2",
                    palette={"product": "#ff0000", "icon": "#00ff00"},
                )
            )

        report = json.loads((Path(td) / "decode_report.json").read_text())
        by_name = {item["name"]: item for item in report["layers"]}
        assert by_name["icon"]["quality_status"] == "missed"
        assert by_name["icon"]["pixel_count"] == 0
        assert by_name["icon"]["bbox"] is None
        assert any("empty layer: icon" in warning for warning in report["warnings"])

        manifest = json.loads((Path(td) / "manifest.json").read_text())
        assert any("empty layer: icon" in warning for warning in manifest["warnings"])


def test_split_palette_writes_contact_sheet():
    from vulca.layers.palette_mask import split_palette

    product = _layer("product", 2)
    icon = _layer("icon", 1)
    provider = _mock_provider(_palette_mask())

    with tempfile.TemporaryDirectory() as td:
        source_path = Path(td) / "source.png"
        _source_image().save(source_path)

        with patch("vulca.providers.get_image_provider", return_value=provider):
            asyncio.run(
                split_palette(
                    str(source_path),
                    [product, icon],
                    output_dir=td,
                    provider="nb2",
                    palette={"product": "#ff0000", "icon": "#00ff00"},
                )
            )

        contact_sheet = Image.open(Path(td) / "contact_sheet.png")
        assert contact_sheet.size[0] > 6
        assert contact_sheet.size[1] > 4


def test_mcp_layers_split_palette_payload_includes_debug_artifact_paths():
    from vulca.mcp_server import layers_split

    product = _layer("product", 2)
    icon = _layer("icon", 1)
    provider = _mock_provider(_palette_mask())

    with tempfile.TemporaryDirectory() as td:
        source_path = Path(td) / "source.png"
        _source_image().save(source_path)

        with (
            patch("vulca.layers.analyze.analyze_layers", AsyncMock(return_value=[product, icon])),
            patch("vulca.providers.get_image_provider", return_value=provider),
        ):
            payload = asyncio.run(
                layers_split(
                    str(source_path),
                    output_dir=td,
                    mode="palette",
                    provider="nb2",
                )
            )

        for key in (
            "palette_mask_path",
            "palette_mask_quantized_path",
            "decode_report_path",
            "contact_sheet_path",
        ):
            assert Path(payload[key]).exists()


def test_cli_layers_split_palette_prints_debug_artifact_paths():
    from vulca.cli import _cmd_layers

    product = _layer("product", 2)
    icon = _layer("icon", 1)
    provider = _mock_provider(_palette_mask())

    with tempfile.TemporaryDirectory() as td:
        source_path = Path(td) / "source.png"
        _source_image().save(source_path)
        args = argparse.Namespace(
            layers_command="split",
            image=str(source_path),
            output=td,
            mode="palette",
            provider="nb2",
            tradition="default",
            case_log="",
        )

        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            patch("vulca.layers.analyze.analyze_layers", AsyncMock(return_value=[product, icon])),
            patch("vulca.providers.get_image_provider", return_value=provider),
        ):
            _cmd_layers(args)

        output = stdout.getvalue()
        assert "palette_mask.png" in output
        assert "palette_mask_quantized.png" in output
        assert "decode_report.json" in output
        assert "contact_sheet.png" in output


def test_split_palette_importable_from_layers():
    from vulca.layers import split_palette

    assert callable(split_palette)


def test_cli_layers_split_help_mentions_palette():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    result = subprocess.run(
        [sys.executable, "-m", "vulca.cli", "layers", "split", "--help"],
        text=True,
        capture_output=True,
        check=True,
        env=env,
    )

    assert "palette" in result.stdout


def test_mcp_layers_split_docstring_mentions_palette():
    from vulca.mcp_server import layers_split

    assert "palette" in (layers_split.__doc__ or "")
