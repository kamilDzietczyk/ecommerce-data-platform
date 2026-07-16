import os

from dotenv import load_dotenv

from ai_assistant.app.mock_ai import generate_sql_with_mock


load_dotenv(override=False)


def generate_sql(question: str) -> str:
    provider = os.getenv("AI_PROVIDER", "mock").lower()

    if provider == "mock":
        return generate_sql_with_mock(question)

    raise ValueError(
        f"Unsupported AI_PROVIDER: {provider}. "
        "Currently supported providers: mock."
    )