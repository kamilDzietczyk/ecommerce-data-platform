import uuid
from datetime import datetime

from ingestion.db.connection import get_connection
from ingestion.db.insert_utils import batch_insert
from ingestion.db.table_utils import truncate_table

from ingestion.datasets.products_loader import load_products


SOURCE_SYSTEM = "generated_csv"


def run_pipeline():

    print("Starting products ingestion pipeline...")

    pipeline_run_id = str(uuid.uuid4())

    print(f"Pipeline run id: {pipeline_run_id}")

    df = load_products()

    connection = get_connection()

    truncate_table(
        connection=connection,
        table_name="raw.products"
    )

    rows = []

    for _, row in df.iterrows():

        rows.append((
            int(row["product_id"]),
            row["product_name"],
            row["category"],
            float(row["price"]),
            int(row["stock_quantity"]),
            row["created_at"],
            SOURCE_SYSTEM,
            datetime.utcnow(),
            pipeline_run_id
        ))

    columns = [
        "product_id",
        "product_name",
        "category",
        "price",
        "stock_quantity",
        "created_at",
        "source_system",
        "ingested_at",
        "pipeline_run_id"
    ]

    batch_insert(
        connection=connection,
        table_name="raw.products",
        columns=columns,
        rows=rows
    )

    connection.close()

    print("Products ingestion completed.")


if __name__ == "__main__":

    run_pipeline()