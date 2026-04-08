import io
from PIL import Image

from vulca.layers.layered_cache import LayerCache, build_cache_key


def _png_bytes():
    img = Image.new("RGBA", (8, 8), (10, 20, 30, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_cache_key_stable():
    a = build_cache_key(
        provider_id="gemini", model_id="m1", prompt="hi",
        canvas_color="#ffffff", canvas_tolerance=0.05, seed=0, schema_version="0.13",
    )
    b = build_cache_key(
        provider_id="gemini", model_id="m1", prompt="hi",
        canvas_color="#ffffff", canvas_tolerance=0.05, seed=0, schema_version="0.13",
    )
    assert a == b
    assert isinstance(a, str) and len(a) == 64  # sha256 hex


def test_cache_key_changes_on_prompt():
    a = build_cache_key(
        provider_id="g", model_id="m", prompt="x",
        canvas_color="#fff", canvas_tolerance=0.05, seed=0, schema_version="0.13",
    )
    b = build_cache_key(
        provider_id="g", model_id="m", prompt="y",
        canvas_color="#fff", canvas_tolerance=0.05, seed=0, schema_version="0.13",
    )
    assert a != b


def test_cache_key_changes_on_provider():
    a = build_cache_key(
        provider_id="g1", model_id="m", prompt="x",
        canvas_color="#fff", canvas_tolerance=0.05, seed=0, schema_version="0.13",
    )
    b = build_cache_key(
        provider_id="g2", model_id="m", prompt="x",
        canvas_color="#fff", canvas_tolerance=0.05, seed=0, schema_version="0.13",
    )
    assert a != b


def _base_kwargs():
    return dict(
        provider_id="g", model_id="m", prompt="x",
        canvas_color="#fff", canvas_tolerance=0.05, seed=0, schema_version="0.13",
    )


def test_cache_key_changes_on_key_strategy():
    a = build_cache_key(**_base_kwargs(), key_strategy="LuminanceKeying")
    b = build_cache_key(**_base_kwargs(), key_strategy="ChromaKeying")
    assert a != b


def test_cache_key_changes_on_canvas_invert():
    a = build_cache_key(**_base_kwargs(), canvas_invert=False)
    b = build_cache_key(**_base_kwargs(), canvas_invert=True)
    assert a != b


def test_cache_key_changes_on_dimensions():
    a = build_cache_key(**_base_kwargs(), width=1024, height=1024)
    b = build_cache_key(**_base_kwargs(), width=512, height=512)
    assert a != b


def test_cache_key_defaults_are_backward_compatible():
    """Omitting new kwargs must not change pre-existing keys (default values
    hash to a fixed string that tests from v0.13.0 baseline still match)."""
    a = build_cache_key(**_base_kwargs())
    b = build_cache_key(**_base_kwargs(), key_strategy="", canvas_invert=False,
                        width=0, height=0)
    assert a == b


def test_cache_roundtrip(tmp_path):
    cache = LayerCache(tmp_path / "art")
    key = "k1"
    assert cache.get(key) is None
    cache.put(key, _png_bytes())
    data = cache.get(key)
    assert data is not None and data.startswith(b"\x89PNG")


def test_cache_miss_returns_none(tmp_path):
    cache = LayerCache(tmp_path / "art")
    assert cache.get("nonexistent") is None


def test_cache_disabled_with_flag(tmp_path):
    cache = LayerCache(tmp_path / "art", enabled=False)
    cache.put("k", _png_bytes())
    assert cache.get("k") is None


def test_cache_disabled_with_none_dir():
    cache = LayerCache(None)
    cache.put("k", _png_bytes())
    assert cache.get("k") is None


def test_cache_creates_directory(tmp_path):
    art_dir = tmp_path / "fresh_artifact"
    assert not art_dir.exists()
    cache = LayerCache(art_dir)
    cache.put("k", _png_bytes())
    assert (art_dir / ".layered_cache").is_dir()
    assert (art_dir / ".layered_cache" / "k.png").is_file()
