import uuid
import pandas as pd
from datetime import datetime

from ingestion.db.connection import get_connection
from ingestion.db.insert_utils import batch_insert
from ingestion.db.table_utils import truncate_table

from ingestion.datasets.shipments_loader import load_shipments


SOURCE_SYSTEM = "generated_csv"


def run_pipeline():

    print("Starting shipments ingestion pipeline...")

    pipeline_run_id = str(uuid.uuid4())

    df = load_shipments()

    connection = get_connection()

    truncate_table(
        connection=connection,
        table_name="raw.shipments"
    )

    rows = []

    for _, row in df.iterrows():

        rows.append((
            int(row["shipment_id"]),
            int(row["order_id"]),
            row["shipment_status"],
            row["shipment_provider"],
            None if pd.isna(row["shipped_date"]) else row["shipped_date"],
            None if pd.isna(row["delivered_date"]) else row["delivered_date"],
            SOURCE_SYSTEM,
            datetime.utcnow(),
            pipeline_run_id
        ))

    columns = [
        "shipment_id",
        "order_id",
        "shipment_status",
        "shipment_provider",
        "shipped_date",
        "delivered_date",
        "source_system",
        "ingested_at",
        "pipeline_run_id"
    ]

    batch_insert(
        connection=connection,
        table_name="raw.shipments",
        columns=columns,
        rows=rows
    )

    connection.close()

    print("Shipments ingestion completed.")


if __name__ == "__main__":

    run_pipeline()