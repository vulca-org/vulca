from PIL import Image

from vulca.layers.redraw_strategy import (
    RedrawRoute,
    analyze_alpha_geometry,
    choose_redraw_route,
)


def _alpha(size=(1000, 1000), boxes=()):
    img = Image.new("L", size, 0)
    for x, y, w, h in boxes:
        img.paste(Image.new("L", (w, h), 255), (x, y))
    return img


def test_dense_layer_routes_full_canvas():
    geom = analyze_alpha_geometry(_alpha(boxes=[(100, 100, 700, 700)]))
    assert geom.area_pct == 49.0
    assert geom.component_count == 1
    assert choose_redraw_route(geom).route == RedrawRoute.DENSE_FULL_CANVAS


def test_sparse_single_routes_bbox_crop():
    geom = analyze_alpha_geometry(_alpha(boxes=[(420, 410, 120, 120)]))
    plan = choose_redraw_route(geom)
    assert geom.area_pct == 1.44
    assert geom.component_count == 1
    assert plan.route == RedrawRoute.SPARSE_BBOX_CROP
    assert plan.crop_boxes[0].w > 120
    assert plan.crop_boxes[0].h > 120


def test_sparse_multi_routes_per_component():
    geom = analyze_alpha_geometry(
        _alpha(boxes=[(50, 50, 80, 80), (450, 60, 80, 80), (850, 70, 80, 80)])
    )
    plan = choose_redraw_route(geom)
    assert geom.component_count == 3
    assert geom.bbox_fill < 0.5
    assert plan.route == RedrawRoute.SPARSE_PER_INSTANCE
    assert len(plan.crop_boxes) == 3
