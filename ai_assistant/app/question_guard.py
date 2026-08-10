class UnsupportedQuestionError(ValueError):
    """Raised when the requested analysis is not supported."""

    pass


FUTURE_PHRASES = [
    "przyszł",
    "prognoz",
    "przewid",
    "będzie",
    "będą",
    "forecast",
    "predict",
    "prediction",
    "future",
    "will",
    "next year",
    "next month",
]


UNSUPPORTED_FORECAST_DIMENSIONS = [
    "produkt",
    "product",
    "kategoria",
    "category",
    "klient",
    "customer",
]


def validate_question(question: str) -> None:
    normalized_question = (
        question
        .strip()
        .lower()
    )

    if not normalized_question:
        raise ValueError(
            "Question cannot be empty."
        )

    if len(normalized_question) > 500:
        raise ValueError(
            "Question cannot be longer than 500 characters."
        )

    is_forecast_question = any(
        phrase in normalized_question
        for phrase in FUTURE_PHRASES
    )

    asks_for_unsupported_dimension = any(
        dimension in normalized_question
        for dimension in UNSUPPORTED_FORECAST_DIMENSIONS
    )

    if (
        is_forecast_question
        and asks_for_unsupported_dimension
    ):
        raise UnsupportedQuestionError(
            "Prognozowanie jest obecnie dostępne "
            "tylko dla całkowitej miesięcznej sprzedaży. "
            "Prognozy produktów, kategorii i klientów "
            "nie są obecnie dostępne."
        )