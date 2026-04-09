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


def test_generate_single_routes_mock_v2_to_mock_generate(tmp_path):
    """v0.13.2 P2 codex G3: _generate_single's legacy fallback must also
    route non-raw_rgba providers (e.g. a future 'mock_v2') to _mock_generate,
    not try to call an undefined provider path. Previously this branch was
    gated on the literal string 'mock'."""
    import asyncio
    from vulca.layers.types import LayerInfo

    node = LayerGenerateNode()
    calls: list[str] = []

    def _fake_mock_generate(info, output_dir, ctx):
        calls.append(info.name)
        return "sentinel"

    node._mock_generate = _fake_mock_generate  # type: ignore[method-assign]
    node._build_prompt = lambda info, ctx: "prompt"  # type: ignore[method-assign]

    info = LayerInfo(name="bg", description="bg desc", z_index=0)
    ctx = SimpleNamespace(
        provider="mock_v2",
        image_provider=_FakeNonRawProvider(),
        api_key=None,
        round_num=1,
    )
    result = asyncio.run(
        node._generate_single(info, ctx, str(tmp_path), None)
    )
    assert result == "sentinel"
    assert calls == ["bg"]
