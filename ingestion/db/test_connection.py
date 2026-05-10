from ingestion.db.connection import get_connection


def test_connection():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("SELECT version();")

    version = cursor.fetchone()

    print("PostgreSQL version:")
    print(version)

    cursor.close()
    connection.close()

    print("Connection closed.")


if __name__ == "__main__":

    test_connection()