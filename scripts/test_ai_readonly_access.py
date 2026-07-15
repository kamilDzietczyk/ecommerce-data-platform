import os

import psycopg2
from dotenv import load_dotenv


load_dotenv(override=False)


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(f"Missing required environment variable: {name}")

    return value


def main():

    postgres_host = get_required_env("POSTGRES_HOST")
    postgres_port = get_required_env("POSTGRES_PORT")
    postgres_db = get_required_env("POSTGRES_DB")

    ai_db_user = get_required_env("AI_DB_USER")
    ai_db_password = get_required_env("AI_DB_PASSWORD")

    print("Connecting as AI read-only user...")

    connection = psycopg2.connect(
        host=postgres_host,
        port=postgres_port,
        dbname=postgres_db,
        user=ai_db_user,
        password=ai_db_password
    )

    cursor = connection.cursor()

    print("Testing allowed access to marts...")

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM marts.mart_daily_sales
        """
    )

    result = cursor.fetchone()

    print(f"marts access OK. mart_daily_sales rows: {result[0]}")

    print("Testing blocked access to raw...")

    try:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM raw.customers
            """
        )

        raise RuntimeError("Security check failed. AI user can access raw.customers.")

    except psycopg2.Error:
        connection.rollback()
        print("raw access blocked correctly.")

    print("Testing blocked write operation...")

    try:
        cursor.execute(
            """
            DELETE FROM marts.mart_daily_sales
            """
        )

        raise RuntimeError("Security check failed. AI user can execute DELETE.")

    except psycopg2.Error:
        connection.rollback()
        print("write operation blocked correctly.")

    cursor.close()
    connection.close()

    print("AI read-only access validation completed successfully.")


if __name__ == "__main__":
    main()