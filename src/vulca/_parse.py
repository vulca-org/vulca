"""Robust JSON parsing for LLM outputs."""

from __future__ import annotations

import json
import re


def parse_llm_json(text: str) -> dict:
    """Parse JSON from LLM output, handling common formatting issues.

    Handles: markdown fences, trailing commas, single quotes,
    comments, and other non-standard JSON from LLMs.
    """
    # Strip markdown code fences
    if "```" in text:
        # Extract content between fences
        match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
        if match:
            text = match.group(1).strip()

    # Try standard parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Fix trailing commas before } or ]
    text = re.sub(r",\s*([}\]])", r"\1", text)

    # Fix single quotes → double quotes (careful with apostrophes in text)
    # Only replace quotes that look like JSON keys/values
    text = re.sub(r"(?<=[\[{,:])\s*'([^']*?)'\s*(?=[,}\]:])", r' "\1"', text)

    # Remove inline comments
    text = re.sub(r"//.*?$", "", text, flags=re.MULTILINE)

    # Try again
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Last resort: find the first { ... } block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        candidate = match.group(0)
        candidate = re.sub(r",\s*([}\]])", r"\1", candidate)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse JSON from LLM output: {text[:200]}...")
