from ingestion.datasets.base_loader import load_csv_dataset


REQUIRED_COLUMNS = [
    "order_item_id",
    "order_id",
    "product_id",
    "quantity",
    "unit_price"
]


def load_order_items():

    return load_csv_dataset(
        file_name="order_items.csv",
        required_columns=REQUIRED_COLUMNS
    )