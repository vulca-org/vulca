from vulca.layers.redraw_review import classify_redraw_review


def test_ready_for_review_uses_source_pasteback_as_primary_after():
    review = classify_redraw_review(
        {
            "file": "/tmp/layer.png",
            "source_pasteback_path": "/tmp/layer_on_source.png",
            "quality_gate_passed": True,
        }
    )

    assert review.state == "ready_for_review"
    assert review.primary_after_path == "/tmp/layer_on_source.png"
    assert review.layer_asset_path == "/tmp/layer.png"
    assert review.show_as_final is True
    assert review.quality_gate_passed is True
    assert review.warnings == ()


def test_technical_preview_keeps_pasteback_but_marks_quality_failure():
    review = classify_redraw_review(
        {
            "file": "/tmp/layer.png",
            "source_pasteback_path": "/tmp/layer_on_source.png",
            "quality_gate_passed": False,
            "quality_failures": ["background_bleed"],
        }
    )

    assert review.state == "technical_preview"
    assert review.primary_after_path == "/tmp/layer_on_source.png"
    assert review.show_as_final is True
    assert review.quality_gate_passed is False
    assert review.warnings == ("quality_gate_failed: background_bleed",)


def test_unknown_quality_preview_tolerates_missing_advisory():
    review = classify_redraw_review(
        {
            "file": "/tmp/layer.png",
            "source_pasteback_path": "/tmp/layer_on_source.png",
        }
    )

    assert review.state == "unknown_quality_preview"
    assert review.primary_after_path == "/tmp/layer_on_source.png"
    assert review.show_as_final is True
    assert review.quality_gate_passed is None
    assert review.warnings == ("quality_gate_missing",)


def test_layer_only_result_does_not_promote_sparse_asset_as_final():
    review = classify_redraw_review({"file": "/tmp/layer.png"})

    assert review.state == "layer_only_result"
    assert review.primary_after_path == "/tmp/layer.png"
    assert review.layer_asset_path == "/tmp/layer.png"
    assert review.show_as_final is False
    assert review.warnings == ("source_pasteback_path_missing",)


def test_pasteback_warning_preserves_layer_asset_for_inspector():
    review = classify_redraw_review(
        {
            "file": "/tmp/layer.png",
            "source_pasteback_error": "source size (10, 10) != layer size (20, 20)",
        }
    )

    assert review.state == "pasteback_warning"
    assert review.primary_after_path == "/tmp/layer.png"
    assert review.layer_asset_path == "/tmp/layer.png"
    assert review.show_as_final is False
    assert review.warnings == (
        "source_pasteback_error: source size (10, 10) != layer size (20, 20)",
    )


def test_to_dict_matches_external_webapp_payload_shape():
    review = classify_redraw_review(
        {
            "file": "/tmp/layer.png",
            "source_pasteback_path": "/tmp/layer_on_source.png",
            "quality_gate_passed": True,
            "refinement_applied": True,
            "refined_child_count": 4,
        }
    )

    assert review.to_dict() == {
        "state": "ready_for_review",
        "primary_after_path": "/tmp/layer_on_source.png",
        "layer_asset_path": "/tmp/layer.png",
        "source_pasteback_path": "/tmp/layer_on_source.png",
        "source_pasteback_error": "",
        "show_as_final": True,
        "quality_gate_passed": True,
        "warnings": [],
        "refinement_applied": True,
        "refined_child_count": 4,
    }
