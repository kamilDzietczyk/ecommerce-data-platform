import uuid
from datetime import datetime

from ingestion.db.connection import get_connection
from ingestion.db.insert_utils import batch_insert
from ingestion.db.table_utils import truncate_table

from ingestion.datasets.customers_loader import load_customers


SOURCE_SYSTEM = "generated_csv"


def run_pipeline():

    print("Starting customers ingestion pipeline...")

    pipeline_run_id = str(uuid.uuid4())

    print(f"Pipeline run id: {pipeline_run_id}")

    df = load_customers()

    connection = get_connection()

    truncate_table(
        connection=connection,
        table_name="raw.customers"
    )

    rows = []

    for _, row in df.iterrows():

        rows.append((
            int(row["customer_id"]),
            row["first_name"],
            row["last_name"],
            row["email"],
            row["country"],
            row["city"],
            row["created_at"],
            SOURCE_SYSTEM,
            datetime.utcnow(),
            pipeline_run_id
        ))

    columns = [
        "customer_id",
        "first_name",
        "last_name",
        "email",
        "country",
        "city",
        "created_at",
        "source_system",
        "ingested_at",
        "pipeline_run_id"
    ]

    batch_insert(
        connection=connection,
        table_name="raw.customers",
        columns=columns,
        rows=rows
    )

    connection.close()

    print("Customers ingestion completed.")


if __name__ == "__main__":

    run_pipeline()