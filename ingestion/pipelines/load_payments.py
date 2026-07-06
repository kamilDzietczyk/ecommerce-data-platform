import uuid
from datetime import datetime

from ingestion.db.connection import get_connection
from ingestion.db.insert_utils import batch_insert
from ingestion.db.table_utils import truncate_table

from ingestion.datasets.payments_loader import load_payments


SOURCE_SYSTEM = "generated_csv"


def run_pipeline():

    print("Starting payments ingestion pipeline...")

    pipeline_run_id = str(uuid.uuid4())

    df = load_payments()

    connection = get_connection()

    truncate_table(
        connection=connection,
        table_name="raw.payments"
    )

    rows = []

    for _, row in df.iterrows():

        rows.append((
            int(row["payment_id"]),
            int(row["order_id"]),
            row["payment_method"],
            row["payment_status"],
            row["payment_date"],
            float(row["payment_amount"]),
            SOURCE_SYSTEM,
            datetime.utcnow(),
            pipeline_run_id
        ))

    columns = [
        "payment_id",
        "order_id",
        "payment_method",
        "payment_status",
        "payment_date",
        "payment_amount",
        "source_system",
        "ingested_at",
        "pipeline_run_id"
    ]

    batch_insert(
        connection=connection,
        table_name="raw.payments",
        columns=columns,
        rows=rows
    )

    connection.close()

    print("Payments ingestion completed.")


if __name__ == "__main__":

    run_pipeline()