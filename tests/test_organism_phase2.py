"""Tests for Organism Integrity Phase 2."""
from __future__ import annotations
import pytest


class TestLayeredAutoComposite:
    """Task 1: LAYERED template includes composite node."""

    def test_layered_has_composite_node(self):
        from vulca.pipeline.templates import LAYERED
        assert "composite" in LAYERED.nodes

    def test_layered_has_three_nodes(self):
        from vulca.pipeline.templates import LAYERED
        assert len(LAYERED.nodes) == 3

    def test_layered_composite_is_last(self):
        from vulca.pipeline.templates import LAYERED
        assert LAYERED.nodes[-1] == "composite"

    def test_layered_edge_layer_generate_to_composite(self):
        from vulca.pipeline.templates import LAYERED
        assert ("layer_generate", "composite") in LAYERED.edges


class TestSketchParameterRemoved:
    """Task 2: --sketch CLI param removed (dead code — GenerateNode never read sketch_b64)."""

    def test_sketch_not_in_create_signature(self):
        """create() and acreate() no longer accept a 'sketch' parameter."""
        import inspect
        from vulca.create import acreate, create
        for fn in (create, acreate):
            sig = inspect.signature(fn)
            assert "sketch" not in sig.parameters, (
                f"{fn.__name__}() should not have 'sketch' parameter"
            )

    def test_reference_still_in_create_signature(self):
        """--reference remains as the sole image input for create."""
        import inspect
        from vulca.create import acreate
        sig = inspect.signature(acreate)
        assert "reference" in sig.parameters, (
            "acreate() must still accept 'reference' parameter"
        )

    def test_sketch_b64_not_in_create_local(self):
        """_create_local no longer builds sketch_b64 in gen_params."""
        import inspect
        from vulca.create import _create_local
        source = inspect.getsource(_create_local)
        assert "sketch_b64" not in source, (
            "_create_local should not reference sketch_b64"
        )

    def test_generate_node_has_no_sketch_b64(self):
        """GenerateNode does not read sketch_b64 from gen_params."""
        import inspect
        from vulca.pipeline.nodes.generate import GenerateNode
        source = inspect.getsource(GenerateNode)
        assert "sketch_b64" not in source, (
            "GenerateNode should have no reference to sketch_b64"
        )


class TestCleanDeadParameters:
    """Task 3: Remove include_evidence, document sparse behavior."""

    def test_include_evidence_not_in_evaluate_signature(self):
        """include_evidence should not be in evaluate() signature."""
        import inspect
        from vulca import evaluate
        sig = inspect.signature(evaluate)
        assert "include_evidence" not in sig.parameters

    def test_include_evidence_not_in_aevaluate_signature(self):
        """include_evidence should not be in aevaluate() signature."""
        import inspect
        from vulca import aevaluate
        sig = inspect.signature(aevaluate)
        assert "include_evidence" not in sig.parameters

    def test_sparse_documented_in_aevaluate(self):
        """aevaluate docstring should explain sparse behavior."""
        from vulca.evaluate import aevaluate
        assert aevaluate.__doc__ is not None
        assert "sparse" in aevaluate.__doc__.lower()
