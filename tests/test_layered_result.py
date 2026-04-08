from vulca.layers.types import LayerInfo
from vulca.layers.layered_generate import (
    LayerOutcome, LayerFailure, LayeredResult,
)


def _info(name, content_type="subject", role=""):
    return LayerInfo(name=name, description="", z_index=0, content_type=content_type, tradition_role=role)


def test_outcome_ok():
    o = LayerOutcome(ok=True, info=_info("远山", role="远景淡墨"), rgba_path="/tmp/x.png")
    assert o.ok and o.rgba_path.endswith(".png")


def test_failure_carries_reason():
    f = LayerFailure(layer_id="layer_x", role="远景淡墨", reason="generation_failed", attempts=3)
    assert f.reason == "generation_failed" and f.attempts == 3


def test_layered_result_is_complete():
    res = LayeredResult(
        layers=[
            LayerOutcome(ok=True, info=_info("a", role="bg"), rgba_path="/a.png"),
            LayerOutcome(ok=True, info=_info("b", content_type="subject", role="m"), rgba_path="/b.png"),
        ],
        failed=[],
    )
    assert res.is_complete and res.is_usable


def test_layered_result_partial_usable():
    res = LayeredResult(
        layers=[
            LayerOutcome(ok=True, info=_info("bg", content_type="background", role="bg"), rgba_path="/bg.png"),
            LayerOutcome(ok=True, info=_info("subj", content_type="subject", role="m"), rgba_path="/s.png"),
        ],
        failed=[LayerFailure(layer_id="x", role="题款", reason="generation_failed", attempts=1)],
    )
    assert not res.is_complete
    assert res.is_usable


def test_layered_result_unusable_no_subject():
    res = LayeredResult(
        layers=[LayerOutcome(ok=True, info=_info("bg", content_type="background", role="bg"), rgba_path="/bg.png")],
        failed=[LayerFailure("x", "subj", "generation_failed", 1)],
    )
    assert not res.is_usable
