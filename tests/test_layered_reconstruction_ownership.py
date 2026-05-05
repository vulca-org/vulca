import numpy as np
from PIL import Image

from vulca.layers.reconstruction import (
    LayerPromptContract,
    evaluate_ownership_quality_gates,
    normalize_layer_ownership,
)


def _contract(path: str, z: int, policy: str, parent=None):
    return LayerPromptContract(
        semantic_path=path,
        display_name=path,
        z_index=z,
        visual_role="detail" if path.startswith("detail.") else "foreground",
        mvp_policy=policy,
        allowed_policies=(policy,),
        edit_risk="low",
        parent_layer=parent,
        mask_prompt=path,
        prompt_lines=(path,),
        forbidden_content=(),
    )


def _mask(size, box):
    img = Image.new("L", size, 0)
    img.paste(Image.new("L", (box[2], box[3]), 255), (box[0], box[1]))
    return img


def test_detail_flower_pixels_are_subtracted_from_parent_hedge():
    size = (8, 6)
    layers = (
        _contract("foreground.hedge_bush", 60, "preserve"),
        _contract(
            "detail.white_flower_cluster",
            80,
            "local_redraw",
            "foreground.hedge_bush",
        ),
        _contract(
            "detail.yellow_dandelion_heads",
            90,
            "local_redraw",
            "foreground.hedge_bush",
        ),
        _contract("residual.source_texture", 100, "residual"),
    )
    source_masks = {
        "foreground.hedge_bush": _mask(size, (0, 2, 8, 4)),
        "detail.white_flower_cluster": _mask(size, (2, 3, 2, 2)),
        "detail.yellow_dandelion_heads": _mask(size, (5, 3, 1, 1)),
    }

    owned = normalize_layer_ownership(size=size, layers=layers, source_masks=source_masks)

    hedge = np.asarray(owned["foreground.hedge_bush"]) > 0
    white = np.asarray(owned["detail.white_flower_cluster"]) > 0
    yellow = np.asarray(owned["detail.yellow_dandelion_heads"]) > 0
    residual = np.asarray(owned["residual.source_texture"]) > 0

    assert not np.logical_and(hedge, white).any()
    assert not np.logical_and(hedge, yellow).any()
    assert white.sum() == 4
    assert yellow.sum() == 1
    union = hedge | white | yellow | residual
    assert union.all()


def test_unassigned_pixels_go_to_visible_residual_layer():
    size = (4, 4)
    layers = (
        _contract("background.sky.clean_blue", 0, "reconstruct"),
        _contract("residual.source_texture", 100, "residual"),
    )
    source_masks = {"background.sky.clean_blue": _mask(size, (0, 0, 4, 2))}

    owned = normalize_layer_ownership(size=size, layers=layers, source_masks=source_masks)

    residual = np.asarray(owned["residual.source_texture"]) > 0
    assert residual[:2, :].sum() == 0
    assert residual[2:, :].all()


def test_quality_gates_detect_flower_overlap_with_parent_hedge():
    size = (4, 4)
    layers = (
        _contract("foreground.hedge_bush", 60, "preserve"),
        _contract(
            "detail.white_flower_cluster",
            80,
            "local_redraw",
            "foreground.hedge_bush",
        ),
        _contract("residual.source_texture", 100, "residual"),
    )
    owned_masks = {
        "foreground.hedge_bush": _mask(size, (0, 0, 2, 2)),
        "detail.white_flower_cluster": _mask(size, (1, 1, 2, 2)),
        "residual.source_texture": _mask(size, (2, 2, 2, 2)),
    }

    gates = evaluate_ownership_quality_gates(
        size=size,
        layers=layers,
        owned_masks=owned_masks,
    )

    assert gates["ownership_no_overlap"] is False
    assert gates["flower_pixels_absent_from_parent_hedge"] is False
