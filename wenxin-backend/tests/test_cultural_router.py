"""Test cultural router."""
from __future__ import annotations

import json
import os
import tempfile
from unittest.mock import patch

import pytest

from app.prototype.agents.critic_config import DIMENSIONS
from app.prototype.cultural_pipelines.cultural_weights import (
    KNOWN_TRADITIONS,
    _get_fallback_weights,
    get_known_traditions,
    get_weights,
    get_all_weight_tables,
)
from app.prototype.cultural_pipelines.pipeline_router import (
    CulturalPipelineRouter,
    PipelineVariant,
    _VARIANTS,
    _TRADITION_TO_VARIANT,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def router() -> CulturalPipelineRouter:
    return CulturalPipelineRouter()


# All 9 known traditions (excluding "default" which is meta)
ALL_TRADITIONS: list[str] = [
    "african_traditional",
    "chinese_gongbi",
    "chinese_xieyi",
    "default",
    "islamic_geometric",
    "japanese_traditional",
    "south_asian",
    "watercolor",
    "western_academic",
]


# ---------------------------------------------------------------------------
# 1. get_weights: each tradition sums to ~1.0
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("tradition", ALL_TRADITIONS)
def test_weights_sum_to_one(tradition: str) -> None:
    """Every tradition's weights must sum to approximately 1.0."""
    weights = get_weights(tradition)
    total = sum(weights.values())
    assert abs(total - 1.0) < 1e-6, (
        f"Tradition '{tradition}' weights sum to {total}, expected ~1.0"
    )


@pytest.mark.parametrize("tradition", ALL_TRADITIONS)
def test_weights_have_all_dimensions(tradition: str) -> None:
    """Every tradition must provide a weight for each L1-L5 dimension."""
    weights = get_weights(tradition)
    for dim in DIMENSIONS:
        assert dim in weights, f"Tradition '{tradition}' missing dimension '{dim}'"
        assert isinstance(weights[dim], float), (
            f"Tradition '{tradition}' dimension '{dim}' is not a float"
        )


@pytest.mark.parametrize("tradition", ALL_TRADITIONS)
def test_weights_all_positive(tradition: str) -> None:
    """All weights must be > 0."""
    weights = get_weights(tradition)
    for dim, val in weights.items():
        assert val > 0, f"Tradition '{tradition}' dimension '{dim}' weight is {val}"


# ---------------------------------------------------------------------------
# 2. Unknown tradition falls back to default weights
# ---------------------------------------------------------------------------

def test_unknown_tradition_falls_back_to_default() -> None:
    """An unrecognised tradition must return the default weights."""
    unknown = get_weights("totally_nonexistent_tradition_xyz")
    default = get_weights("default")
    assert unknown == default


def test_empty_string_tradition_falls_back_to_default() -> None:
    """An empty string tradition must also fall back to default."""
    weights = get_weights("")
    default = get_weights("default")
    assert weights == default


# ---------------------------------------------------------------------------
# 3. evolved_context.json override
# ---------------------------------------------------------------------------

def test_evolved_context_overrides_weights() -> None:
    """When evolved_context.json has tradition_weights, they override fallback."""
    custom_weights = {
        "visual_perception": 0.05,
        "technical_analysis": 0.10,
        "cultural_context": 0.35,
        "critical_interpretation": 0.25,
        "philosophical_aesthetic": 0.25,
    }
    evolved_data = {
        "tradition_weights": {
            "chinese_xieyi": custom_weights,
        },
        "version": 1,
        "evolutions": 3,
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as tmp:
        json.dump(evolved_data, tmp)
        tmp_path = tmp.name

    try:
        with patch(
            "app.prototype.cultural_pipelines.cultural_weights._EVOLVED_CONTEXT_PATH",
            tmp_path,
        ):
            weights = get_weights("chinese_xieyi")
            assert weights == custom_weights, (
                f"Expected evolved weights but got {weights}"
            )
    finally:
        os.unlink(tmp_path)


def test_evolved_context_empty_dict_no_override() -> None:
    """If tradition_weights is an empty dict, fallback weights are used."""
    evolved_data = {"tradition_weights": {}, "version": 1, "evolutions": 0}

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as tmp:
        json.dump(evolved_data, tmp)
        tmp_path = tmp.name

    try:
        with patch(
            "app.prototype.cultural_pipelines.cultural_weights._EVOLVED_CONTEXT_PATH",
            tmp_path,
        ):
            weights = get_weights("chinese_xieyi")
            fallback = _get_fallback_weights()["chinese_xieyi"]
            # When evolved dict is empty, we should get fallback (or YAML) weights
            assert weights is not None
            assert sum(weights.values()) == pytest.approx(1.0)
    finally:
        os.unlink(tmp_path)


def test_evolved_context_missing_file_no_error() -> None:
    """If evolved_context.json does not exist, no error and fallback used."""
    with patch(
        "app.prototype.cultural_pipelines.cultural_weights._EVOLVED_CONTEXT_PATH",
        "/tmp/nonexistent_evolved_context_abc123.json",
    ):
        weights = get_weights("default")
        assert sum(weights.values()) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 4. Pipeline variant mapping
# ---------------------------------------------------------------------------

def test_chinese_xieyi_maps_to_chinese_xieyi_variant(
    router: CulturalPipelineRouter,
) -> None:
    route = router.route("chinese_xieyi")
    assert route.variant.name == "chinese_xieyi"


def test_western_academic_maps_to_western_academic_variant(
    router: CulturalPipelineRouter,
) -> None:
    route = router.route("western_academic")
    assert route.variant.name == "western_academic"


@pytest.mark.parametrize(
    "tradition",
    [
        "chinese_gongbi",
        "islamic_geometric",
        "japanese_traditional",
        "watercolor",
        "african_traditional",
        "south_asian",
        "default",
    ],
)
def test_other_traditions_map_to_default_variant(
    router: CulturalPipelineRouter, tradition: str
) -> None:
    """Traditions without a dedicated variant use the default pipeline."""
    route = router.route(tradition)
    assert route.variant.name == "default", (
        f"Tradition '{tradition}' expected variant 'default', got '{route.variant.name}'"
    )


def test_unknown_tradition_maps_to_default_variant(
    router: CulturalPipelineRouter,
) -> None:
    route = router.route("unknown_tradition_xyz")
    assert route.variant.name == "default"


# ---------------------------------------------------------------------------
# 5. Pipeline variant critic_stages structure validation
# ---------------------------------------------------------------------------

def test_default_variant_single_critic_stage() -> None:
    """Default variant has exactly 1 critic stage covering all 5 dimensions."""
    variant = _VARIANTS["default"]
    assert len(variant.critic_stages) == 1
    assert set(variant.critic_stages[0]) == set(DIMENSIONS)
    assert variant.allow_local_rerun is True


def test_chinese_xieyi_variant_single_stage_no_rerun() -> None:
    """chinese_xieyi: single critic stage, no local rerun (一气呵成)."""
    variant = _VARIANTS["chinese_xieyi"]
    assert len(variant.critic_stages) == 1
    assert set(variant.critic_stages[0]) == set(DIMENSIONS)
    assert variant.allow_local_rerun is False
    # Scout focuses on L3+L5
    assert "cultural_context" in variant.scout_focus_layers
    assert "philosophical_aesthetic" in variant.scout_focus_layers


def test_western_academic_variant_three_progressive_stages() -> None:
    """western_academic: 3 progressive critic stages covering all dimensions."""
    variant = _VARIANTS["western_academic"]
    assert len(variant.critic_stages) == 3
    assert variant.allow_local_rerun is True

    # Stage 1: form (L1 + L2)
    assert set(variant.critic_stages[0]) == {
        "visual_perception",
        "technical_analysis",
    }
    # Stage 2: meaning (L3 + L4)
    assert set(variant.critic_stages[1]) == {
        "cultural_context",
        "critical_interpretation",
    }
    # Stage 3: philosophy (L5)
    assert set(variant.critic_stages[2]) == {"philosophical_aesthetic"}

    # Union of all stages must equal all dimensions
    all_dims_covered = set()
    for stage in variant.critic_stages:
        all_dims_covered.update(stage)
    assert all_dims_covered == set(DIMENSIONS)


# ---------------------------------------------------------------------------
# 6. Router produces correct CriticConfig with tradition-specific weights
# ---------------------------------------------------------------------------

def test_route_critic_config_has_tradition_weights(
    router: CulturalPipelineRouter,
) -> None:
    """The CriticConfig in a route must carry the tradition's specific weights."""
    route = router.route("chinese_xieyi")
    # chinese_xieyi emphasises L5 (philosophical_aesthetic = 0.30)
    xieyi_weights = get_weights("chinese_xieyi")
    assert route.critic_config.weights == xieyi_weights


def test_route_to_dict_serializable(router: CulturalPipelineRouter) -> None:
    """PipelineRoute.to_dict() should be JSON-serializable."""
    route = router.route("western_academic")
    d = route.to_dict()
    serialized = json.dumps(d)
    assert isinstance(serialized, str)
    parsed = json.loads(serialized)
    assert parsed["tradition"] == "western_academic"
    assert parsed["variant"]["name"] == "western_academic"


# ---------------------------------------------------------------------------
# 7. KNOWN_TRADITIONS consistency (static + dynamic)
# ---------------------------------------------------------------------------

def test_known_traditions_is_sorted() -> None:
    assert KNOWN_TRADITIONS == sorted(KNOWN_TRADITIONS)


def test_all_known_traditions_have_fallback_weights() -> None:
    """Every KNOWN_TRADITIONS entry must have a fallback weight table."""
    fallback = _get_fallback_weights()
    for tradition in KNOWN_TRADITIONS:
        assert tradition in fallback, (
            f"Tradition '{tradition}' in KNOWN_TRADITIONS but not in _get_fallback_weights()"
        )


def test_all_traditions_have_routing_entry() -> None:
    """Every KNOWN_TRADITIONS entry must have a routing mapping."""
    for tradition in KNOWN_TRADITIONS:
        assert tradition in _TRADITION_TO_VARIANT, (
            f"Tradition '{tradition}' missing from _TRADITION_TO_VARIANT"
        )


def test_get_all_weight_tables_returns_all() -> None:
    """get_all_weight_tables must include at least the 9 known traditions."""
    tables = get_all_weight_tables()
    for tradition in KNOWN_TRADITIONS:
        assert tradition in tables
        assert sum(tables[tradition].values()) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 8. get_known_traditions() dynamic version
# ---------------------------------------------------------------------------

def test_get_known_traditions_is_sorted() -> None:
    """Dynamic traditions list must be sorted."""
    traditions = get_known_traditions()
    assert traditions == sorted(traditions)


def test_get_known_traditions_superset_of_static() -> None:
    """Dynamic traditions must be a superset of the static KNOWN_TRADITIONS."""
    dynamic = set(get_known_traditions())
    static = set(KNOWN_TRADITIONS)
    assert static.issubset(dynamic), (
        f"Static traditions not in dynamic: {static - dynamic}"
    )


def test_get_known_traditions_includes_fallback_keys() -> None:
    """Dynamic traditions must include all _get_fallback_weights() keys."""
    dynamic = set(get_known_traditions())
    fallback_keys = set(_get_fallback_weights().keys())
    assert fallback_keys.issubset(dynamic), (
        f"Fallback keys not in dynamic: {fallback_keys - dynamic}"
    )


def test_get_known_traditions_includes_evolved_context() -> None:
    """Dynamic traditions should pick up keys from evolved_context.json."""
    evolved_data = {
        "tradition_weights": {
            "test_emerging_tradition": {
                "visual_perception": 0.20,
                "technical_analysis": 0.20,
                "cultural_context": 0.20,
                "critical_interpretation": 0.20,
                "philosophical_aesthetic": 0.20,
            },
        },
        "version": 1,
        "evolutions": 1,
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as tmp:
        json.dump(evolved_data, tmp)
        tmp_path = tmp.name

    try:
        with patch(
            "app.prototype.cultural_pipelines.cultural_weights._EVOLVED_CONTEXT_PATH",
            tmp_path,
        ):
            traditions = get_known_traditions()
            assert "test_emerging_tradition" in traditions, (
                f"Evolved tradition not found in dynamic list: {traditions}"
            )
    finally:
        os.unlink(tmp_path)


def test_get_known_traditions_returns_list_of_strings() -> None:
    """get_known_traditions must return a list of strings."""
    traditions = get_known_traditions()
    assert isinstance(traditions, list)
    for t in traditions:
        assert isinstance(t, str)
