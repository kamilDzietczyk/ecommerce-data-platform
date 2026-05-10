from pathlib import Path
import pandas as pd


DATA_DIR = Path("data")


def load_csv_dataset(
    file_name: str,
    required_columns: list
) -> pd.DataFrame:

    """
    Load and validate CSV dataset.
    """

    file_path = DATA_DIR / file_name

    print(f"Loading dataset: {file_path}")

    if not file_path.exists():

        raise FileNotFoundError(
            f"Dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    print(f"Loaded {len(df)} records.")

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    print("Dataset validation passed.")

    return df