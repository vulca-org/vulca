# Cultural-Term Real Provider Opt-In Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an explicit real-provider execution path for the cultural-term efficacy harness using an OpenAI-compatible image endpoint without persisting secrets.

**Architecture:** Extend `OpenAIImageProvider` with configurable base URL support, then wire the benchmark harness to run A/B/C/D conditions only when `--real-provider --provider openai` and environment credentials are present. The harness writes generated images, manifest metadata, and provider-cost records while keeping dry-run behavior unchanged.

**Tech Stack:** Python standard library, `httpx.MockTransport` tests, existing `OpenAIImageProvider`, existing `ImageResult`, pytest.

---

## File Map

- Modify `src/vulca/providers/openai_provider.py`: add base URL normalization and use it for generations/edits endpoints.
- Modify `tests/test_openai_provider.py`: verify custom base URL and environment fallback.
- Modify `scripts/visual_discovery_benchmark.py`: add real-provider env resolution, image writing, metadata writing, cost writing, and CLI `--provider`.
- Modify `tests/test_visual_discovery_benchmark.py`: verify fail-closed behavior and mocked real-provider artifact output.
- Modify `tests/test_visual_discovery_docs_truth.py`: verify docs/spec/examples do not contain credential-looking strings or the real gateway host.
- Modify `docs/product/experiments/cultural-term-efficacy.md`: document the explicit real-provider command with safe placeholder values.

## Task 1: Add OpenAI Base URL Tests

**Files:**
- Modify: `tests/test_openai_provider.py`

- [ ] **Step 1: Add tests for custom OpenAI-compatible base URL**

Append these tests after `test_usage_cost_populates_cost_usd_metadata`:

```python
def test_custom_base_url_is_used_for_image_generations():
    captured_urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured_urls.append(str(request.url))
        return httpx.Response(200, json={"data": [{"b64_json": "AAAA"}]})

    with _httpx_with_handler(handler):
        asyncio.run(
            OpenAIImageProvider(
                api_key="test-token",
                model="gpt-image-2",
                base_url="https://gateway.example/v1/",
            ).generate("a sunset")
        )

    assert captured_urls == ["https://gateway.example/v1/images/generations"]


def test_openai_base_url_can_come_from_environment(monkeypatch):
    captured_urls: list[str] = []
    monkeypatch.setenv("VULCA_OPENAI_BASE_URL", "https://env-gateway.example")

    def handler(request: httpx.Request) -> httpx.Response:
        captured_urls.append(str(request.url))
        return httpx.Response(200, json={"data": [{"b64_json": "AAAA"}]})

    with _httpx_with_handler(handler):
        asyncio.run(
            OpenAIImageProvider(
                api_key="test-token",
                model="gpt-image-2",
            ).generate("a sunset")
        )

    assert captured_urls == ["https://env-gateway.example/v1/images/generations"]
```

- [ ] **Step 2: Verify RED**

Run:

```bash
PYTHONPATH=src pytest tests/test_openai_provider.py::test_custom_base_url_is_used_for_image_generations tests/test_openai_provider.py::test_openai_base_url_can_come_from_environment -q
```

Expected: failure because `OpenAIImageProvider.__init__` does not accept `base_url` and still hardcodes `https://api.openai.com`.

## Task 2: Implement OpenAI Base URL Support

**Files:**
- Modify: `src/vulca/providers/openai_provider.py`

- [ ] **Step 1: Add URL helpers and constructor field**

Add these helpers near `_mime_for_output_format`:

```python
def _normalize_openai_base_url(base_url: str) -> str:
    url = (base_url or "https://api.openai.com").strip().rstrip("/")
    if not url:
        url = "https://api.openai.com"
    if url.endswith("/v1"):
        return url
    return f"{url}/v1"


def _openai_image_endpoint(base_url: str, endpoint: str) -> str:
    return f"{_normalize_openai_base_url(base_url)}/images/{endpoint}"
```

Change `OpenAIImageProvider.__init__` to:

```python
def __init__(
    self,
    api_key: str = "",
    model: str = "gpt-image-1",
    base_url: str = "",
):
    self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
    self.model = model
    self.base_url = _normalize_openai_base_url(
        base_url
        or os.environ.get("VULCA_OPENAI_BASE_URL", "")
        or os.environ.get("OPENAI_BASE_URL", "")
    )
```

- [ ] **Step 2: Replace hardcoded generation/edit URLs**

In `generate()`, replace:

```python
"https://api.openai.com/v1/images/edits"
```

with:

```python
_openai_image_endpoint(self.base_url, "edits")
```

and replace:

```python
"https://api.openai.com/v1/images/generations"
```

with:

```python
_openai_image_endpoint(self.base_url, "generations")
```

In `inpaint_with_mask()`, replace:

```python
"https://api.openai.com/v1/images/edits"
```

with:

```python
_openai_image_endpoint(self.base_url, "edits")
```

- [ ] **Step 3: Verify GREEN**

Run:

```bash
PYTHONPATH=src pytest tests/test_openai_provider.py::test_custom_base_url_is_used_for_image_generations tests/test_openai_provider.py::test_openai_base_url_can_come_from_environment tests/test_openai_provider.py::test_usage_cost_populates_cost_usd_metadata -q
```

Expected: pass.

## Task 3: Add Harness Real-Provider Contract Tests

**Files:**
- Modify: `tests/test_visual_discovery_benchmark.py`

- [ ] **Step 1: Add real-provider tests**

Append these imports near the top:

```python
import base64
```

Append these tests after `test_harness_forces_litellm_local_cost_map`:

```python
def _tiny_png_b64() -> str:
    return base64.b64encode(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00"
        b"\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00"
        b"\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    ).decode("ascii")


def test_real_provider_requires_env_key_before_provider_construction(
    monkeypatch,
    tmp_path,
):
    import scripts.visual_discovery_benchmark as benchmark

    monkeypatch.delenv("VULCA_REAL_PROVIDER_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def fail_provider(*args, **kwargs):
        raise AssertionError("provider must not be constructed without a key")

    monkeypatch.setattr(benchmark, "OpenAIImageProvider", fail_provider, raising=False)

    with pytest.raises(RuntimeError, match="VULCA_REAL_PROVIDER_API_KEY"):
        benchmark.run_real_provider_experiment(
            real_provider=True,
            provider="openai",
            output_root=tmp_path,
            slug="premium-tea-packaging",
            date="2026-04-30",
        )


def test_real_provider_rejects_unsupported_provider(monkeypatch, tmp_path):
    from scripts.visual_discovery_benchmark import run_real_provider_experiment

    monkeypatch.setenv("VULCA_REAL_PROVIDER_API_KEY", "test-token")

    with pytest.raises(ValueError, match="supported real provider"):
        run_real_provider_experiment(
            real_provider=True,
            provider="gemini",
            output_root=tmp_path,
            slug="premium-tea-packaging",
            date="2026-04-30",
        )


def test_real_provider_writes_images_metadata_and_costs(monkeypatch, tmp_path):
    import scripts.visual_discovery_benchmark as benchmark
    from vulca.providers.base import ImageResult

    constructed: list[dict[str, str]] = []
    prompts: list[str] = []

    class FakeOpenAIProvider:
        def __init__(self, *, api_key: str, model: str, base_url: str):
            constructed.append(
                {"api_key": api_key, "model": model, "base_url": base_url}
            )

        async def generate(self, prompt: str, **kwargs):
            prompts.append(prompt)
            condition_id = chr(ord("A") + len(prompts) - 1)
            return ImageResult(
                image_b64=_tiny_png_b64(),
                mime="image/png",
                metadata={
                    "endpoint": "generations",
                    "condition_id": condition_id,
                    "cost_usd": 0.01,
                },
            )

    monkeypatch.setenv("VULCA_REAL_PROVIDER_API_KEY", "test-token")
    monkeypatch.setenv(
        "VULCA_REAL_PROVIDER_BASE_URL",
        "https://gateway.example/v1/ignored?token=nope",
    )
    monkeypatch.setenv("VULCA_REAL_PROVIDER_MODEL", "gpt-image-2")
    monkeypatch.setattr(benchmark, "OpenAIImageProvider", FakeOpenAIProvider)

    result = benchmark.run_real_provider_experiment(
        real_provider=True,
        provider="openai",
        output_root=tmp_path,
        slug="premium-tea-packaging",
        date="2026-04-30",
    )

    out_dir = Path(result["output_dir"])
    assert constructed == [
        {
            "api_key": "test-token",
            "model": "gpt-image-2",
            "base_url": "https://gateway.example",
        }
    ]
    assert len(prompts) == 4
    for condition_id in ["A", "B", "C", "D"]:
        assert (out_dir / "images" / f"{condition_id}.png").exists()

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["mode"] == "real_provider"
    assert manifest["provider_execution"] == "enabled"
    assert manifest["real_provider"] == {
        "provider": "openai",
        "model": "gpt-image-2",
        "base_url": "https://gateway.example",
    }
    assert "test-token" not in (out_dir / "manifest.json").read_text(encoding="utf-8")

    metadata = json.loads(
        (out_dir / "images" / "metadata.json").read_text(encoding="utf-8")
    )
    assert [item["id"] for item in metadata["conditions"]] == ["A", "B", "C", "D"]
    assert metadata["conditions"][0]["image_path"] == "images/A.png"

    provider_costs = json.loads(
        (out_dir / "provider_costs.json").read_text(encoding="utf-8")
    )
    assert provider_costs["status"] == "collected"
    assert provider_costs["total_usd"] == 0.04
```

- [ ] **Step 2: Verify RED**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_benchmark.py::test_real_provider_requires_env_key_before_provider_construction tests/test_visual_discovery_benchmark.py::test_real_provider_rejects_unsupported_provider tests/test_visual_discovery_benchmark.py::test_real_provider_writes_images_metadata_and_costs -q
```

Expected: failure because `run_real_provider_experiment()` still only accepts `real_provider` and raises `NotImplementedError`.

## Task 4: Implement Harness Real-Provider Execution

**Files:**
- Modify: `scripts/visual_discovery_benchmark.py`

- [ ] **Step 1: Add imports**

Add after `import argparse`:

```python
import asyncio
import base64
from urllib.parse import urlsplit, urlunsplit
```

Add after discovery imports:

```python
from vulca.providers.openai_provider import OpenAIImageProvider
```

- [ ] **Step 2: Add environment and URL helpers**

Add after `_provider_records()`:

```python
def _sanitize_base_url(base_url: str) -> str:
    raw = (base_url or "").strip()
    if not raw:
        return ""
    split = urlsplit(raw)
    if not split.scheme or not split.netloc:
        return raw.rstrip("/")
    netloc = split.hostname or split.netloc
    if split.port:
        netloc = f"{netloc}:{split.port}"
    path = split.path.rstrip("/")
    if path == "/v1":
        path = ""
    return urlunsplit((split.scheme, netloc, path, "", "")).rstrip("/")


def _real_provider_config() -> dict[str, str]:
    api_key = os.environ.get("VULCA_REAL_PROVIDER_API_KEY", "") or os.environ.get(
        "OPENAI_API_KEY", ""
    )
    if not api_key:
        raise RuntimeError(
            "Real provider execution requires VULCA_REAL_PROVIDER_API_KEY "
            "or OPENAI_API_KEY in the environment."
        )
    base_url = (
        os.environ.get("VULCA_REAL_PROVIDER_BASE_URL", "")
        or os.environ.get("VULCA_OPENAI_BASE_URL", "")
        or os.environ.get("OPENAI_BASE_URL", "")
    )
    return {
        "api_key": api_key,
        "base_url": _sanitize_base_url(base_url),
        "model": os.environ.get("VULCA_REAL_PROVIDER_MODEL", "") or "gpt-image-2",
    }


def _decode_image_bytes(image_b64: str) -> bytes:
    if not image_b64:
        raise RuntimeError("provider returned an empty image payload")
    return base64.b64decode(image_b64)
```

- [ ] **Step 3: Add real-provider artifact writer**

Add before `run_real_provider_experiment()`:

```python
async def _write_openai_real_provider_run(
    *,
    output_root: str | Path,
    slug: str,
    date: str | None,
    config: dict[str, str],
) -> dict[str, str]:
    dry_result = write_experiment_dry_run(
        output_root=output_root,
        slug=slug,
        date=date,
    )
    out_dir = Path(dry_result["output_dir"])
    project = get_experiment_project(slug)
    card = select_direction_card(project)
    conditions = build_conditions(project.prompt, card)
    images_dir = out_dir / "images"
    provider = OpenAIImageProvider(
        api_key=config["api_key"],
        model=config["model"],
        base_url=config["base_url"],
    )

    image_records: list[dict[str, Any]] = []
    costs: list[dict[str, Any]] = []
    total_usd = 0.0

    for condition in conditions:
        result = await provider.generate(
            condition["prompt"],
            negative_prompt=str(condition.get("negative_prompt", "")),
            width=1024,
            height=1024,
            output_format="png",
            raw_prompt=True,
        )
        image_path = images_dir / f"{condition['id']}.png"
        image_path.write_bytes(_decode_image_bytes(result.image_b64))
        metadata = dict(result.metadata or {})
        image_records.append(
            {
                "id": condition["id"],
                "image_path": f"images/{condition['id']}.png",
                "mime": result.mime,
                "metadata": metadata,
            }
        )
        cost = metadata.get("cost_usd")
        if isinstance(cost, (int, float)):
            total_usd += float(cost)
            costs.append(
                {
                    "condition_id": condition["id"],
                    "cost_usd": float(cost),
                }
            )

    _write_json(
        images_dir / "metadata.json",
        {
            "schema_version": "0.1",
            "provider": "openai",
            "model": config["model"],
            "conditions": image_records,
        },
    )
    _write_json(
        out_dir / "provider_costs.json",
        {
            "schema_version": "0.1",
            "status": "collected" if costs else "unavailable",
            "providers": [
                {
                    "provider": "openai",
                    "model": config["model"],
                    "base_url": config["base_url"],
                    "conditions": costs,
                }
            ],
            "total_usd": round(total_usd, 6),
        },
    )

    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    manifest["mode"] = "real_provider"
    manifest["provider_execution"] = "enabled"
    manifest["real_provider"] = {
        "provider": "openai",
        "model": config["model"],
        "base_url": config["base_url"],
    }
    for provider_record in manifest["providers"]:
        if provider_record["provider"] == "openai":
            provider_record["execution"] = "run"
    _write_json(out_dir / "manifest.json", manifest)

    summary = f"""# Cultural-Term Efficacy Real Provider Run: {project.slug}

## Status
real_provider

## Provider
openai-compatible image endpoint

## Model
{config["model"]}

## Conditions
{chr(10).join(f"- {item['id']}: {item['label']}" for item in conditions)}

## Decision Boundary
Images were generated, but no quality conclusion can be drawn until human
ranking and `/evaluate` results are collected.
"""
    (out_dir / "summary.md").write_text(summary, encoding="utf-8")
    return dry_result
```

- [ ] **Step 4: Replace `run_real_provider_experiment()`**

Replace the existing function with:

```python
def run_real_provider_experiment(
    *,
    real_provider: bool = False,
    provider: str = "openai",
    output_root: str | Path = "docs/product/experiments/results",
    slug: str = "premium-tea-packaging",
    date: str | None = None,
) -> dict[str, str]:
    if not real_provider:
        raise RuntimeError(
            "Real provider execution requires explicit opt-in and is disabled "
            "for the dry-run harness."
        )
    if provider != "openai":
        raise ValueError("supported real provider: openai")
    config = _real_provider_config()
    return asyncio.run(
        _write_openai_real_provider_run(
            output_root=output_root,
            slug=slug,
            date=date,
            config=config,
        )
    )
```

- [ ] **Step 5: Update CLI**

In `main()`, add:

```python
parser.add_argument("--provider", default="openai")
```

Replace:

```python
if args.real_provider:
    run_real_provider_experiment(real_provider=True)
```

with:

```python
if args.real_provider:
    slugs = (
        [project.slug for project in build_experiment_projects()]
        if args.slug == "all"
        else [args.slug]
    )
    for slug in slugs:
        run_real_provider_experiment(
            real_provider=True,
            provider=args.provider,
            output_root=args.output_root,
            slug=slug,
            date=args.date,
        )
    return 0
```

- [ ] **Step 6: Verify GREEN**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_benchmark.py::test_real_provider_requires_env_key_before_provider_construction tests/test_visual_discovery_benchmark.py::test_real_provider_rejects_unsupported_provider tests/test_visual_discovery_benchmark.py::test_real_provider_writes_images_metadata_and_costs -q
```

Expected: pass.

## Task 5: Update Docs and Secret Guard Tests

**Files:**
- Modify: `tests/test_visual_discovery_docs_truth.py`
- Modify: `docs/product/experiments/cultural-term-efficacy.md`

- [ ] **Step 1: Add docs secret guard test**

Append this test to `tests/test_visual_discovery_docs_truth.py`:

```python
def test_real_provider_docs_do_not_contain_live_credentials():
    public_text = "\n".join(
        [
            (ROOT / "docs" / "product" / "experiments" / "cultural-term-efficacy.md")
            .read_text(encoding="utf-8"),
            (
                ROOT
                / "docs"
                / "superpowers"
                / "specs"
                / "2026-04-30-cultural-term-real-provider-opt-in-design.md"
            ).read_text(encoding="utf-8"),
        ]
    )

    assert "sk-" not in public_text
    assert "global" + "ai" not in public_text.lower()
    assert "example.openai-compatible-gateway.test" in public_text
```

- [ ] **Step 2: Verify RED**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_docs_truth.py::test_real_provider_docs_do_not_contain_live_credentials -q
```

Expected: failure because `docs/product/experiments/cultural-term-efficacy.md` does not yet contain the safe example host.

- [ ] **Step 3: Update experiment docs**

In `docs/product/experiments/cultural-term-efficacy.md`, after the existing harness paragraph, add:

```markdown
Real provider execution requires explicit opt-in:

```bash
VULCA_REAL_PROVIDER_BASE_URL=https://example.openai-compatible-gateway.test \
VULCA_REAL_PROVIDER_API_KEY=... \
VULCA_REAL_PROVIDER_MODEL=gpt-image-2 \
PYTHONPATH=src python3 scripts/visual_discovery_benchmark.py \
  --real-provider \
  --provider openai \
  --slug premium-tea-packaging \
  --output-root /private/tmp/vulca-cultural-term-real-provider \
  --date 2026-04-30
```

Never put live API keys in repository files, generated artifacts, PR bodies, or documentation. Use local environment variables or a secret manager.
```

- [ ] **Step 4: Verify docs tests pass**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_docs_truth.py -q
```

Expected: pass.

## Task 6: Final Verification and Commit

**Files:**
- All files above.

- [ ] **Step 1: Run focused tests**

Run:

```bash
PYTHONPATH=src pytest tests/test_visual_discovery_benchmark.py tests/test_visual_discovery_docs_truth.py -q
```

Expected: pass.

- [ ] **Step 2: Verify dry run still works**

Run:

```bash
PYTHONPATH=src python3 scripts/visual_discovery_benchmark.py --output-root /private/tmp/vulca-cultural-term-dry-run --date 2026-04-30
```

Expected: exits 0 and writes three dry-run directories.

- [ ] **Step 3: Verify real-provider missing key fails before network**

Run:

```bash
env -u VULCA_REAL_PROVIDER_API_KEY -u OPENAI_API_KEY PYTHONPATH=src python3 scripts/visual_discovery_benchmark.py --real-provider --provider openai --slug premium-tea-packaging --output-root /private/tmp/vulca-cultural-term-missing-key --date 2026-04-30
```

Expected: non-zero exit with a message naming `VULCA_REAL_PROVIDER_API_KEY` or `OPENAI_API_KEY`; no real network call.

- [ ] **Step 4: Scan for secrets and unfinished markers**

Run:

```bash
grep -RInE "(^|[^[:alpha:]])s[k]-[A-Za-z0-9]|globala[i]|TB[D]|TO[D]O|lo[r]em|coming soo[n]" scripts/visual_discovery_benchmark.py src/vulca/providers/openai_provider.py tests/test_visual_discovery_benchmark.py tests/test_visual_discovery_docs_truth.py docs/product/experiments/cultural-term-efficacy.md docs/superpowers/specs/2026-04-30-cultural-term-real-provider-opt-in-design.md docs/superpowers/plans/2026-04-30-cultural-term-real-provider-opt-in.md
```

Expected: no matches.

- [ ] **Step 5: Check whitespace**

Run:

```bash
git diff --check
```

Expected: no output.

- [ ] **Step 6: Commit implementation**

Run:

```bash
git add src/vulca/providers/openai_provider.py scripts/visual_discovery_benchmark.py tests/test_visual_discovery_benchmark.py tests/test_visual_discovery_docs_truth.py docs/product/experiments/cultural-term-efficacy.md docs/superpowers/plans/2026-04-30-cultural-term-real-provider-opt-in.md
git commit -m "feat: add real provider opt-in for cultural term harness"
```
