import json

import pytest


def _style_constraints():
    return {
        "positive": ["clean readable layers", "consistent daylight"],
        "negative": ["flat single-image output"],
        "palette": ["blue sky", "green hedge", "white flowers"],
        "composition": ["roadside guardrail above flower bank"],
        "required_motifs": ["sky", "guardrail", "flower bank"],
        "prohibited_motifs": [],
    }


def _layer_plan():
    return {
        "source": "visual_plan",
        "desired_layer_count": 2,
        "layers": [
            {
                "semantic_path": "background.sky",
                "display_name": "Sky",
                "role": "background",
                "z_index": 0,
                "generation_prompt_ref": "prompts/layers/background.sky.txt",
                "alpha_strategy": "opaque_full_canvas",
                "required": True,
            },
            {
                "semantic_path": "foreground.flowers",
                "display_name": "White flowers",
                "role": "foreground",
                "z_index": 10,
                "generation_prompt_ref": "prompts/layers/foreground.flowers.txt",
                "alpha_strategy": "transparent_subject",
                "required": True,
            },
        ],
    }


def _prompt_stack():
    return {
        "system_prompt_path": "prompts/system.txt",
        "plan_prompt_path": "prompts/plan.txt",
        "layer_prompt_refs": [
            {
                "semantic_path": "background.sky",
                "prompt_path": "prompts/layers/background.sky.txt",
                "prompt_text_hash": "sha256:sky",
            },
            {
                "semantic_path": "foreground.flowers",
                "prompt_path": "prompts/layers/foreground.flowers.txt",
                "prompt_text_hash": "sha256:flowers",
            },
        ],
        "negative_prompt_path": "prompts/negative.txt",
        "provider_request": {
            "size": "1024x1024",
            "quality": "high",
            "output_format": "png",
        },
    }


def _layers():
    return [
        {
            "semantic_path": "background.sky",
            "asset_path": "runs/layered/case/background.sky.png",
            "mask_path": "",
            "alpha_path": "",
            "visible": True,
            "locked": False,
            "status": "generated",
        },
        {
            "semantic_path": "foreground.flowers",
            "asset_path": "runs/layered/case/foreground.flowers.png",
            "mask_path": "runs/layered/case/foreground.flowers.mask.png",
            "alpha_path": "runs/layered/case/foreground.flowers.alpha.png",
            "visible": True,
            "locked": False,
            "status": "generated",
        },
    ]


def test_build_layer_generate_case_minimal_schema():
    from vulca.layers.layer_generate_cases import build_layer_generate_case

    record = build_layer_generate_case(
        user_intent="Create a layered roadside botanical scene.",
        tradition="ipad_cartoon_showcase",
        style_constraints=_style_constraints(),
        layer_plan=_layer_plan(),
        prompt_stack=_prompt_stack(),
        provider="openai",
        model="gpt-image-2",
        artifact_dir="runs/layered/case",
        layer_manifest_path="runs/layered/case/manifest.json",
        layers=_layers(),
        composite_path="runs/layered/case/composite.png",
        preview_path="runs/layered/case/preview.png",
        created_at="2026-05-05T12:00:00Z",
    )

    assert record["schema_version"] == 1
    assert record["case_type"] == "layer_generate_case"
    assert record["case_id"].startswith("layer_generate_20260505T120000Z_")
    assert record["created_at"] == "2026-05-05T12:00:00Z"
    assert record["inputs"]["user_intent"] == (
        "Create a layered roadside botanical scene."
    )
    assert record["inputs"]["tradition"] == "ipad_cartoon_showcase"
    assert record["inputs"]["provider"] == "openai"
    assert record["inputs"]["model"] == "gpt-image-2"
    assert record["inputs"]["style_constraints"]["positive"] == [
        "clean readable layers",
        "consistent daylight",
    ]
    assert record["inputs"]["layer_plan"]["desired_layer_count"] == 2
    assert record["inputs"]["prompt_stack"]["provider_request"]["quality"] == "high"
    assert record["decisions"]["layer_count"] == {
        "planned": 2,
        "generated": 2,
        "accepted": 0,
    }
    assert record["decisions"]["semantic_roles"] == [
        {
            "semantic_path": "background.sky",
            "role": "background",
            "required": True,
        },
        {
            "semantic_path": "foreground.flowers",
            "role": "foreground",
            "required": True,
        },
    ]
    assert record["decisions"]["z_index"][0] == {
        "semantic_path": "background.sky",
        "z_index": 0,
        "reason": "layer_plan",
    }
    assert record["decisions"]["mask_alpha_strategy"]["canvas_mode"] == (
        "full_canvas_rgba_layers"
    )
    assert record["decisions"]["fallback_decisions"] == []
    assert record["outputs"]["artifact_dir"] == "runs/layered/case"
    assert record["outputs"]["layer_manifest_path"] == (
        "runs/layered/case/manifest.json"
    )
    assert record["outputs"]["layers"][1]["asset_path"].endswith(
        "foreground.flowers.png"
    )
    assert record["outputs"]["composite_path"] == "runs/layered/case/composite.png"
    assert record["outputs"]["preview_path"] == "runs/layered/case/preview.png"
    assert record["learning_targets"] == {
        "tiny_model": {
            "failure_classification": "",
            "quality_score": None,
            "route_recommendation": "",
        },
        "tiny_agent": {
            "next_action_policy": "",
        },
    }
    assert record["review"] == {
        "human_accept": None,
        "failure_type": "",
        "preferred_action": "",
        "reviewer": "",
        "reviewed_at": "",
    }


def test_layer_generate_case_rejects_redraw_route_geometry_refinement_fields():
    from vulca.layers.layer_generate_cases import build_layer_generate_case

    with pytest.raises(ValueError, match="forbidden sibling case field"):
        build_layer_generate_case(
            user_intent="Generate layers.",
            tradition="test",
            style_constraints=_style_constraints(),
            layer_plan=_layer_plan(),
            prompt_stack=_prompt_stack(),
            provider="openai",
            model="gpt-image-2",
            layer_manifest_path="runs/layered/case/manifest.json",
            layers=_layers(),
            decisions={"route": {"chosen": "inpaint"}},
            created_at="2026-05-05T12:00:00Z",
        )

    with pytest.raises(ValueError, match="forbidden sibling case field"):
        build_layer_generate_case(
            user_intent="Generate layers.",
            tradition="test",
            style_constraints=_style_constraints(),
            layer_plan={"desired_layer_count": 1, "detector": "sam", "layers": []},
            prompt_stack=_prompt_stack(),
            provider="openai",
            model="gpt-image-2",
            layer_manifest_path="runs/layered/case/manifest.json",
            layers=_layers(),
            created_at="2026-05-05T12:00:00Z",
        )


def test_layer_generate_case_requires_per_layer_asset_paths():
    from vulca.layers.layer_generate_cases import build_layer_generate_case

    bad_layers = [{"semantic_path": "background.sky"}]

    with pytest.raises(ValueError, match="asset_path"):
        build_layer_generate_case(
            user_intent="Generate layers.",
            tradition="test",
            style_constraints=_style_constraints(),
            layer_plan=_layer_plan(),
            prompt_stack=_prompt_stack(),
            provider="openai",
            model="gpt-image-2",
            layer_manifest_path="runs/layered/case/manifest.json",
            layers=bad_layers,
            created_at="2026-05-05T12:00:00Z",
        )


def test_layer_generate_case_taxonomy_rejects_unknown_labels():
    from vulca.layers.layer_generate_cases import (
        validate_failure_type,
        validate_preferred_action,
        validate_route_recommendation,
    )

    assert validate_failure_type("") == ""
    assert validate_failure_type("style_drift") == "style_drift"
    with pytest.raises(ValueError, match="unsupported layer_generate failure_type"):
        validate_failure_type("pasteback_mismatch")

    assert validate_preferred_action("") == ""
    assert validate_preferred_action("split_layer") == "split_layer"
    with pytest.raises(ValueError, match="unsupported layer_generate preferred_action"):
        validate_preferred_action("adjust_mask")

    assert validate_route_recommendation("") == ""
    assert validate_route_recommendation("direct_generation") == "direct_generation"
    with pytest.raises(
        ValueError,
        match="unsupported layer_generate route_recommendation",
    ):
        validate_route_recommendation("sparse_bbox_crop")


def test_layer_generate_case_learning_targets_round_trip():
    from vulca.layers.layer_generate_cases import build_layer_generate_case

    record = build_layer_generate_case(
        user_intent="Create layers.",
        tradition="test",
        style_constraints=_style_constraints(),
        layer_plan=_layer_plan(),
        prompt_stack=_prompt_stack(),
        provider="openai",
        model="gpt-image-2",
        layer_manifest_path="runs/layered/case/manifest.json",
        layers=_layers(),
        learning_targets={
            "tiny_model": {
                "failure_classification": "style_drift",
                "quality_score": 0.42,
                "route_recommendation": "adjust_prompt",
            },
            "tiny_agent": {
                "next_action_policy": "adjust_prompt",
            },
        },
        failure_type="style_drift",
        preferred_action="adjust_prompt",
        reviewer="human:reviewer-a",
        reviewed_at="2026-05-05T13:00:00Z",
        created_at="2026-05-05T12:00:00Z",
    )

    assert record["learning_targets"] == {
        "tiny_model": {
            "failure_classification": "style_drift",
            "quality_score": 0.42,
            "route_recommendation": "adjust_prompt",
        },
        "tiny_agent": {
            "next_action_policy": "adjust_prompt",
        },
    }
    assert record["review"] == {
        "human_accept": None,
        "failure_type": "style_drift",
        "preferred_action": "adjust_prompt",
        "reviewer": "human:reviewer-a",
        "reviewed_at": "2026-05-05T13:00:00Z",
    }


def test_layer_generate_case_id_is_stable_for_same_inputs():
    from vulca.layers.layer_generate_cases import build_layer_generate_case

    kwargs = {
        "user_intent": "Create layers.",
        "tradition": "test",
        "style_constraints": _style_constraints(),
        "layer_plan": _layer_plan(),
        "prompt_stack": _prompt_stack(),
        "provider": "openai",
        "model": "gpt-image-2",
        "layer_manifest_path": "runs/layered/case/manifest.json",
        "layers": _layers(),
        "created_at": "2026-05-05T12:00:00Z",
    }
    first = build_layer_generate_case(**kwargs)
    second = build_layer_generate_case(**kwargs)
    changed = build_layer_generate_case(**{**kwargs, "model": "other-model"})

    assert first["case_id"] == second["case_id"]
    assert first["case_id"] != changed["case_id"]


def test_append_layer_generate_case_writes_one_json_line(tmp_path):
    from vulca.layers.layer_generate_cases import append_layer_generate_case

    path = tmp_path / "cases" / "layer_generate_cases.jsonl"
    record = {
        "schema_version": 1,
        "case_type": "layer_generate_case",
        "case_id": "layer_generate_example",
    }

    written = append_layer_generate_case(str(path), record)

    assert written == str(path)
    lines = path.read_text().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == record


def test_layer_generate_case_uses_sibling_schema_not_redraw_or_decompose():
    from vulca.layers.layer_generate_cases import build_layer_generate_case

    record = build_layer_generate_case(
        user_intent="Create layers.",
        tradition="test",
        style_constraints=_style_constraints(),
        layer_plan=_layer_plan(),
        prompt_stack=_prompt_stack(),
        provider="openai",
        model="gpt-image-2",
        layer_manifest_path="runs/layered/case/manifest.json",
        layers=_layers(),
        created_at="2026-05-05T12:00:00Z",
    )

    assert record["case_type"] == "layer_generate_case"
    assert "route" not in record
    assert "geometry" not in record
    assert "refinement" not in record
    assert "artifacts" not in record
    assert "inputs" in record
    assert "decisions" in record
    assert "outputs" in record
    assert record["outputs"]["layer_manifest_path"].endswith("manifest.json")
