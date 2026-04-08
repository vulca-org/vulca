"""v0.13.2 P2: _provider_supports_native uses capabilities, not string match."""
from __future__ import annotations

from types import SimpleNamespace

from vulca.pipeline.nodes.layer_generate import LayerGenerateNode


class _FakeRawProvider:
    capabilities = frozenset({"raw_rgba"})

    async def generate(self, *args, **kwargs):
        raise NotImplementedError


class _FakeNonRawProvider:
    capabilities = frozenset()

    async def generate(self, *args, **kwargs):
        raise NotImplementedError


def _ctx(provider_name: str, image_provider=None):
    return SimpleNamespace(provider=provider_name, image_provider=image_provider)


def test_injected_raw_provider_supports_native():
    ctx = _ctx("anything", image_provider=_FakeRawProvider())
    assert LayerGenerateNode._provider_supports_native(ctx) is True


def test_injected_non_raw_provider_does_not_support_native():
    ctx = _ctx("anything", image_provider=_FakeNonRawProvider())
    assert LayerGenerateNode._provider_supports_native(ctx) is False


def test_default_mock_provider_blocked():
    ctx = _ctx("mock", image_provider=None)
    assert LayerGenerateNode._provider_supports_native(ctx) is False


def test_future_mock_v2_with_empty_capabilities_also_blocked():
    """The point: routing decides by capabilities, not string match on 'mock'."""
    ctx = _ctx("mock_v2", image_provider=_FakeNonRawProvider())
    assert LayerGenerateNode._provider_supports_native(ctx) is False
