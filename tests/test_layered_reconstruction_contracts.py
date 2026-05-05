from pathlib import Path

import pytest

from vulca.layers.reconstruction import (
    assert_image_edits_endpoint_allowed,
    load_reconstruction_contracts,
)


CONTRACT_PATH = Path(
    "docs/superpowers/contracts/2026-05-05-layered-scene-reconstruction-prompts.json"
)


def test_loads_required_source_layered_generation_contracts():
    contracts = load_reconstruction_contracts(CONTRACT_PATH)

    assert contracts.schema_version == (
        "2026-05-05.source_layered_generation.prompt_contracts.v1"
    )
    assert contracts.product["workflow_kind"] == "source_conditioned_layered_generation"
    assert contracts.product["not_a_decompose_workflow"] is True
    assert contracts.provider["endpoint"] == "/v1/images/edits"
    assert "/v1/chat/completions" in contracts.provider["forbidden_endpoints"]
    assert contracts.artifact_policy["default_artifact_root"] == (
        ".scratch/source-layered-generation"
    )
    assert [layer.semantic_path for layer in contracts.layers] == [
        "background.sky.clean_blue",
        "background.distant_trees",
        "subject.vehicle.red_car",
        "subject.vehicle.yellow_truck",
        "foreground.guardrail",
        "foreground.grass_bank",
        "foreground.hedge_bush",
        "detail.dry_stems",
        "detail.white_flower_cluster",
        "detail.yellow_dandelion_heads",
        "residual.source_texture",
    ]


def test_rejects_contract_without_residual_layer(tmp_path):
    contract = CONTRACT_PATH.read_text()
    edited = contract.replace(
        '"semantic_path": "residual.source_texture"',
        '"semantic_path": "residual.missing"',
    )
    path = tmp_path / "bad.json"
    path.write_text(edited)

    with pytest.raises(ValueError, match="residual.source_texture"):
        load_reconstruction_contracts(path)


def test_rejects_chat_completions_endpoint_mode(monkeypatch):
    monkeypatch.setenv("VULCA_OPENAI_IMAGE_ENDPOINT", "chat_completions")

    with pytest.raises(ValueError, match="/v1/chat/completions"):
        assert_image_edits_endpoint_allowed()


def test_allows_default_images_edits_endpoint(monkeypatch):
    monkeypatch.delenv("VULCA_OPENAI_IMAGE_ENDPOINT", raising=False)

    assert_image_edits_endpoint_allowed() is None
