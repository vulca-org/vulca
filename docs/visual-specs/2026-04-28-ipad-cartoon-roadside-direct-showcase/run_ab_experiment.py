from __future__ import annotations

import json
import os
import time
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parent
REFERENCE = ROOT / "source" / "reference_1536x1024.png"
MASK = ROOT / "source" / "full_edit_mask_1536x1024.png"
OUT_DIR = ROOT / "iters" / "ab"
RESULTS = OUT_DIR / "results.json"

ARMS = [
    {
        "name": "naive",
        "prompt": ROOT / "prompts" / "naive_prompt.txt",
        "output": OUT_DIR / "naive_gpt_image_2.png",
    },
    {
        "name": "vulca_structured",
        "prompt": ROOT / "prompts" / "vulca_structured_prompt.txt",
        "output": OUT_DIR / "vulca_structured_gpt_image_2.png",
    },
]


def _write_results(payload: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def _call_edit(*, api_key: str, prompt: str) -> tuple[int, str, bytes | None]:
    headers = {"Authorization": f"Bearer {api_key}"}
    with httpx.Client(timeout=180) as client:
        with open(REFERENCE, "rb") as image_fh, open(MASK, "rb") as mask_fh:
            files = {
                "image": ("reference_1536x1024.png", image_fh, "image/png"),
                "mask": ("full_edit_mask_1536x1024.png", mask_fh, "image/png"),
            }
            data = {
                "model": "gpt-image-2",
                "prompt": prompt,
                "n": "1",
                "size": "1536x1024",
                "quality": "high",
            }
            response = client.post(
                "https://api.openai.com/v1/images/edits",
                headers=headers,
                files=files,
                data=data,
            )

    body = response.text
    if response.status_code != 200:
        return response.status_code, body, None

    payload = response.json()
    image_b64 = payload["data"][0].get("b64_json") or payload["data"][0].get("b64")
    if not image_b64:
        return 200, body, None

    import base64

    return 200, body, base64.b64decode(image_b64)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        _write_results(
            {
                "verdict": "blocked_missing_openai_api_key",
                "blocked_reason": "OPENAI_API_KEY is not set.",
            }
        )
        return 2

    if not REFERENCE.exists() or not MASK.exists():
        _write_results(
            {
                "verdict": "blocked_missing_inputs",
                "reference_exists": REFERENCE.exists(),
                "mask_exists": MASK.exists(),
            }
        )
        return 2

    rows: list[dict] = []
    for arm in ARMS:
        prompt = arm["prompt"].read_text()
        started = time.time()
        status, body, image_bytes = _call_edit(api_key=api_key, prompt=prompt)
        elapsed = round(time.time() - started, 2)

        if status != 200:
            blocked = "Billing hard limit has been reached" in body
            verdict = (
                "blocked_billing_hard_limit_reached"
                if blocked
                else "failed_provider_error"
            )
            _write_results(
                {
                    "verdict": verdict,
                    "blocked_reason": "OpenAI billing hard limit reached."
                    if blocked
                    else "OpenAI returned a non-200 response.",
                    "failed_arm": arm["name"],
                    "status_code": status,
                    "response_body": body,
                    "completed_arms": rows,
                }
            )
            return 1

        if image_bytes is None:
            _write_results(
                {
                    "verdict": "failed_missing_image_bytes",
                    "failed_arm": arm["name"],
                    "status_code": status,
                    "response_body": body,
                    "completed_arms": rows,
                }
            )
            return 1

        arm["output"].write_bytes(image_bytes)
        rows.append(
            {
                "arm": arm["name"],
                "output": str(arm["output"]),
                "wall_time_sec": elapsed,
                "status_code": status,
                "bytes": len(image_bytes),
            }
        )

    _write_results(
        {
            "verdict": "completed",
            "provider": "openai",
            "model": "gpt-image-2",
            "endpoint": "images/edits",
            "reference": str(REFERENCE),
            "mask": str(MASK),
            "arms": rows,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
