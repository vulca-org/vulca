"""Unit tests for SAM2 device-selection + checkpoint-name fixes in 0.17.2.

Covers two bugs found in T1.6.a emoart smoke after 0.17.1 shipped:
  - Bug #2: default checkpoint was "sam2.1_hiera_small" (invalid HF ID)
  - Bug #3: upstream build_sam2* assumes CUDA; MPS/CPU hosts crash on default

Tests are offline and do not require sam2 installed; they exercise the
pure helpers (`_sam2_device`, `_patch_sam2_build_to_device`, constant,
and docstring) so coverage exists even on CI without the sam2 package.
"""
from __future__ import annotations

import sys
import types
from unittest import mock

import pytest

from vulca.layers import sam as sam_mod


def test_default_checkpoint_is_valid_hf_id() -> None:
    """The DEFAULT_SAM2_CHECKPOINT constant must be a valid HF Hub ID.

    A valid HF ID is `<org>/<repo>` with hyphens. The old broken value
    `sam2.1_hiera_small` (underscores, no prefix) is not resolvable.
    """
    assert sam_mod.DEFAULT_SAM2_CHECKPOINT == "facebook/sam2.1-hiera-small"
    assert "/" in sam_mod.DEFAULT_SAM2_CHECKPOINT
    assert "_" not in sam_mod.DEFAULT_SAM2_CHECKPOINT.split("/", 1)[1]


def test_sam2_device_returns_cpu_when_no_cuda(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without CUDA, device selection must fall back to CPU (not MPS).

    SAM2 does not reliably support MPS as of 2026-04-20; Apple Silicon
    intentionally uses CPU rather than returning 'mps'.
    """
    fake_torch = types.SimpleNamespace(
        cuda=types.SimpleNamespace(is_available=lambda: False),
    )
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    assert sam_mod._sam2_device() == "cpu"


def test_sam2_device_returns_cuda_when_available(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_torch = types.SimpleNamespace(
        cuda=types.SimpleNamespace(is_available=lambda: True),
    )
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    assert sam_mod._sam2_device() == "cuda"


def test_sam2_device_returns_cpu_when_torch_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """No torch at all -> CPU (no crash)."""
    # Force `import torch` inside the helper to raise
    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def raising_import(name: str, *args, **kwargs):
        if name == "torch":
            raise ImportError("torch gone")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(
        "builtins.__import__",
        raising_import,
    )
    assert sam_mod._sam2_device() == "cpu"


def test_patch_sam2_build_noop_when_unavailable() -> None:
    """If SAM2 not importable, the patcher is a silent no-op."""
    with mock.patch.object(sam_mod, "SAM_AVAILABLE", False):
        sam_mod._patch_sam2_build_to_device("cpu")  # must not raise


def test_patch_sam2_build_injects_device_kwarg(monkeypatch: pytest.MonkeyPatch) -> None:
    """The patch wraps build_sam2* to inject device kwarg if absent."""
    # Stand up a minimal fake `sam2.build_sam` module with callable stubs
    captured: dict[str, dict] = {}

    def _stub(name: str):
        def fn(*args, **kwargs):
            captured[name] = kwargs
            return "fake_model"
        return fn

    fake_build_sam = types.SimpleNamespace(
        build_sam2=_stub("build_sam2"),
        build_sam2_hf=_stub("build_sam2_hf"),
        build_sam2_video_predictor=_stub("build_sam2_video_predictor"),
    )
    fake_sam2 = types.ModuleType("sam2")
    fake_sam2.build_sam = fake_build_sam  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "sam2", fake_sam2)
    monkeypatch.setitem(sys.modules, "sam2.build_sam", fake_build_sam)
    monkeypatch.setattr(sam_mod, "SAM_AVAILABLE", True)

    sam_mod._patch_sam2_build_to_device("cpu")

    # Call each patched fn; device should be injected
    fake_build_sam.build_sam2("arg")
    fake_build_sam.build_sam2_hf("arg")
    fake_build_sam.build_sam2_video_predictor("arg")

    for name in ("build_sam2", "build_sam2_hf", "build_sam2_video_predictor"):
        assert captured[name].get("device") == "cpu", (
            f"{name} did not receive injected device kwarg"
        )

    # Re-patching should not wrap again (idempotency check)
    sam_mod._patch_sam2_build_to_device("cpu")
    assert getattr(fake_build_sam.build_sam2, "_vulca_patched", False) is True


def test_patch_preserves_explicit_device_kwarg(monkeypatch: pytest.MonkeyPatch) -> None:
    """If caller passes device=... explicitly, the patch must not override it."""
    captured: dict[str, dict] = {}

    def fn(*args, **kwargs):
        captured["build_sam2"] = kwargs
        return "fake"

    fake_build_sam = types.SimpleNamespace(build_sam2=fn)
    fake_sam2 = types.ModuleType("sam2")
    fake_sam2.build_sam = fake_build_sam  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "sam2", fake_sam2)
    monkeypatch.setitem(sys.modules, "sam2.build_sam", fake_build_sam)
    monkeypatch.setattr(sam_mod, "SAM_AVAILABLE", True)

    sam_mod._patch_sam2_build_to_device("cpu")

    fake_build_sam.build_sam2("x", device="cuda")  # explicit override

    assert captured["build_sam2"].get("device") == "cuda"


def test_sam_split_raises_importerror_without_sam2(monkeypatch: pytest.MonkeyPatch) -> None:
    """When SAM2 is not importable, sam_split raises ImportError with
    the two-step install hint (regression protection for 0.17.1 behavior).
    """
    monkeypatch.setattr(sam_mod, "SAM_AVAILABLE", False)
    with pytest.raises(ImportError, match="pip install vulca\\[sam\\]"):
        sam_mod.sam_split(
            image_path="irrelevant.jpg",
            layers=[],
            output_dir="/tmp/irrelevant",
        )
