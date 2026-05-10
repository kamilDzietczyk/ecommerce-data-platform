from ingestion.datasets.base_loader import load_csv_dataset


REQUIRED_COLUMNS = [
    "product_id",
    "product_name",
    "category",
    "price",
    "stock_quantity",
    "created_at"
]


def load_products():

    return load_csv_dataset(
        file_name="products.csv",
        required_columns=REQUIRED_COLUMNS
    )