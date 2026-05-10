from ingestion.datasets.base_loader import load_csv_dataset


REQUIRED_COLUMNS = [
    "order_id",
    "customer_id",
    "order_date",
    "order_status",
    "total_amount"
]


def load_orders():

    return load_csv_dataset(
        file_name="orders.csv",
        required_columns=REQUIRED_COLUMNS
    )