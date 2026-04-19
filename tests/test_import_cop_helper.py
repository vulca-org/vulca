"""Tests for the _import_cop helper that wraps sys.path + module import."""
import sys
import threading


def test_import_cop_returns_sys_modules_singleton():
    from vulca.pipeline.segment.orchestrator import _import_cop
    cop1 = _import_cop()
    cop2 = _import_cop()
    assert cop1 is cop2, "helper must return same module instance"
    assert cop1 is sys.modules["claude_orchestrated_pipeline"], \
        "helper must expose the same module runtime uses"


def test_import_cop_exposes_four_cached_loaders():
    from vulca.pipeline.segment.orchestrator import _import_cop
    cop = _import_cop()
    for name in ("load_grounding_dino", "load_yolo",
                 "load_face_parser", "_load_sam_model"):
        loader = getattr(cop, name, None)
        assert loader is not None, f"{name} must exist on cop"
        assert callable(getattr(loader, "cache_clear", None)), \
            f"{name} must be lru_cache'd (cache_clear attribute missing)"


def test_import_cop_thread_safety():
    """4 concurrent _import_cop() calls return same module."""
    from vulca.pipeline.segment.orchestrator import _import_cop

    results = []

    def worker():
        results.append(_import_cop())

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    ids = {id(r) for r in results}
    assert len(ids) == 1, f"concurrent calls got different modules: {ids}"
