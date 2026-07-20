import os
from typing import Any

from dotenv import load_dotenv

from ai_assistant.app.ollama_client import (
    summarize_result_with_ollama,
)


load_dotenv(override=False)


def generate_summary(
    question: str,
    sql_query: str,
    rows: list[dict[str, Any]],
) -> str:
    provider = os.getenv(
        "AI_PROVIDER",
        "mock",
    ).strip().lower()

    if not rows:
        return "No data found for this question."

    if provider == "mock":
        return (
            f"Found {len(rows)} result rows for the question: "
            f"'{question}'."
        )

    if provider == "ollama":
        return summarize_result_with_ollama(
            question=question,
            sql_query=sql_query,
            rows=rows,
        )

    raise ValueError(
        f"Unsupported AI_PROVIDER: {provider}. "
        "Supported providers: mock, ollama."
    )