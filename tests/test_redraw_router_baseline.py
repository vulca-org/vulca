import json


def _case(**overrides):
    record = {
        "case_id": "redraw_example",
        "case_type": "redraw_case",
        "route": {
            "requested": "auto",
            "chosen": "inpaint",
            "redraw_route": "sparse_bbox_crop",
            "geometry_redraw_route": "sparse_bbox_crop",
        },
        "geometry": {
            "area_pct": 0.64,
            "bbox_fill": 1.0,
            "component_count": 1,
            "sparse_detected": True,
        },
        "quality": {
            "gate_passed": True,
            "failures": [],
            "metrics": {},
        },
        "refinement": {
            "applied": False,
            "reason": "no_target_profile",
            "strategy": "none",
            "child_count": 0,
            "mask_granularity_score": 0.0,
        },
        "artifacts": {
            "source_pasteback_path": "/tmp/redraw_on_source.png",
        },
        "review": {
            "human_accept": None,
            "failure_type": "",
            "preferred_action": "",
        },
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(record.get(key), dict):
            nested = dict(record[key])
            nested.update(value)
            record[key] = nested
        else:
            record[key] = value
    return record


def test_label_oracle_maps_seed_failures_to_required_actions():
    from vulca.layers.redraw_router_baseline import recommend_action

    expected = {
        "mask_too_broad": "adjust_mask",
        "route_error": "adjust_route",
        "pasteback_mismatch": "manual_review",
        "over_split": "fallback_to_original",
        "under_split": "fallback_to_agent",
    }

    for failure_type, action in expected.items():
        result = recommend_action(
            _case(review={"failure_type": failure_type, "preferred_action": ""}),
            policy_name="label_oracle",
        )
        assert result.recommended_action == action
        assert result.failure_hint == failure_type


def test_label_oracle_accepts_human_accept_before_failure_label():
    from vulca.layers.redraw_router_baseline import recommend_action

    result = recommend_action(
        _case(
            review={
                "human_accept": True,
                "failure_type": "mask_too_broad",
                "preferred_action": "adjust_mask",
            }
        ),
        policy_name="label_oracle",
    )

    assert result.recommended_action == "accept"
    assert result.accept_prediction is True


def test_observable_signal_accepts_passed_quality_with_pasteback():
    from vulca.layers.redraw_router_baseline import recommend_action

    result = recommend_action(
        _case(review={"failure_type": "route_error", "preferred_action": "adjust_route"}),
        policy_name="observable_signal",
    )

    assert result.recommended_action == "accept"
    assert result.failure_hint == ""
    assert result.accept_prediction is True


def test_observable_signal_routes_quality_failures_to_mask_adjustment():
    from vulca.layers.redraw_router_baseline import recommend_action

    result = recommend_action(
        _case(
            quality={
                "gate_passed": False,
                "failures": ["mask_too_broad_for_target"],
                "metrics": {},
            }
        ),
        policy_name="observable_signal",
    )

    assert result.recommended_action == "adjust_mask"
    assert result.failure_hint == "mask_too_broad"
    assert result.accept_prediction is False


def test_observable_signal_routes_geometry_mismatch_to_route_adjustment():
    from vulca.layers.redraw_router_baseline import recommend_action

    result = recommend_action(
        _case(
            route={
                "requested": "auto",
                "chosen": "inpaint",
                "redraw_route": "dense_full_canvas",
                "geometry_redraw_route": "sparse_bbox_crop",
            }
        ),
        policy_name="observable_signal",
    )

    assert result.recommended_action == "adjust_route"
    assert result.failure_hint == "route_error"


def test_observable_signal_does_not_read_review_labels():
    from vulca.layers.redraw_router_baseline import recommend_action

    class ReviewTrap(dict):
        def __getitem__(self, key):
            if key == "review":
                raise AssertionError("observable_signal must not read review")
            return super().__getitem__(key)

        def get(self, key, default=None):
            if key == "review":
                raise AssertionError("observable_signal must not read review")
            return super().get(key, default)

    result = recommend_action(
        ReviewTrap(
            _case(
                quality={
                    "gate_passed": False,
                    "failures": ["large_white_component"],
                    "metrics": {},
                }
            )
        ),
        policy_name="observable_signal",
    )

    assert result.recommended_action == "adjust_mask"
    assert result.failure_hint == "large_white_component"


def test_evaluate_records_reports_action_accuracy_and_confusion():
    from vulca.layers.redraw_router_baseline import evaluate_records

    records = [
        _case(
            case_id="one",
            review={
                "human_accept": False,
                "failure_type": "mask_too_broad",
                "preferred_action": "adjust_mask",
            },
        ),
        _case(
            case_id="two",
            review={
                "human_accept": False,
                "failure_type": "route_error",
                "preferred_action": "adjust_route",
            },
        ),
    ]

    report = evaluate_records(records, policy_name="label_oracle")

    assert report["policy_name"] == "label_oracle"
    assert report["case_count"] == 2
    assert report["coverage"] == 1.0
    assert report["action_accuracy"] == 1.0
    assert report["accept_reject_accuracy"] == 1.0
    assert report["failure_classification_accuracy"] == 1.0
    assert report["failure_macro_f1"] == 1.0
    assert report["confusion_by_failure"]["mask_too_broad"]["adjust_mask"] == 1
    assert report["confusion_by_failure"]["route_error"]["adjust_route"] == 1


def test_cli_scores_jsonl_without_provider_calls(tmp_path, capsys):
    from scripts.redraw_router_baseline_eval import main

    case_log = tmp_path / "redraw_cases.jsonl"
    case_log.write_text(
        "\n".join(
            [
                json.dumps(
                    _case(
                        case_id="one",
                        review={
                            "human_accept": False,
                            "failure_type": "mask_too_broad",
                            "preferred_action": "adjust_mask",
                        },
                    )
                )
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    assert main([str(case_log), "--policy", "label_oracle"]) == 0
    output = json.loads(capsys.readouterr().out)

    assert output["policy_name"] == "label_oracle"
    assert output["case_count"] == 1
    assert output["action_accuracy"] == 1.0
