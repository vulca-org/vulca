import numpy as np
from PIL import Image, ImageDraw

from vulca.layers.mask_refine import infer_refinement_profile, refine_mask_for_target


def test_infers_bright_small_subject_from_flower_instruction():
    profile = infer_refinement_profile(
        description="wildflower cluster on hedge",
        instruction="small bright white wildflowers with warm yellow centers",
    )
    assert profile is not None
    assert profile.kind == "bright_small_subject"


def test_non_target_layer_is_not_refined():
    source = Image.new("RGB", (200, 160), (40, 90, 40))
    alpha = Image.new("L", (200, 160), 255)

    result = refine_mask_for_target(
        source,
        alpha,
        description="red car body",
        instruction="make the car more cartoon",
    )

    assert result.applied is False
    assert result.child_masks == ()
    assert result.reason == "no_target_profile"


def test_refines_broad_flower_mask_into_child_patches():
    source = Image.new("RGB", (240, 180), (35, 92, 43))
    draw = ImageDraw.Draw(source)
    flower_boxes = (
        (46, 48, 65, 67),
        (112, 78, 132, 98),
        (178, 42, 199, 63),
    )
    for box in flower_boxes:
        draw.ellipse(box, fill=(238, 235, 220))
        cx = (box[0] + box[2]) // 2
        cy = (box[1] + box[3]) // 2
        draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=(218, 172, 54))

    alpha = Image.new("L", source.size, 0)
    ImageDraw.Draw(alpha).rectangle((28, 25, 215, 122), fill=255)

    result = refine_mask_for_target(
        source,
        alpha,
        description="wildflower cluster on hedge",
        instruction="make small bright white wildflowers with yellow centers",
    )

    assert result.applied is True
    assert result.strategy == "bright_small_subject"
    assert len(result.child_masks) >= 3

    parent_area = int(np.asarray(alpha).astype(bool).sum())
    for child in result.child_masks:
        child_area = int(np.asarray(child).astype(bool).sum())
        assert 0 < child_area < parent_area * 0.2


def test_refines_connected_flower_evidence_into_separate_patches():
    source = Image.new("RGB", (260, 180), (35, 92, 43))
    draw = ImageDraw.Draw(source)
    centers = ((58, 62), (130, 86), (202, 58))
    draw.line(centers, fill=(230, 228, 218), width=1)
    for cx, cy in centers:
        draw.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=(238, 235, 220))
        draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=(218, 172, 54))

    alpha = Image.new("L", source.size, 0)
    ImageDraw.Draw(alpha).rectangle((30, 25, 230, 125), fill=255)

    result = refine_mask_for_target(
        source,
        alpha,
        description="wildflower cluster on hedge",
        instruction="make small bright white wildflowers with yellow centers",
    )

    assert result.applied is True
    assert len(result.child_masks) >= 3


def test_refined_child_masks_do_not_fill_broad_parent_bbox():
    source = Image.new("RGB", (260, 180), (35, 92, 43))
    draw = ImageDraw.Draw(source)
    draw.line(((42, 36), (218, 116)), fill=(238, 235, 220), width=3)

    alpha = Image.new("L", source.size, 0)
    ImageDraw.Draw(alpha).rectangle((30, 25, 230, 125), fill=255)

    result = refine_mask_for_target(
        source,
        alpha,
        description="wildflower cluster on hedge",
        instruction="make small bright white wildflowers with yellow centers",
    )

    assert result.applied is True
    parent_area = int(np.asarray(alpha).astype(bool).sum())
    child_area = sum(int(np.asarray(child).astype(bool).sum()) for child in result.child_masks)
    assert child_area < parent_area * 0.5
