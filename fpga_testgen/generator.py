"""Gemini API integration for testbench generation."""

from __future__ import annotations
import json
import re
from google import genai
from .config import settings
from .schemas import VerilogModule
from .prompts import SYSTEM_PROMPT, build_prompt, build_feedback_prompt


def _extract_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown code fences."""
    # Try direct JSON parse first
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Could not parse JSON from response: {text[:200]}")


def _create_client() -> genai.Client:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    return genai.Client(api_key=settings.gemini_api_key)


def generate_testbench(
    module: VerilogModule,
    previous_errors: list[str] | None = None,
    previous_tb: str | None = None,
) -> tuple[str, str]:
    """Generate a testbench for the given module.

    Returns (testbench_code, description).
    """
    client = _create_client()

    if previous_errors and previous_tb:
        user_prompt = build_feedback_prompt(module, previous_tb, previous_errors)
    else:
        user_prompt = build_prompt(module)

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=[{"role": "user", "parts": [{"text": user_prompt}]}],
        config={
            "system_instruction": SYSTEM_PROMPT,
            "response_mime_type": "application/json",
            "temperature": 0.2,
        },
    )

    result = _extract_json(response.text)
    testbench = result.get("testbench", "")
    description = result.get("description", "")

    if not testbench:
        raise ValueError("LLM returned empty testbench")

    return testbench, description
