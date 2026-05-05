import json

from vulca.layers.reconstruction import write_reconstruction_summary


def test_summary_records_policies_usage_cost_failures_and_gates(tmp_path):
    path = write_reconstruction_summary(
        tmp_path,
        source_image="source.png",
        provider="openai",
        model="gpt-image-2",
        layer_policies={
            "foreground.hedge_bush": {
                "policy": "preserve",
                "status": "completed",
                "mask_area_pct": 40.0,
                "owned_area_pct": 37.5,
                "subtracted_by": ["detail.white_flower_cluster"],
            },
            "detail.white_flower_cluster": {
                "policy": "local_redraw",
                "status": "completed",
                "mask_area_pct": 2.5,
                "owned_area_pct": 2.5,
                "cost_usd": 0.0123,
            },
        },
        usage={"input_tokens": 100, "output_tokens": 200},
        cost={"total_cost_usd": 0.0123, "known": True},
        failures=[],
        quality_gates={
            "ownership_no_overlap": True,
            "residual_fills_unassigned": True,
            "flower_pixels_absent_from_parent_hedge": True,
        },
    )

    data = json.loads(path.read_text())
    assert data["schema_version"] == (
        "2026-05-05.source_layered_generation.summary.v1"
    )
    assert data["source_image"] == "source.png"
    assert data["provider"] == "openai"
    assert data["model"] == "gpt-image-2"
    assert data["layer_policies"]["foreground.hedge_bush"]["policy"] == "preserve"
    assert data["usage"]["input_tokens"] == 100
    assert data["cost"]["total_cost_usd"] == 0.0123
    assert data["failures"] == []
    assert data["quality_gates"]["flower_pixels_absent_from_parent_hedge"] is True
