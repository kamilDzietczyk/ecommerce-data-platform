import os
from typing import Any

from ai_assistant.app.db import execute_select_query
from ai_assistant.app.sql_generator import generate_sql
from ai_assistant.app.sql_guard import validate_sql
from ai_assistant.app.summary_generator import generate_summary


def answer_question(question: str) -> dict[str, Any]:
    generated_sql = generate_sql(question)

    safe_sql = validate_sql(generated_sql)

    rows = execute_select_query(safe_sql)

    summary = generate_summary(
        question=question,
        sql_query=safe_sql,
        rows=rows,
    )

    return {
        "question": question,
        "provider": os.getenv("AI_PROVIDER", "mock"),
        "sql": safe_sql,
        "summary": summary,
        "row_count": len(rows),
        "rows": rows,
    }