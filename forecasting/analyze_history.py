import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv


load_dotenv(override=False)


MONTHLY_SALES_QUERY = """
    SELECT
        sales_month,
        total_orders,
        total_revenue,
        average_order_value
    FROM marts.mart_monthly_sales
    WHERE is_complete_month = TRUE
    ORDER BY sales_month
"""


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(
            f"Missing required environment variable: {name}"
        )

    return value


def get_connection():
    """
    Forecast analysis currently uses the existing read-only AI user.
    The script only reads historical data and does not modify PostgreSQL.
    """
    return psycopg2.connect(
        host=get_required_env("POSTGRES_HOST"),
        port=get_required_env("POSTGRES_PORT"),
        dbname=get_required_env("POSTGRES_DB"),
        user=get_required_env("AI_DB_USER"),
        password=get_required_env("AI_DB_PASSWORD"),
    )


def load_monthly_sales() -> pd.DataFrame:
    connection = get_connection()

    try:
        dataframe = pd.read_sql_query(
            MONTHLY_SALES_QUERY,
            connection,
        )

    finally:
        connection.close()

    if dataframe.empty:
        raise RuntimeError(
            "No monthly sales data found in "
            "marts.mart_monthly_sales."
        )

    dataframe["sales_month"] = pd.to_datetime(
        dataframe["sales_month"]
    )

    dataframe["total_orders"] = pd.to_numeric(
        dataframe["total_orders"]
    )

    dataframe["total_revenue"] = pd.to_numeric(
        dataframe["total_revenue"]
    )

    dataframe["average_order_value"] = pd.to_numeric(
        dataframe["average_order_value"]
    )

    return dataframe


def find_missing_months(
    dataframe: pd.DataFrame,
) -> pd.DatetimeIndex:
    expected_months = pd.date_range(
        start=dataframe["sales_month"].min(),
        end=dataframe["sales_month"].max(),
        freq="MS",
    )

    actual_months = pd.DatetimeIndex(
        dataframe["sales_month"]
    )

    return expected_months.difference(actual_months)


def recommend_model(
    number_of_months: int,
    missing_months_count: int,
) -> str:
    if missing_months_count > 0:
        return (
            "History contains missing months. "
            "Resolve missing periods before model training."
        )

    if number_of_months < 12:
        return (
            "History is too short for a reliable yearly forecast. "
            "Use a simple baseline or generate more history."
        )

    if number_of_months < 24:
        return (
            "History supports a trend-based forecast, "
            "but yearly seasonality may be unreliable."
        )

    return (
        "History is long enough to test both trend-based "
        "and 12-month seasonal forecasting models."
    )


def print_history_report(
    dataframe: pd.DataFrame,
) -> None:
    missing_months = find_missing_months(dataframe)

    first_month = dataframe["sales_month"].min()
    last_month = dataframe["sales_month"].max()

    number_of_months = len(dataframe)

    print()
    print("Monthly sales history report")
    print("=" * 40)

    print(
        f"First month: "
        f"{first_month.strftime('%Y-%m')}"
    )

    print(
        f"Last month: "
        f"{last_month.strftime('%Y-%m')}"
    )

    print(f"Number of months: {number_of_months}")

    print(
        f"Missing months: "
        f"{len(missing_months)}"
    )

    print(
        f"Average monthly revenue: "
        f"{dataframe['total_revenue'].mean():,.2f}"
    )

    print(
        f"Minimum monthly revenue: "
        f"{dataframe['total_revenue'].min():,.2f}"
    )

    print(
        f"Maximum monthly revenue: "
        f"{dataframe['total_revenue'].max():,.2f}"
    )

    if len(missing_months) > 0:
        print()
        print("Missing periods:")

        for missing_month in missing_months:
            print(
                f"- {missing_month.strftime('%Y-%m')}"
            )

    print()
    print("Model recommendation:")
    print(
        recommend_model(
            number_of_months=number_of_months,
            missing_months_count=len(missing_months),
        )
    )


def main() -> None:
    dataframe = load_monthly_sales()

    print_history_report(dataframe)


if __name__ == "__main__":
    main()