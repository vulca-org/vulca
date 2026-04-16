"""Phase 0 Task 0: 8-layer cap lifted to 20."""
import pytest

from vulca.pipeline.types import PipelineInput


def test_default_max_layers_unchanged():
    inp = PipelineInput(subject="x", provider="mock")
    assert inp.max_layers == 8


def test_pipeline_accepts_up_to_20_layers():
    inp = PipelineInput(subject="x", provider="mock", max_layers=20)
    assert inp.max_layers == 20


def test_pipeline_accepts_12_layers():
    inp = PipelineInput(subject="x", provider="mock", max_layers=12)
    assert inp.max_layers == 12


def test_pipeline_rejects_above_20_layers():
    with pytest.raises(ValueError, match="max_layers"):
        PipelineInput(subject="x", provider="mock", max_layers=21)


def test_pipeline_rejects_zero_layers():
    with pytest.raises(ValueError, match="max_layers"):
        PipelineInput(subject="x", provider="mock", max_layers=0)
