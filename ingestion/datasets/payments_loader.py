from ingestion.datasets.base_loader import load_csv_dataset


REQUIRED_COLUMNS = [
    "payment_id",
    "order_id",
    "payment_method",
    "payment_status",
    "payment_date",
    "payment_amount"
]


def load_payments():

    return load_csv_dataset(
        file_name="payments.csv",
        required_columns=REQUIRED_COLUMNS
    )