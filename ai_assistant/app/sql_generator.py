import os

from dotenv import load_dotenv

from ai_assistant.app.mock_ai import generate_sql_with_mock
from ai_assistant.app.ollama_client import generate_sql_with_ollama


load_dotenv(override=False)


def generate_sql(question: str) -> str:
    provider = os.getenv(
        "AI_PROVIDER",
        "mock",
    ).strip().lower()

    if provider == "mock":
        return generate_sql_with_mock(question)

    if provider == "ollama":
        return generate_sql_with_ollama(question)

    raise ValueError(
        f"Unsupported AI_PROVIDER: {provider}. "
        "Supported providers: mock, ollama."
    )