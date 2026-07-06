from ingestion.datasets.base_loader import load_csv_dataset


REQUIRED_COLUMNS = [
    "shipment_id",
    "order_id",
    "shipment_status",
    "shipment_provider",
    "shipped_date",
    "delivered_date"
]


def load_shipments():

    return load_csv_dataset(
        file_name="shipments.csv",
        required_columns=REQUIRED_COLUMNS
    )