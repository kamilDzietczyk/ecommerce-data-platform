import os
from typing import Any

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor


load_dotenv(override=False)


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(f"Missing required environment variable: {name}")

    return value


def get_connection():
    return psycopg2.connect(
        host=get_required_env("POSTGRES_HOST"),
        port=get_required_env("POSTGRES_PORT"),
        dbname=get_required_env("POSTGRES_DB"),
        user=get_required_env("AI_DB_USER"),
        password=get_required_env("AI_DB_PASSWORD"),
    )


def execute_select_query(query: str) -> list[dict[str, Any]]:
    connection = get_connection()

    try:
        connection.set_session(readonly=True)

        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    finally:
        connection.close()