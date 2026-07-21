import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.engine.base import Engine


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


def create_database_engine() -> Engine:
    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=get_required_env("AI_DB_USER"),
        password=get_required_env("AI_DB_PASSWORD"),
        host=get_required_env("POSTGRES_HOST"),
        port=int(get_required_env("POSTGRES_PORT")),
        database=get_required_env("POSTGRES_DB"),
    )

    return create_engine(
        database_url,
        pool_pre_ping=True,
    )


def load_monthly_sales() -> pd.DataFrame:
    engine = create_database_engine()

    try:
        with engine.connect() as connection:
            dataframe = pd.read_sql_query(
                text(MONTHLY_SALES_QUERY),
                connection,
            )

    finally:
        engine.dispose()

    if dataframe.empty:
        raise RuntimeError(
            "No complete monthly sales data found in "
            "marts.mart_monthly_sales."
        )

    expected_columns = {
        "sales_month",
        "total_orders",
        "total_revenue",
        "average_order_value",
    }

    missing_columns = (
        expected_columns
        - set(dataframe.columns)
    )

    if missing_columns:
        raise RuntimeError(
            "Monthly sales data is missing columns: "
            f"{sorted(missing_columns)}"
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

    dataframe = (
        dataframe
        .sort_values("sales_month")
        .reset_index(drop=True)
    )

    duplicated_months = dataframe.loc[
        dataframe["sales_month"].duplicated(),
        "sales_month",
    ]

    if not duplicated_months.empty:
        raise RuntimeError(
            "Monthly sales contains duplicated months: "
            f"{duplicated_months.dt.strftime('%Y-%m').tolist()}"
        )

    return dataframe