import numpy as np
from PIL import Image, ImageDraw

from vulca.layers.mask_refine import infer_refinement_profile, refine_mask_for_target


def test_infers_small_botanical_subject_from_flower_instruction():
    profile = infer_refinement_profile(
        description="wildflower cluster on hedge",
        instruction="small bright white wildflowers with warm yellow centers",
    )
    assert profile is not None
    assert profile.kind == "small_botanical_subject_replacement"


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
    assert result.strategy == "small_botanical_subject_replacement"
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


def test_refines_dense_connected_flower_evidence_into_bounded_tiles():
    source = Image.new("RGB", (360, 240), (35, 92, 43))
    draw = ImageDraw.Draw(source)
    for x in range(90, 260, 24):
        for y in range(62, 168, 22):
            draw.ellipse((x - 12, y - 10, x + 12, y + 10), fill=(238, 235, 220))
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(218, 172, 54))
    for y in range(62, 168, 22):
        draw.line((90, y, 258, y), fill=(238, 235, 220), width=2)

    alpha = Image.new("L", source.size, 0)
    ImageDraw.Draw(alpha).rectangle((50, 35, 310, 205), fill=255)

    result = refine_mask_for_target(
        source,
        alpha,
        description="wildflower cluster on hedge",
        instruction="make small bright white wildflowers with yellow centers",
        max_children=12,
    )

    assert result.applied is True
    assert len(result.child_masks) > 1
    for child in result.child_masks:
        ys, xs = np.where(np.asarray(child) > 0)
        assert int(xs.max() - xs.min() + 1) <= 140
        assert int(ys.max() - ys.min() + 1) <= 140


def test_default_refinement_budget_covers_dense_connected_flower_evidence():
    source = Image.new("RGB", (480, 260), (35, 92, 43))
    draw = ImageDraw.Draw(source)
    for x in range(90, 390, 24):
        for y in range(62, 190, 22):
            draw.ellipse((x - 12, y - 10, x + 12, y + 10), fill=(238, 235, 220))
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(218, 172, 54))
    for y in range(62, 190, 22):
        draw.line((90, y, 388, y), fill=(238, 235, 220), width=2)

    alpha = Image.new("L", source.size, 0)
    ImageDraw.Draw(alpha).rectangle((50, 35, 430, 225), fill=255)

    result = refine_mask_for_target(
        source,
        alpha,
        description="wildflower cluster on hedge",
        instruction="make small bright white wildflowers with yellow centers",
    )

    assert result.applied is True
    assert len(result.child_masks) > 1
    assert result.metrics["refined_coverage_pct"] > 0.65


def test_refines_yellow_dandelion_heads_without_flower_keyword():
    source = Image.new("RGB", (320, 220), (76, 112, 52))
    draw = ImageDraw.Draw(source)
    centers = (
        (58, 42),
        (104, 56),
        (152, 48),
        (214, 78),
        (260, 96),
        (90, 138),
        (184, 152),
        (250, 166),
    )
    for cx, cy in centers:
        draw.line((cx, cy + 5, cx - 4, cy + 34), fill=(64, 105, 48), width=2)
        draw.ellipse((cx - 7, cy - 6, cx + 7, cy + 6), fill=(232, 190, 31))
        draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=(176, 130, 18))

    alpha = Image.new("L", source.size, 0)
    ImageDraw.Draw(alpha).rectangle((20, 18, 300, 190), fill=255)

    result = refine_mask_for_target(
        source,
        alpha,
        description="roadside dandelion heads in grass",
        instruction="turn the yellow dots into buttercup meadow rhythm",
    )

    assert result.applied is True
    assert result.strategy == "small_botanical_subject_replacement"
    assert len(result.child_masks) >= 4
    assert result.metrics["refined_coverage_pct"] < 0.25


def test_refined_yellow_child_mask_covers_muted_source_head_footprint():
    source = Image.new("RGB", (140, 100), (76, 112, 52))
    draw = ImageDraw.Draw(source)
    draw.ellipse((50, 36, 84, 64), fill=(156, 154, 132))
    draw.ellipse((60, 43, 74, 57), fill=(232, 190, 31))
    draw.ellipse((65, 48, 69, 52), fill=(176, 130, 18))

    alpha = Image.new("L", source.size, 0)
    ImageDraw.Draw(alpha).rectangle((28, 20, 112, 80), fill=255)

    result = refine_mask_for_target(
        source,
        alpha,
        description="roadside dandelion heads in grass",
        instruction="turn the yellow dots into buttercup flower heads",
    )

    assert result.applied is True
    child = result.child_masks[0]
    child_arr = np.asarray(child)
    parent_area = int(np.asarray(alpha).astype(bool).sum())
    child_area = int((child_arr > 0).sum())

    assert child_arr[50, 52] > 0
    assert child_arr[50, 82] > 0
    assert child_area < parent_area * 0.2
