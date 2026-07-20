import os

from dotenv import load_dotenv

from ai_assistant.app.mock_ai import generate_sql_with_mock
from ai_assistant.app.ollama_client import (
    generate_sql_with_ollama,
    repair_sql_with_ollama,
)


load_dotenv(override=False)


def get_provider() -> str:
    return os.getenv(
        "AI_PROVIDER",
        "mock",
    ).strip().lower()


def generate_sql(question: str) -> str:
    provider = get_provider()

    if provider == "mock":
        return generate_sql_with_mock(question)

    if provider == "ollama":
        return generate_sql_with_ollama(question)

    raise ValueError(
        f"Unsupported AI_PROVIDER: {provider}. "
        "Supported providers: mock, ollama."
    )


def repair_sql(
    question: str,
    failed_sql: str,
    database_error: str,
) -> str:
    provider = get_provider()

    if provider == "ollama":
        return repair_sql_with_ollama(
            question=question,
            failed_sql=failed_sql,
            database_error=database_error,
        )

    # Mock ma deterministyczne, wcześniej zdefiniowane SQL-e.
    return generate_sql_with_mock(question)