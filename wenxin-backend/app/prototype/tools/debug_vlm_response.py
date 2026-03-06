"""Debug VLM raw response — diagnose JSON truncation issue.

Sends a real image to Gemini 2.5 Flash via direct API
and dumps the FULL raw response to identify truncation cause.

Usage:
    export $(grep -E '^(GOOGLE_API_KEY|GEMINI_API_KEY)=' .env | xargs)
    ./venv/bin/python3 app/prototype/tools/debug_vlm_response.py
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import sys
import time
from pathlib import Path


def find_test_image() -> str | None:
    """Find any checkpoint image for testing."""
    cp_dir = Path("app/prototype/checkpoints/draft")
    if cp_dir.exists():
        # Images are inside subdirectories
        for f in sorted(cp_dir.glob("**/*.png"))[:1]:
            return str(f)
        for f in sorted(cp_dir.glob("**/*.jpg"))[:1]:
            return str(f)
    return None


async def test_vlm_direct(image_path: str) -> None:
    """Call VLM directly and dump full response."""
    import litellm

    # Read and encode image
    img_data = Path(image_path).read_bytes()
    img_b64 = base64.b64encode(img_data).decode("ascii")

    # Detect MIME
    if img_data[:4] == b"\x89PNG":
        mime = "image/png"
    elif img_data[:2] == b"\xff\xd8":
        mime = "image/jpeg"
    else:
        mime = "image/png"

    print(f"Image: {image_path} ({len(img_data)} bytes, {mime})")

    # Use the exact same prompt as vlm_critic.py
    system_prompt = (
        "You are an expert art critic evaluating AI-generated artwork across 5 cultural\n"
        "dimensions. You will see an image and its context. Score each dimension 0.0-1.0.\n\n"
        "Scoring guide:\n"
        "- 0.0-0.2: Poor / major issues\n"
        "- 0.2-0.4: Below average / noticeable problems\n"
        "- 0.4-0.6: Average / acceptable\n"
        "- 0.6-0.8: Good / well-executed\n"
        "- 0.8-1.0: Excellent / masterful\n\n"
        "Dimensions:\n"
        "- L1 (Visual Perception): Composition, layout, spatial arrangement, visual clarity\n"
        "- L2 (Technical Execution): Rendering quality, detail, technique fidelity, resolution\n"
        "- L3 (Cultural Context): Fidelity to cultural tradition, correct terminology usage\n"
        "- L4 (Critical Interpretation): No taboo violations, respectful representation\n"
        "- L5 (Philosophical/Aesthetic): Artistic depth, emotional resonance, aesthetic harmony\n\n"
        'Output ONLY valid JSON (no markdown, no explanation):\n'
        '{"L1": 0.XX, "L2": 0.XX, "L3": 0.XX, "L4": 0.XX, "L5": 0.XX,\n'
        ' "L1_rationale": "brief reason",\n'
        ' "L2_rationale": "brief reason",\n'
        ' "L3_rationale": "brief reason",\n'
        ' "L4_rationale": "brief reason",\n'
        ' "L5_rationale": "brief reason"}'
    )

    user_text = (
        "Evaluate this AI-generated artwork.\n\n"
        "Subject: test artwork\n"
        "Cultural Tradition: chinese ink\n"
        "Generation Prompt: a landscape painting\n\n"
        "Score all 5 dimensions (L1-L5) as JSON."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime};base64,{img_b64}",
                    },
                },
                {
                    "type": "text",
                    "text": user_text,
                },
            ],
        },
    ]

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""

    if not api_key:
        print("ERROR: No API key found (GOOGLE_API_KEY or GEMINI_API_KEY)")
        sys.exit(1)

    print(f"API key: {api_key[:8]}...{api_key[-4:]}")
    print(f"Model: gemini/gemini-2.5-flash")

    # Test with different max_tokens values
    for max_tok in [512, 1024, 2048]:
        print(f"\n{'='*60}")
        print(f"Testing max_tokens={max_tok}")
        print(f"{'='*60}")

        t0 = time.monotonic()
        try:
            response = await litellm.acompletion(
                model="gemini/gemini-2.5-flash",
                messages=messages,
                max_tokens=max_tok,
                temperature=0.1,
                timeout=30,
                api_key=api_key,
            )
            elapsed = int((time.monotonic() - t0) * 1000)

            content = response.choices[0].message.content or ""
            finish_reason = response.choices[0].finish_reason
            usage = getattr(response, "usage", None)

            print(f"Latency: {elapsed}ms")
            print(f"Finish reason: {finish_reason}")
            if usage:
                print(f"Tokens: prompt={getattr(usage, 'prompt_tokens', '?')}, "
                      f"completion={getattr(usage, 'completion_tokens', '?')}")
            print(f"Content length: {len(content)} chars")
            print(f"--- RAW CONTENT START ---")
            print(content)
            print(f"--- RAW CONTENT END ---")

            # Try to parse
            text = content.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                if lines[-1].strip() == "```":
                    inner = "\n".join(lines[1:-1])
                else:
                    inner = "\n".join(lines[1:])
                text = inner.strip()

            try:
                data = json.loads(text)
                print(f"JSON parse: SUCCESS")
                print(f"Keys: {list(data.keys())}")
                scores = {k: data[k] for k in ("L1", "L2", "L3", "L4", "L5") if k in data}
                print(f"Scores: {scores}")
            except json.JSONDecodeError as e:
                print(f"JSON parse: FAILED - {e}")
                # Try extracting JSON
                start = text.find("{")
                end = text.rfind("}") + 1
                print(f"JSON markers: start={start}, end_brace_pos={text.rfind('}')}")
                if start >= 0 and end > start:
                    try:
                        data = json.loads(text[start:end])
                        print(f"Extracted JSON parse: SUCCESS")
                        print(f"Keys: {list(data.keys())}")
                    except json.JSONDecodeError as e2:
                        print(f"Extracted JSON parse: FAILED - {e2}")
                else:
                    print("No closing brace found — response is TRUNCATED")

        except Exception as exc:
            elapsed = int((time.monotonic() - t0) * 1000)
            print(f"ERROR ({elapsed}ms): {type(exc).__name__}: {exc}")


def main() -> None:
    img = find_test_image()
    if not img:
        print("No test image found in checkpoints/draft/")
        sys.exit(1)

    asyncio.run(test_vlm_direct(img))


if __name__ == "__main__":
    main()
