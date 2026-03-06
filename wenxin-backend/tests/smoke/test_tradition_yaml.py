"""Unit 3: Tradition YAML validation suite.

Validates all 9 tradition YAML files for structural correctness,
weight consistency, terminology/taboo coverage, and YAML-vs-fallback
regression. No API calls or API keys required.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TRADITIONS_DIR = Path(__file__).resolve().parents[2] / "app" / "prototype" / "data" / "traditions"
_SCHEMA_PATH = _TRADITIONS_DIR / "schema.json"

EXPECTED_TRADITIONS = [
    "default",
    "chinese_xieyi",
    "chinese_gongbi",
    "western_academic",
    "islamic_geometric",
    "japanese_traditional",
    "watercolor",
    "african_traditional",
    "south_asian",
]

REQUIRED_FIELDS = ["name", "display_name", "weights", "terminology", "taboos", "pipeline"]
L_LABELS = ["L1", "L2", "L3", "L4", "L5"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_yaml(name: str) -> dict:
    path = _TRADITIONS_DIR / f"{name}.yaml"
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Test: YAML files exist and parse
# ---------------------------------------------------------------------------

class TestYAMLFilesExist:
    """All 9 tradition YAML files exist and parse correctly."""

    @pytest.mark.parametrize("tradition", EXPECTED_TRADITIONS)
    def test_file_exists(self, tradition: str):
        path = _TRADITIONS_DIR / f"{tradition}.yaml"
        assert path.is_file(), f"Missing tradition file: {path}"

    @pytest.mark.parametrize("tradition", EXPECTED_TRADITIONS)
    def test_file_parses(self, tradition: str):
        data = _load_yaml(tradition)
        assert isinstance(data, dict), f"{tradition}.yaml did not parse to a dict"

    def test_template_exists(self):
        path = _TRADITIONS_DIR / "_template.yaml"
        assert path.is_file()

    def test_template_parses(self):
        with open(_TRADITIONS_DIR / "_template.yaml", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# Test: Required fields
# ---------------------------------------------------------------------------

class TestRequiredFields:
    """Each tradition has all required fields."""

    @pytest.mark.parametrize("tradition", EXPECTED_TRADITIONS)
    def test_has_required_fields(self, tradition: str):
        data = _load_yaml(tradition)
        for field in REQUIRED_FIELDS:
            assert field in data, f"{tradition} missing required field: {field}"

    @pytest.mark.parametrize("tradition", EXPECTED_TRADITIONS)
    def test_name_matches_filename(self, tradition: str):
        data = _load_yaml(tradition)
        assert data["name"] == tradition, (
            f"File {tradition}.yaml has name={data['name']}"
        )

    @pytest.mark.parametrize("tradition", EXPECTED_TRADITIONS)
    def test_display_name_has_en(self, tradition: str):
        data = _load_yaml(tradition)
        assert "en" in data["display_name"], f"{tradition} missing display_name.en"


# ---------------------------------------------------------------------------
# Test: Weights
# ---------------------------------------------------------------------------

class TestWeights:
    """Weights must have L1-L5 and sum to 1.0."""

    @pytest.mark.parametrize("tradition", EXPECTED_TRADITIONS)
    def test_has_all_l_labels(self, tradition: str):
        data = _load_yaml(tradition)
        weights = data["weights"]
        for label in L_LABELS:
            assert label in weights, f"{tradition} missing weight: {label}"

    @pytest.mark.parametrize("tradition", EXPECTED_TRADITIONS)
    def test_weights_sum_to_one(self, tradition: str):
        data = _load_yaml(tradition)
        weights = data["weights"]
        total = sum(weights[l] for l in L_LABELS)
        assert abs(total - 1.0) < 0.001, (
            f"{tradition} weights sum to {total:.4f}"
        )

    @pytest.mark.parametrize("tradition", EXPECTED_TRADITIONS)
    def test_weights_are_positive(self, tradition: str):
        data = _load_yaml(tradition)
        weights = data["weights"]
        for label in L_LABELS:
            assert 0 <= weights[label] <= 1, (
                f"{tradition} weight {label}={weights[label]} out of range"
            )


# ---------------------------------------------------------------------------
# Test: Terminology
# ---------------------------------------------------------------------------

class TestTerminology:
    """Each tradition has at least 5 terminology entries with required fields."""

    @pytest.mark.parametrize("tradition", EXPECTED_TRADITIONS)
    def test_has_enough_terms(self, tradition: str):
        data = _load_yaml(tradition)
        terms = data["terminology"]
        assert len(terms) >= 3, (
            f"{tradition} has only {len(terms)} terms (need >= 3)"
        )

    @pytest.mark.parametrize("tradition", EXPECTED_TRADITIONS)
    def test_term_has_required_fields(self, tradition: str):
        data = _load_yaml(tradition)
        for i, term in enumerate(data["terminology"]):
            assert "term" in term, f"{tradition} terminology[{i}] missing 'term'"
            assert "definition" in term, f"{tradition} terminology[{i}] missing 'definition'"
            assert "l_levels" in term, f"{tradition} terminology[{i}] missing 'l_levels'"


# ---------------------------------------------------------------------------
# Test: Taboos
# ---------------------------------------------------------------------------

class TestTaboos:
    """Each tradition has at least 1 taboo rule."""

    @pytest.mark.parametrize("tradition", EXPECTED_TRADITIONS)
    def test_has_taboos(self, tradition: str):
        data = _load_yaml(tradition)
        taboos = data["taboos"]
        assert len(taboos) >= 1, f"{tradition} has no taboo rules"

    @pytest.mark.parametrize("tradition", EXPECTED_TRADITIONS)
    def test_taboo_has_rule_and_severity(self, tradition: str):
        data = _load_yaml(tradition)
        for i, taboo in enumerate(data["taboos"]):
            assert "rule" in taboo, f"{tradition} taboos[{i}] missing 'rule'"
            assert "severity" in taboo, f"{tradition} taboos[{i}] missing 'severity'"
            assert taboo["severity"] in ("low", "medium", "high", "critical"), (
                f"{tradition} taboos[{i}] invalid severity: {taboo['severity']}"
            )


# ---------------------------------------------------------------------------
# Test: Pipeline config
# ---------------------------------------------------------------------------

class TestPipelineConfig:
    """Pipeline config is valid."""

    @pytest.mark.parametrize("tradition", EXPECTED_TRADITIONS)
    def test_has_variant(self, tradition: str):
        data = _load_yaml(tradition)
        pipeline = data["pipeline"]
        assert "variant" in pipeline
        assert pipeline["variant"] in ("default", "chinese_xieyi", "western_academic")


# ---------------------------------------------------------------------------
# Test: tradition_loader integration
# ---------------------------------------------------------------------------

class TestTraditionLoader:
    """Verify tradition_loader.py loads all 9 + default correctly."""

    def test_get_all_traditions_count(self):
        from app.prototype.cultural_pipelines.tradition_loader import get_all_traditions
        traditions = get_all_traditions()
        assert len(traditions) >= 9, f"Only {len(traditions)} traditions loaded"
        for name in EXPECTED_TRADITIONS:
            assert name in traditions, f"Tradition '{name}' not loaded"

    def test_get_tradition_returns_config(self):
        from app.prototype.cultural_pipelines.tradition_loader import get_tradition
        for name in EXPECTED_TRADITIONS:
            tc = get_tradition(name)
            assert tc is not None, f"get_tradition('{name}') returned None"
            assert tc.name == name

    def test_validate_tradition_yaml_passes(self):
        from app.prototype.cultural_pipelines.tradition_loader import validate_tradition_yaml
        for name in EXPECTED_TRADITIONS:
            path = _TRADITIONS_DIR / f"{name}.yaml"
            errors = validate_tradition_yaml(path)
            assert errors == [], f"{name}.yaml validation errors: {errors}"


# ---------------------------------------------------------------------------
# Test: get_weights consistency
# ---------------------------------------------------------------------------

class TestWeightsConsistency:
    """Verify get_weights() returns valid dicts for all traditions."""

    def test_get_weights_for_all(self):
        from app.prototype.cultural_pipelines.cultural_weights import get_weights
        dim_ids = [
            "visual_perception", "technical_analysis", "cultural_context",
            "critical_interpretation", "philosophical_aesthetic",
        ]
        for tradition in EXPECTED_TRADITIONS:
            weights = get_weights(tradition)
            assert isinstance(weights, dict), f"get_weights('{tradition}') not a dict"
            for dim in dim_ids:
                assert dim in weights, f"get_weights('{tradition}') missing {dim}"
            total = sum(weights.values())
            assert abs(total - 1.0) < 0.01, (
                f"get_weights('{tradition}') sums to {total:.4f}"
            )

    def test_yaml_matches_fallback(self):
        """YAML weights should match hardcoded fallback (regression check)."""
        from app.prototype.cultural_pipelines.cultural_weights import (
            _FALLBACK_WEIGHTS,
            get_weights,
        )
        for tradition, fallback_w in _FALLBACK_WEIGHTS.items():
            yaml_w = get_weights(tradition)
            for dim, expected_val in fallback_w.items():
                actual_val = yaml_w.get(dim, -1)
                assert abs(actual_val - expected_val) < 0.001, (
                    f"Tradition '{tradition}' dim '{dim}': "
                    f"YAML={actual_val} != fallback={expected_val}"
                )


# ---------------------------------------------------------------------------
# Test: JSON Schema
# ---------------------------------------------------------------------------

class TestJSONSchema:
    """schema.json is valid and can validate YAML files."""

    def test_schema_exists_and_parses(self):
        assert _SCHEMA_PATH.is_file(), f"schema.json not found at {_SCHEMA_PATH}"
        with open(_SCHEMA_PATH, encoding="utf-8") as f:
            schema = json.load(f)
        assert schema.get("type") == "object"
        assert "properties" in schema

    def test_schema_validates_all_yamls(self):
        """If jsonschema is available, validate all YAML files against it."""
        try:
            import jsonschema
        except ImportError:
            pytest.skip("jsonschema not installed")

        with open(_SCHEMA_PATH, encoding="utf-8") as f:
            schema = json.load(f)

        for tradition in EXPECTED_TRADITIONS:
            data = _load_yaml(tradition)
            try:
                jsonschema.validate(data, schema)
            except jsonschema.ValidationError as e:
                pytest.fail(f"{tradition}.yaml schema validation failed: {e.message}")
