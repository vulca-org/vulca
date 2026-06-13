from __future__ import annotations

import asyncio
import base64
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
