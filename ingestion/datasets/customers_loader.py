from ingestion.datasets.base_loader import load_csv_dataset


REQUIRED_COLUMNS = [
    "customer_id",
    "first_name",
    "last_name",
    "email",
    "country",
    "city",
    "created_at"
]


def load_customers():

    return load_csv_dataset(
        file_name="customers.csv",
        required_columns=REQUIRED_COLUMNS
    )