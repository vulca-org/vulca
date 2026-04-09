# Retry Exception Map

What exceptions each provider raises, and how the two retry layers handle them.

## Two retry layers

1. **Provider-internal retry** (`vulca.providers.retry.with_retry`) — inside each provider's `generate()`. Retries based on `_is_retryable(exc)` predicate. Budget: 3 retries, exponential backoff 500ms–16s.

2. **Orchestration retry** (`vulca.layers.layered_generate._call_provider_with_retry`) — wraps the entire `_call_provider()` call. Catches any `Exception` except `AssertionError`/`TypeError`/`CancelledError`. Budget: 2 retries, jittered backoff 0–2s.

A transient failure hits provider-internal retry first. If all 4 provider attempts fail, the last exception propagates to orchestration retry, which tries 3 more times (each of which internally retries 4 times). Worst case: 3 × 4 = 12 provider calls.

## Gemini (`vulca.providers.gemini.GeminiImageProvider`)

| Exception | Source | Provider-internal retryable? | Orchestration retryable? |
|---|---|---|---|
| `asyncio.TimeoutError` → wrapped as `TimeoutError` | `asyncio.wait_for` timeout | Yes (`_is_retryable` returns True) | Yes (subclass of `Exception`) |
| Google API 429 (rate limit) | `google.genai` client | Yes (status_code=429) | Yes |
| Google API 500 (server error) | `google.genai` client | Yes (status_code=500) | Yes |
| Google API 503 (unavailable) | `google.genai` client | Yes (status_code=503) | Yes |
| Google API 400 (bad request) | `google.genai` client | No (not in retryable set) | Yes (but shouldn't — deterministic failure) |
| Google API 403 (forbidden) | `google.genai` client | No | Yes (but shouldn't) |
| `RuntimeError("Gemini returned no image data")` | No candidates in response | No | Yes (but shouldn't — deterministic) |
| `ValueError("GEMINI_API_KEY required")` | Missing API key | No | Yes (but shouldn't — deterministic) |

### Risk: deterministic failures retried at orchestration layer

`ValueError` (missing key), `RuntimeError` (no image data), and 400/403 errors are **not transient** but will be retried by the orchestration layer (which catches all `Exception`). This wastes the retry budget on unrecoverable errors. Acceptable for now — retry budget is only 2, so worst case is 3 wasted calls. Future improvement: orchestration retry could have its own `_is_retryable` predicate.

## OpenAI (`vulca.providers.openai_provider.OpenAIImageProvider`)

| Exception | Source | Provider-internal retryable? | Orchestration retryable? |
|---|---|---|---|
| `httpx.HTTPStatusError` with 429 | Rate limit | Yes | Yes |
| `httpx.HTTPStatusError` with 500 | Server error | Yes | Yes |
| `httpx.HTTPStatusError` with 503 | Unavailable | Yes | Yes |
| `httpx.TimeoutException` | Network timeout | Yes | Yes |
| `httpx.ConnectError` | Network failure | Yes | Yes |
| `httpx.HTTPStatusError` with 400 | Bad request | No | Yes (but shouldn't) |
| `ValueError("OpenAI API key required")` | Missing API key | No | Yes (but shouldn't) |

Same risk pattern as Gemini: deterministic failures are retried at orchestration level.

## ComfyUI (`vulca.providers.comfyui.ComfyUIImageProvider`)

No internal retry — relies entirely on orchestration retry. All exceptions from the ComfyUI HTTP API (httpx errors) will be caught and retried.

## Exception taxonomy in orchestration retry

```python
# _call_provider_with_retry
except (AssertionError, TypeError, asyncio.CancelledError):
    raise  # programmer bugs / control flow — never retry
except Exception as exc:
    # everything else — retry up to budget
```

**Propagated immediately (not retried):**
- `AssertionError` — programmer bug (e.g. shape mismatch in keying)
- `TypeError` — programmer bug (e.g. wrong argument types)
- `asyncio.CancelledError` — task cancellation (BaseException in Python 3.9+, but listed explicitly for AssertionError/TypeError which ARE Exception subclasses)

**Retried (may be wrong for deterministic failures):**
- All other `Exception` subclasses — including `ValueError`, `RuntimeError`, `httpx.HTTPStatusError` with 400/403

## Recommendations (not blocking, for future consideration)

1. **Add `_is_retryable` to orchestration retry** — skip retry for `ValueError`, `RuntimeError("no image data")`, and HTTP 4xx (except 429). This would avoid wasting retry budget on deterministic failures.

2. **Monitor `attempts > 1` rate** (item 8 from backlog) — if orchestration retry never fires in production, the entire mechanism may be unnecessary complexity.

3. **Consider whether two retry layers are needed** — provider-internal retry (4 attempts) + orchestration retry (3 attempts) = up to 12 calls. If provider-internal retry handles all transient cases, orchestration retry may be redundant.
