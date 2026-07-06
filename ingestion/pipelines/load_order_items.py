import uuid
from datetime import datetime

from ingestion.db.connection import get_connection
from ingestion.db.insert_utils import batch_insert
from ingestion.db.table_utils import truncate_table

from ingestion.datasets.order_items_loader import load_order_items


SOURCE_SYSTEM = "generated_csv"


def run_pipeline():

    print("Starting order items ingestion pipeline...")

    pipeline_run_id = str(uuid.uuid4())

    df = load_order_items()

    connection = get_connection()

    truncate_table(
        connection=connection,
        table_name="raw.order_items"
    )

    rows = []

    for _, row in df.iterrows():

        rows.append((
            int(row["order_item_id"]),
            int(row["order_id"]),
            int(row["product_id"]),
            int(row["quantity"]),
            float(row["unit_price"]),
            SOURCE_SYSTEM,
            datetime.utcnow(),
            pipeline_run_id
        ))

    columns = [
        "order_item_id",
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
        "source_system",
        "ingested_at",
        "pipeline_run_id"
    ]

    batch_insert(
        connection=connection,
        table_name="raw.order_items",
        columns=columns,
        rows=rows
    )

    connection.close()

    print("Order items ingestion completed.")


if __name__ == "__main__":

    run_pipeline()