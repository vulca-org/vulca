from PIL import Image

from vulca.layers.redraw_quality import evaluate_redraw_quality


def _rgba(size=(200, 200), color=(120, 80, 60), box=(80, 80, 40, 40)):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    patch = Image.new("RGBA", (box[2], box[3]), (*color, 255))
    img.alpha_composite(patch, (box[0], box[1]))
    return img


def test_quality_gate_flags_large_white_block():
    source = _rgba()
    output = _rgba(color=(255, 255, 255), box=(0, 0, 200, 200))
    report = evaluate_redraw_quality(source, output)
    assert not report.passed
    assert "large_white_component" in report.failures


def test_quality_gate_flags_alpha_expansion():
    source = _rgba(box=(90, 90, 20, 20))
    output = _rgba(box=(20, 20, 160, 160))
    report = evaluate_redraw_quality(source, output)
    assert not report.passed
    assert "alpha_bbox_expanded" in report.failures


def test_quality_gate_passes_same_alpha_reasonable_color():
    source = _rgba(color=(120, 80, 60))
    output = _rgba(color=(130, 90, 70))
    report = evaluate_redraw_quality(source, output)
    assert report.passed


def test_quality_gate_flags_broad_small_bright_target_without_refinement():
    source = _rgba(
        size=(240, 180),
        color=(35, 92, 43),
        box=(28, 25, 188, 98),
    )
    output = _rgba(
        size=(240, 180),
        color=(242, 240, 224),
        box=(28, 25, 188, 98),
    )

    report = evaluate_redraw_quality(
        source,
        output,
        description="wildflower cluster on hedge",
        instruction="small bright white wildflowers with yellow centers",
        refinement_applied=False,
        refined_child_count=0,
    )

    assert not report.passed
    assert "mask_too_broad_for_target" in report.failures
    assert report.metrics["refined_child_count"] == 0
    assert report.metrics["mask_granularity_score"] == 0
