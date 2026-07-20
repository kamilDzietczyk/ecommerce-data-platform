import os
from typing import Any

from ai_assistant.app.db import (
    QueryExecutionError,
    execute_select_query,
)
from ai_assistant.app.question_guard import validate_question
from ai_assistant.app.sql_generator import (
    generate_sql,
    repair_sql,
)
from ai_assistant.app.sql_guard import validate_sql
from ai_assistant.app.summary_generator import generate_summary


def answer_question(
    question: str,
) -> dict[str, Any]:
    validate_question(question)

    generated_sql = generate_sql(question)
    safe_sql = validate_sql(generated_sql)

    sql_corrected = False

    try:
        rows = execute_select_query(safe_sql)

    except QueryExecutionError as first_error:
        repaired_sql = repair_sql(
            question=question,
            failed_sql=safe_sql,
            database_error=first_error.database_message,
        )

        safe_sql = validate_sql(repaired_sql)
        sql_corrected = True

        try:
            rows = execute_select_query(safe_sql)

        except QueryExecutionError as second_error:
            raise QueryExecutionError(
                database_message=second_error.database_message,
                public_message=(
                    "Model nie zdołał wygenerować poprawnego "
                    "zapytania SQL po jednej próbie korekty."
                ),
            ) from second_error

    summary = generate_summary(
        question=question,
        sql_query=safe_sql,
        rows=rows,
    )

    return {
        "question": question,
        "provider": os.getenv(
            "AI_PROVIDER",
            "mock",
        ),
        "sql": safe_sql,
        "sql_corrected": sql_corrected,
        "summary": summary,
        "row_count": len(rows),
        "rows": rows,
    }