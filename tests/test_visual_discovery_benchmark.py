from __future__ import annotations

import base64
import json
import importlib
import os
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _tiny_png_b64() -> str:
    return base64.b64encode(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\rIDATx\x9cc\xf8\x0f\x00"
        b"\x01\x01\x01\x00\x18\xdd\x8d\xb0"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    ).decode("ascii")


def test_experiment_projects_match_protocol_domains():
    from scripts.visual_discovery_benchmark import build_experiment_projects

    projects = build_experiment_projects()

    assert [project.slug for project in projects] == [
        "premium-tea-packaging",
        "spiritual-editorial-poster",
        "cultural-material-campaign",
    ]
    assert "xieyi restraint" in projects[0].prompt
    assert "spiritual but non-religious" in projects[1].prompt
    assert "material references" in projects[2].prompt


def test_build_conditions_a_through_d():
    from scripts.visual_discovery_benchmark import (
        build_conditions,
        build_experiment_projects,
        select_direction_card,
    )

    project = build_experiment_projects()[0]
    card = select_direction_card(project)

    conditions = build_conditions(project.prompt, card)

    assert [condition["id"] for condition in conditions] == ["A", "B", "C", "D"]
    assert conditions[0]["label"] == "User prompt only"
    assert conditions[0]["source_card_id"] == ""
    assert "cultural terms" in conditions[1]["label"].lower()
    assert card.culture_terms[0] in conditions[1]["prompt"]
    assert "Visual operations:" in conditions[2]["prompt"]
    assert conditions[3]["label"] == "Full direction-card prompt"
    assert conditions[3]["negative_prompt"]
    assert conditions[3]["evaluation_focus"]["L1"]
    assert conditions[3]["source_card_id"] == card.id


def test_write_experiment_dry_run_artifacts(tmp_path):
    from scripts.visual_discovery_benchmark import write_experiment_dry_run

    result = write_experiment_dry_run(
        output_root=tmp_path,
        slug="premium-tea-packaging",
        date="2026-04-30",
    )

    out_dir = Path(result["output_dir"])
    assert out_dir == tmp_path / "2026-04-30-premium-tea-packaging"
    for condition_id in ["A", "B", "C", "D"]:
        assert (out_dir / "prompts" / f"{condition_id}.txt").exists()
    assert (out_dir / "images" / "README.md").exists()
    assert (out_dir / "evaluations" / "README.md").exists()

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "0.1"
    assert manifest["experiment"] == "cultural-term-efficacy"
    assert manifest["mode"] == "dry_run"
    assert manifest["provider_execution"] == "disabled"
    assert manifest["project"]["slug"] == "premium-tea-packaging"
    assert [condition["id"] for condition in manifest["conditions"]] == [
        "A",
        "B",
        "C",
        "D",
    ]
    assert {provider["execution"] for provider in manifest["providers"]} == {
        "not_run"
    }

    human_ranking = json.loads(
        (out_dir / "human_ranking.json").read_text(encoding="utf-8")
    )
    provider_costs = json.loads(
        (out_dir / "provider_costs.json").read_text(encoding="utf-8")
    )
    assert human_ranking["status"] == "not_collected"
    assert provider_costs["status"] == "not_collected"
    assert "No image quality conclusion" in (
        out_dir / "summary.md"
    ).read_text(encoding="utf-8")


def test_real_provider_execution_fails_closed():
    from scripts.visual_discovery_benchmark import run_real_provider_experiment

    with pytest.raises(RuntimeError, match="explicit opt-in"):
        run_real_provider_experiment(real_provider=False)


def test_harness_forces_litellm_local_cost_map(monkeypatch):
    import scripts.visual_discovery_benchmark as benchmark

    monkeypatch.delenv("LITELLM_LOCAL_MODEL_COST_MAP", raising=False)
    importlib.reload(benchmark)

    assert os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] == "true"


def test_real_provider_requires_env_key_before_provider_construction(
    monkeypatch, tmp_path
):
    import scripts.visual_discovery_benchmark as benchmark

    monkeypatch.delenv("VULCA_REAL_PROVIDER_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def fail_if_constructed(**kwargs):
        raise AssertionError("provider should not be constructed")

    monkeypatch.setattr(benchmark, "OpenAIImageProvider", fail_if_constructed)

    with pytest.raises(RuntimeError, match="VULCA_REAL_PROVIDER_API_KEY"):
        benchmark.run_real_provider_experiment(
            real_provider=True,
            provider="openai",
            output_root=tmp_path,
            slug="premium-tea-packaging",
            date="2026-04-30",
        )


def test_real_provider_rejects_unsupported_provider(monkeypatch, tmp_path):
    import scripts.visual_discovery_benchmark as benchmark

    monkeypatch.setenv("VULCA_REAL_PROVIDER_API_KEY", "test-token")

    with pytest.raises(ValueError, match="supported real provider"):
        benchmark.run_real_provider_experiment(
            real_provider=True,
            provider="gemini",
            output_root=tmp_path,
            slug="premium-tea-packaging",
            date="2026-04-30",
        )


def test_real_provider_rejects_malformed_base_url_before_provider_construction(
    monkeypatch, tmp_path
):
    import scripts.visual_discovery_benchmark as benchmark

    monkeypatch.setenv("VULCA_REAL_PROVIDER_API_KEY", "test-token")
    monkeypatch.setenv(
        "VULCA_REAL_PROVIDER_BASE_URL",
        "gateway.example/v1?token=secret#frag",
    )

    def fail_if_constructed(**kwargs):
        raise AssertionError("provider should not be constructed")

    monkeypatch.setattr(benchmark, "OpenAIImageProvider", fail_if_constructed)

    with pytest.raises(RuntimeError, match="absolute http"):
        benchmark.run_real_provider_experiment(
            real_provider=True,
            provider="openai",
            output_root=tmp_path,
            slug="premium-tea-packaging",
            date="2026-04-30",
        )


def test_real_provider_rejects_absolute_base_url_with_whitespace_before_provider_construction(
    monkeypatch, tmp_path
):
    import scripts.visual_discovery_benchmark as benchmark

    monkeypatch.setenv("VULCA_REAL_PROVIDER_API_KEY", "test-token")
    monkeypatch.setenv(
        "VULCA_REAL_PROVIDER_BASE_URL",
        "https://exa mple.com/v1?token=secret#frag",
    )

    def fail_if_constructed(**kwargs):
        raise AssertionError("provider should not be constructed")

    monkeypatch.setattr(benchmark, "OpenAIImageProvider", fail_if_constructed)

    with pytest.raises(RuntimeError, match="valid absolute http"):
        benchmark.run_real_provider_experiment(
            real_provider=True,
            provider="openai",
            output_root=tmp_path,
            slug="premium-tea-packaging",
            date="2026-04-30",
        )


def test_real_provider_writes_images_metadata_and_costs(monkeypatch, tmp_path):
    import scripts.visual_discovery_benchmark as benchmark
    from vulca.providers.base import ImageResult

    constructed = {}
    calls = []

    class FakeOpenAIProvider:
        def __init__(self, *, api_key, model, base_url):
            constructed.update(
                {"api_key": api_key, "model": model, "base_url": base_url}
            )

        async def generate(
            self,
            *,
            prompt,
            raw_prompt,
            width,
            height,
            output_format,
            negative_prompt="",
        ):
            condition_id = chr(ord("A") + len(calls))
            calls.append(
                {
                    "condition_id": condition_id,
                    "prompt": prompt,
                    "raw_prompt": raw_prompt,
                    "width": width,
                    "height": height,
                    "output_format": output_format,
                    "negative_prompt": negative_prompt,
                }
            )
            return ImageResult(
                image_b64=_tiny_png_b64(),
                mime="image/png",
                metadata={
                    "endpoint": "generations",
                    "condition_id": condition_id,
                    "cost_usd": 0.01,
                },
            )

    monkeypatch.setattr(benchmark, "OpenAIImageProvider", FakeOpenAIProvider)
    monkeypatch.setenv("VULCA_REAL_PROVIDER_API_KEY", "test-token")
    monkeypatch.setenv(
        "VULCA_REAL_PROVIDER_BASE_URL",
        "https://gateway.example/v1/ignored?token=nope",
    )
    monkeypatch.setenv("VULCA_REAL_PROVIDER_MODEL", "gpt-image-2")

    benchmark.run_real_provider_experiment(
        real_provider=True,
        provider="openai",
        output_root=tmp_path,
        slug="premium-tea-packaging",
        date="2026-04-30",
    )

    out_dir = tmp_path / "2026-04-30-premium-tea-packaging"
    assert constructed == {
        "api_key": "test-token",
        "model": "gpt-image-2",
        "base_url": "https://gateway.example",
    }
    assert len(calls) == 4
    for condition_id in ["A", "B", "C", "D"]:
        assert (out_dir / "prompts" / f"{condition_id}.txt").exists()
        assert (out_dir / "images" / f"{condition_id}.png").exists()
    images_readme = (out_dir / "images" / "README.md").read_text(encoding="utf-8")
    assert "Real provider run" in images_readme
    assert "not generated" not in images_readme

    manifest_text = (out_dir / "manifest.json").read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    assert manifest["mode"] == "real_provider"
    assert manifest["provider_execution"] == "enabled"
    assert manifest["real_provider"] == {
        "provider": "openai",
        "model": "gpt-image-2",
        "base_url": "https://gateway.example",
    }
    assert "test-token" not in manifest_text

    metadata = json.loads(
        (out_dir / "images" / "metadata.json").read_text(encoding="utf-8")
    )
    assert metadata["provider"] == "openai"
    assert metadata["model"] == "gpt-image-2"
    assert [item["id"] for item in metadata["conditions"]] == [
        "A",
        "B",
        "C",
        "D",
    ]
    assert metadata["conditions"][0]["image_path"] == "images/A.png"

    provider_costs = json.loads(
        (out_dir / "provider_costs.json").read_text(encoding="utf-8")
    )
    assert provider_costs["status"] == "collected"
    assert provider_costs["providers"] == [
        {
            "provider": "openai",
            "model": "gpt-image-2",
            "base_url": "https://gateway.example",
            "conditions": [
                {"condition_id": "A", "cost_usd": 0.01},
                {"condition_id": "B", "cost_usd": 0.01},
                {"condition_id": "C", "cost_usd": 0.01},
                {"condition_id": "D", "cost_usd": 0.01},
            ],
        }
    ]
    assert provider_costs["total_usd"] == 0.04
