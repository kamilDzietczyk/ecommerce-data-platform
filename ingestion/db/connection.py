import os
import psycopg2

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_connection():

    """
    Create PostgreSQL database connection.
    """

    try:

        connection = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD")
        )

        print("PostgreSQL connection established.")

        return connection

    except Exception as error:

        print(f"Database connection failed: {error}")

        raise