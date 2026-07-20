import os
from typing import Any

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor


load_dotenv(override=False)


class QueryExecutionError(RuntimeError):
    """Raised when PostgreSQL rejects AI-generated SQL."""

    def __init__(
        self,
        database_message: str,
        public_message: str = (
            "Wygenerowane zapytanie SQL nie mogło zostać wykonane."
        ),
    ):
        super().__init__(public_message)

        self.database_message = database_message
        self.public_message = public_message


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(
            f"Missing required environment variable: {name}"
        )

    return value


def get_connection():
    return psycopg2.connect(
        host=get_required_env("POSTGRES_HOST"),
        port=get_required_env("POSTGRES_PORT"),
        dbname=get_required_env("POSTGRES_DB"),
        user=get_required_env("AI_DB_USER"),
        password=get_required_env("AI_DB_PASSWORD"),
    )


def execute_select_query(
    query: str,
) -> list[dict[str, Any]]:
    maximum_rows = int(
        os.getenv("AI_MAX_RESULT_ROWS", "50")
    )

    timeout_ms = int(
        os.getenv("AI_QUERY_TIMEOUT_MS", "15000")
    )

    connection = get_connection()

    try:
        connection.set_session(
            readonly=True,
            autocommit=False,
        )

        limited_query = f"""
        SELECT *
        FROM (
            {query}
        ) AS ai_query_result
        LIMIT {maximum_rows}
        """

        with connection.cursor(
            cursor_factory=RealDictCursor
        ) as cursor:
            cursor.execute(
                """
                SELECT set_config(
                    'statement_timeout',
                    %s,
                    true
                )
                """,
                (str(timeout_ms),),
            )

            cursor.execute(limited_query)

            rows = cursor.fetchall()

            return [
                dict(row)
                for row in rows
            ]

    except psycopg2.Error as error:
        connection.rollback()

        database_message = (
            error.diag.message_primary
            if error.diag
            and error.diag.message_primary
            else str(error)
        )

        raise QueryExecutionError(
            database_message=database_message
        ) from error

    finally:
        connection.close()