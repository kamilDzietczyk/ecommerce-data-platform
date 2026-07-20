import json
import os
import re
from typing import Any

import httpx
from dotenv import load_dotenv

from ai_assistant.app.schema_context import MARTS_SCHEMA_CONTEXT


load_dotenv(override=False)


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(
            f"Missing required environment variable: {name}"
        )

    return value


def clean_model_response(response_text: str) -> str:
    cleaned_text = response_text.strip()

    cleaned_text = re.sub(
        r"^```(?:sql)?\s*",
        "",
        cleaned_text,
        flags=re.IGNORECASE,
    )

    cleaned_text = re.sub(
        r"\s*```$",
        "",
        cleaned_text,
    )

    return cleaned_text.strip()


def call_ollama(messages: list[dict[str, str]]) -> str:
    base_url = get_required_env("OLLAMA_BASE_URL").rstrip("/")
    model = get_required_env("OLLAMA_MODEL")

    timeout_seconds = float(
        os.getenv("OLLAMA_TIMEOUT_SECONDS", "180")
    )

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0,
        },
    }

    try:
        with httpx.Client(timeout=timeout_seconds) as client:
            response = client.post(
                f"{base_url}/api/chat",
                json=payload,
            )

            response.raise_for_status()

    except httpx.ConnectError as error:
        raise RuntimeError(
            "Cannot connect to Ollama. Check whether Ollama is running "
            "and whether OLLAMA_HOST is set to 0.0.0.0:11434."
        ) from error

    except httpx.TimeoutException as error:
        raise RuntimeError(
            f"Ollama did not respond within {timeout_seconds} seconds."
        ) from error

    except httpx.HTTPStatusError as error:
        raise RuntimeError(
            f"Ollama returned HTTP {error.response.status_code}: "
            f"{error.response.text}"
        ) from error

    response_data = response.json()

    generated_content = (
        response_data
        .get("message", {})
        .get("content", "")
    )

    if not generated_content.strip():
        raise RuntimeError("Ollama returned an empty response.")

    return generated_content.strip()


def generate_sql_with_ollama(question: str) -> str:
    system_prompt = f"""
You are a PostgreSQL analytics SQL generator.

Generate exactly one safe, read-only SQL query.

Rules:
- Return SQL only.
- Do not provide explanations.
- Do not use Markdown code blocks.
- Use only SELECT or WITH.
- Use only tables from the marts schema.
- Never access raw, staging, public or information_schema.
- Never use INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE,
  CREATE, GRANT, REVOKE, COPY, CALL or EXECUTE.
- Limit detailed result sets to a maximum of 50 rows.
- Use PostgreSQL syntax.
- Use only columns listed in the schema context.

Available schema:

{MARTS_SCHEMA_CONTEXT}
""".strip()

    generated_sql = call_ollama(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": question,
            },
        ]
    )

    return clean_model_response(generated_sql)


def summarize_result_with_ollama(
    question: str,
    sql_query: str,
    rows: list[dict[str, Any]],
) -> str:
    if not rows:
        return "Nie znaleziono danych odpowiadających temu pytaniu."

    # Nie wysyłamy modelowi nieograniczonej liczby rekordów.
    result_sample = rows[:20]

    serialized_result = json.dumps(
        result_sample,
        ensure_ascii=False,
        default=str,
    )

    system_prompt = """
You are an ecommerce data analyst.

Rules:
- Answer in the same language as the user's question.
- Base your answer only on the provided query result.
- Do not invent causes, values or conclusions.
- Mention the most important values from the result.
- Keep the answer concise: maximum three sentences.
- Do not use Markdown tables.
- Do not describe technical implementation details.
""".strip()

    user_prompt = f"""
User question:
{question}

Executed SQL:
{sql_query}

Number of returned rows:
{len(rows)}

Query result sample:
{serialized_result}
""".strip()

    return call_ollama(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]
    )