class UnsupportedQuestionError(ValueError):
    """Raised when the assistant does not support the requested analysis."""

    pass


FORECAST_PHRASES = [
    "przyszł",
    "prognoz",
    "przewid",
    "będzie sprzedaż",
    "następny rok",
    "następnym roku",
    "następny miesiąc",
    "forecast",
    "predict",
    "prediction",
    "future sales",
    "next year",
    "next month",
]


def validate_question(question: str) -> None:
    normalized_question = question.strip().lower()

    if not normalized_question:
        raise ValueError("Question cannot be empty.")

    if len(normalized_question) > 500:
        raise ValueError("Question cannot be longer than 500 characters.")

    if any(
        phrase in normalized_question
        for phrase in FORECAST_PHRASES
    ):
        raise UnsupportedQuestionError(
            "Prognozowanie nie jest jeszcze dostępne. "
            "Asystent obsługuje obecnie analizę danych historycznych."
        )