"""Optional LLM layer: send the collected static-analysis findings to OpenRouter
for a short, prioritized narrative summary. Requires OPENROUTER_API_KEY."""

from __future__ import annotations

import json
import os
from urllib.request import Request, urlopen

SYSTEM_PROMPT = (
    "You are a pragmatic senior engineer reviewing automated static-analysis "
    "results for a codebase. You did not read the code yourself; you only see "
    "these aggregated metrics. Write exactly one short paragraph of 70-100 words. "
    "Start with the single biggest risk. Then give exactly 3 short next steps in "
    "priority order. Make it direct, plain, and free of headings, bullets, bolding, "
    "or markdown. Do not repeat raw numbers verbatim; interpret them."
)

FREE_MODELS = [
    "cohere/north-mini-code:free",
    "nvidia/nemotron-3.5-content-safety:free",
    "nvidia/nemotron-3-ultra:free",
    "nvidia/nemotron-3-nano-omni:free",
    "poolside/laguna-m1:free",
    "google/gemma-4-26b-a4b:free",
    "google/gemma-4-31b:free",
    "nvidia/nemotron-3-super:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "nvidia/nemotron-nano-12b-2-vl:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "openai/gpt-oss-20b:free",
]


def get_llm_summary(
    project_name: str,
    overall_score: int,
    category_results: dict,
    model_name: str | None = None,
) -> str | None:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return None

    findings = {category: result["details"] for category, result in category_results.items()}
    prompt = (
        f"Project: {project_name}\n"
        f"Overall health score: {overall_score}/100\n\n"
        f"Category findings:\n{json.dumps(findings, indent=2, default=str)}"
    )

    resolved_model = model_name or os.environ.get("OPENROUTER_MODEL", "cohere/north-mini-code:free")
    payload = {
        "model": resolved_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 400,
    }

    request = Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=20) as response:
            body = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 - surface any API error as text, don't crash the scan
        return f"LLM summary unavailable ({exc.__class__.__name__}: {exc})"

    try:
        content = body["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return "LLM summary unavailable (unexpected OpenRouter response)"

    if isinstance(content, list):
        text_blocks = [
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        ]
        content = "\n".join(text_blocks).strip()
    else:
        content = str(content).strip()

    if not content:
        return None

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    if len(lines) > 1:
        content = " ".join(lines)

    content = content.replace("**", "").replace("- ", "")
    content = " ".join(content.split())
    return content
