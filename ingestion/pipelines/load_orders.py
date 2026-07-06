import uuid
from datetime import datetime

from ingestion.db.connection import get_connection
from ingestion.db.insert_utils import batch_insert
from ingestion.db.table_utils import truncate_table

from ingestion.datasets.orders_loader import load_orders


SOURCE_SYSTEM = "generated_csv"


def run_pipeline():

    print("Starting orders ingestion pipeline...")

    pipeline_run_id = str(uuid.uuid4())

    print(f"Pipeline run id: {pipeline_run_id}")

    df = load_orders()

    connection = get_connection()

    truncate_table(
        connection=connection,
        table_name="raw.orders"
    )

    rows = []

    for _, row in df.iterrows():

        rows.append((
            int(row["order_id"]),
            int(row["customer_id"]),
            row["order_date"],
            row["order_status"],
            float(row["total_amount"]),
            SOURCE_SYSTEM,
            datetime.utcnow(),
            pipeline_run_id
        ))

    columns = [
        "order_id",
        "customer_id",
        "order_date",
        "order_status",
        "total_amount",
        "source_system",
        "ingested_at",
        "pipeline_run_id"
    ]

    batch_insert(
        connection=connection,
        table_name="raw.orders",
        columns=columns,
        rows=rows
    )

    connection.close()

    print("Orders ingestion completed.")


if __name__ == "__main__":

    run_pipeline()