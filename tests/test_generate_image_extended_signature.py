"""Tripwire: MCP generate_image extended signature (v0.17.6).

Validates the 4 new Optional kwargs (seed / steps / cfg_scale / negative_prompt)
plumb through the MCP wrapper to the underlying provider without breaking
backward compatibility. Required for /visual-plan Phase 5 spike execution.
"""
from __future__ import annotations

import asyncio
import inspect
from typing import Any

import pytest

from vulca.providers.base import ImageResult


def run(coro):
    return asyncio.run(coro)


class _CapturingProvider:
    """Records the kwargs received by generate(); returns a valid tiny PNG."""

    capabilities = frozenset({"raw_rgba"})

    def __init__(self):
        self.calls: list[dict[str, Any]] = []

    async def generate(self, prompt: str, **kwargs) -> ImageResult:
        import base64
        import io
        from PIL import Image

        self.calls.append({"prompt": prompt, **kwargs})

        buf = io.BytesIO()
        Image.new("RGBA", (8, 8), (0, 0, 0, 255)).save(buf, format="PNG")
        return ImageResult(
            image_b64=base64.b64encode(buf.getvalue()).decode(),
            mime="image/png",
            metadata={"cost_usd": 0.0},
        )


@pytest.fixture
def capturing_provider(monkeypatch):
    cap = _CapturingProvider()
    import vulca.providers as providers_mod
    import vulca.mcp_server as mcp_mod

    def _fake_get(name):
        return cap

    monkeypatch.setattr(providers_mod, "get_image_provider", _fake_get)
    monkeypatch.setattr(mcp_mod, "get_image_provider", _fake_get, raising=False)
    return cap


class TestExtendedSignature:
    def test_signature_has_four_new_optional_kwargs(self):
        """Hard gate per /visual-plan Task 9: signature must expose all 4 as Optional with None default."""
        from vulca.mcp_server import generate_image

        sig = inspect.signature(generate_image)
        params = sig.parameters

        for name in ("seed", "steps", "cfg_scale", "negative_prompt"):
            assert name in params, f"missing kwarg: {name}"
            assert params[name].default is None, f"{name} default must be None, got {params[name].default!r}"

    def test_backward_compat_old_call_still_works(self, tmp_path):
        """Existing 5-param call sites (no new kwargs) must continue to work unchanged."""
        from vulca.mcp_server import generate_image

        r = run(generate_image("a mountain", provider="mock", output_dir=str(tmp_path)))
        assert "image_path" in r
        assert "error" not in r

    def test_seed_plumbs_to_provider(self, capturing_provider, tmp_path):
        from vulca.mcp_server import generate_image

        run(generate_image("p", provider="mock", output_dir=str(tmp_path), seed=4242))

        assert len(capturing_provider.calls) == 1
        assert capturing_provider.calls[0]["seed"] == 4242

    def test_steps_plumbs_to_provider(self, capturing_provider, tmp_path):
        from vulca.mcp_server import generate_image

        run(generate_image("p", provider="mock", output_dir=str(tmp_path), steps=50))

        assert capturing_provider.calls[0]["steps"] == 50

    def test_cfg_scale_plumbs_to_provider(self, capturing_provider, tmp_path):
        from vulca.mcp_server import generate_image

        run(generate_image("p", provider="mock", output_dir=str(tmp_path), cfg_scale=12.5))

        assert capturing_provider.calls[0]["cfg_scale"] == 12.5

    def test_negative_prompt_plumbs_to_provider(self, capturing_provider, tmp_path):
        from vulca.mcp_server import generate_image

        run(generate_image("p", provider="mock", output_dir=str(tmp_path), negative_prompt="blurry, low-res"))

        assert capturing_provider.calls[0]["negative_prompt"] == "blurry, low-res"

    def test_none_values_not_passed_to_provider(self, capturing_provider, tmp_path):
        """When caller omits a kwarg, it MUST NOT appear in prov.generate's kwargs.

        Rationale: some provider signatures may treat None differently from absence
        (e.g., comfyui defaulting to random seed when the key is missing). Keep the
        contract tight — pass only what the user specified.
        """
        from vulca.mcp_server import generate_image

        run(generate_image("p", provider="mock", output_dir=str(tmp_path)))

        received = capturing_provider.calls[0]
        assert "seed" not in received
        assert "steps" not in received
        assert "cfg_scale" not in received
        assert "negative_prompt" not in received

    def test_mock_provider_echoes_all_four_kwargs_in_metadata(self, tmp_path):
        """Direct mock-provider contract: when all 4 kwargs are given, metadata echoes them.

        Used by /visual-plan to verify its seed/steps/cfg_scale actually reached the
        simulated provider during F-calibration dry-runs.
        """
        from vulca.providers.mock import MockImageProvider

        p = MockImageProvider()
        result = run(p.generate(
            "p",
            tradition="chinese_xieyi",
            seed=7,
            steps=25,
            cfg_scale=8.0,
            negative_prompt="noise",
        ))

        assert result.metadata["seed"] == 7
        assert result.metadata["steps"] == 25
        assert result.metadata["cfg_scale"] == 8.0
        assert result.metadata["negative_prompt"] == "noise"
