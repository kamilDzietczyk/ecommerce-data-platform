import os

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql


load_dotenv(override=False)


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(f"Missing required environment variable: {name}")

    return value


def schema_exists(cursor, schema_name: str) -> bool:
    cursor.execute(
        """
        SELECT 1
        FROM information_schema.schemata
        WHERE schema_name = %s
        """,
        (schema_name,)
    )

    return cursor.fetchone() is not None


def main():

    postgres_host = get_required_env("POSTGRES_HOST")
    postgres_port = get_required_env("POSTGRES_PORT")
    postgres_db = get_required_env("POSTGRES_DB")
    postgres_user = get_required_env("POSTGRES_USER")
    postgres_password = get_required_env("POSTGRES_PASSWORD")

    ai_db_user = get_required_env("AI_DB_USER")
    ai_db_password = get_required_env("AI_DB_PASSWORD")

    print("Connecting to PostgreSQL as admin user...")

    connection = psycopg2.connect(
        host=postgres_host,
        port=postgres_port,
        dbname=postgres_db,
        user=postgres_user,
        password=postgres_password
    )

    connection.autocommit = True

    cursor = connection.cursor()

    if not schema_exists(cursor, "marts"):
        raise RuntimeError("Schema 'marts' does not exist. Run dbt models first.")

    print(f"Creating or updating AI read-only user: {ai_db_user}")

    cursor.execute(
        """
        SELECT 1
        FROM pg_roles
        WHERE rolname = %s
        """,
        (ai_db_user,)
    )

    role_exists = cursor.fetchone() is not None

    if role_exists:
        cursor.execute(
            sql.SQL("ALTER ROLE {} WITH LOGIN PASSWORD %s").format(
                sql.Identifier(ai_db_user)
            ),
            (ai_db_password,)
        )

        print("AI user already exists. Password updated.")

    else:
        cursor.execute(
            sql.SQL("CREATE ROLE {} WITH LOGIN PASSWORD %s").format(
                sql.Identifier(ai_db_user)
            ),
            (ai_db_password,)
        )

        print("AI user created.")

    cursor.execute(
        sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
            sql.Identifier(postgres_db),
            sql.Identifier(ai_db_user)
        )
    )

    cursor.execute(
        sql.SQL("GRANT USAGE ON SCHEMA marts TO {}").format(
            sql.Identifier(ai_db_user)
        )
    )

    cursor.execute(
        sql.SQL("GRANT SELECT ON ALL TABLES IN SCHEMA marts TO {}").format(
            sql.Identifier(ai_db_user)
        )
    )

    cursor.execute(
        sql.SQL(
            "ALTER DEFAULT PRIVILEGES FOR ROLE {} IN SCHEMA marts "
            "GRANT SELECT ON TABLES TO {}"
        ).format(
            sql.Identifier(postgres_user),
            sql.Identifier(ai_db_user)
        )
    )

    for restricted_schema in ["raw", "staging"]:
        if schema_exists(cursor, restricted_schema):
            cursor.execute(
                sql.SQL("REVOKE ALL ON SCHEMA {} FROM {}").format(
                    sql.Identifier(restricted_schema),
                    sql.Identifier(ai_db_user)
                )
            )

            cursor.execute(
                sql.SQL("REVOKE ALL ON ALL TABLES IN SCHEMA {} FROM {}").format(
                    sql.Identifier(restricted_schema),
                    sql.Identifier(ai_db_user)
                )
            )

    cursor.close()
    connection.close()

    print("AI read-only database user configured successfully.")
    print("Allowed access: marts schema only.")


if __name__ == "__main__":
    main()