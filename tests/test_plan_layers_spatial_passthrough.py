from vulca.layers.prompt import parse_v2_response


def test_position_and_coverage_pass_through():
    raw = {"layers": [
        {"name": "far", "description": "x", "z_index": 1,
         "blend_mode": "normal", "dominant_colors": [], "content_type": "subject",
         "position": "upper 30%", "coverage": "20-30%",
         "regeneration_prompt": "distant mountains"},
    ]}
    layers = parse_v2_response(raw)
    assert len(layers) == 1
    li = layers[0]
    assert li.position == "upper 30%"
    assert li.coverage == "20-30%"


def test_missing_spatial_fields_default_to_empty():
    raw = {"layers": [
        {"name": "bg", "description": "paper", "z_index": 0,
         "content_type": "background"},
    ]}
    layers = parse_v2_response(raw)
    assert layers[0].position == ""
    assert layers[0].coverage == ""
