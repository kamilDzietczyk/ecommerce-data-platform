import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.engine.base import Engine


load_dotenv(override=False)


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise ValueError(
            f"Missing required environment variable: {name}"
        )

    return value


def create_forecast_engine() -> Engine:
    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=get_required_env("POSTGRES_USER"),
        password=get_required_env("POSTGRES_PASSWORD"),
        host=get_required_env("POSTGRES_HOST"),
        port=int(get_required_env("POSTGRES_PORT")),
        database=get_required_env("POSTGRES_DB"),
    )

    return create_engine(
        database_url,
        pool_pre_ping=True,
    )


def create_forecast_schema_and_table(
    connection,
) -> None:

    connection.execute(
        text(
            """
            CREATE SCHEMA IF NOT EXISTS forecast
            """
        )
    )

    connection.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS forecast.sales_forecast (
                forecast_id BIGSERIAL PRIMARY KEY,

                forecast_month DATE NOT NULL,

                predicted_revenue NUMERIC(18, 2) NOT NULL
                    CHECK (predicted_revenue >= 0),

                model_name VARCHAR(100) NOT NULL,

                trained_at_utc TIMESTAMPTZ NOT NULL,

                history_start_month DATE NOT NULL,
                history_end_month DATE NOT NULL,

                history_months INTEGER NOT NULL
                    CHECK (history_months > 0),

                created_at TIMESTAMPTZ
                    NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                CONSTRAINT uq_sales_forecast_run_month
                    UNIQUE (
                        trained_at_utc,
                        forecast_month
                    )
            )
            """
        )
    )

    connection.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS
                idx_sales_forecast_run
            ON forecast.sales_forecast (
                trained_at_utc DESC,
                forecast_month
            )
            """
        )
    )


def prepare_forecast_records(
    forecast_dataframe: pd.DataFrame,
) -> list[dict]:

    required_columns = {
        "forecast_month",
        "predicted_revenue",
        "model_name",
        "trained_at_utc",
        "history_start_month",
        "history_end_month",
        "history_months",
    }

    missing_columns = (
        required_columns
        - set(forecast_dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            "Forecast dataframe is missing columns: "
            f"{sorted(missing_columns)}"
        )

    dataframe = forecast_dataframe.copy()

    dataframe["forecast_month"] = pd.to_datetime(
        dataframe["forecast_month"]
    )

    dataframe["trained_at_utc"] = pd.to_datetime(
        dataframe["trained_at_utc"],
        utc=True,
    )

    dataframe["history_start_month"] = pd.to_datetime(
        dataframe["history_start_month"]
    )

    dataframe["history_end_month"] = pd.to_datetime(
        dataframe["history_end_month"]
    )

    records = []

    for row in dataframe.itertuples(
        index=False
    ):
        records.append(
            {
                "forecast_month": (
                    row.forecast_month.date()
                ),
                "predicted_revenue": float(
                    row.predicted_revenue
                ),
                "model_name": row.model_name,
                "trained_at_utc": (
                    row.trained_at_utc.to_pydatetime()
                ),
                "history_start_month": (
                    row.history_start_month.date()
                ),
                "history_end_month": (
                    row.history_end_month.date()
                ),
                "history_months": int(
                    row.history_months
                ),
            }
        )

    return records


def save_forecast_to_database(
    forecast_dataframe: pd.DataFrame,
) -> int:

    records = prepare_forecast_records(
        forecast_dataframe
    )

    if not records:
        raise ValueError(
            "Forecast dataframe contains no rows."
        )

    engine = create_forecast_engine()

    insert_query = text(
        """
        INSERT INTO forecast.sales_forecast (
            forecast_month,
            predicted_revenue,
            model_name,
            trained_at_utc,
            history_start_month,
            history_end_month,
            history_months
        )
        VALUES (
            :forecast_month,
            :predicted_revenue,
            :model_name,
            :trained_at_utc,
            :history_start_month,
            :history_end_month,
            :history_months
        )
        ON CONFLICT (
            trained_at_utc,
            forecast_month
        )
        DO UPDATE SET
            predicted_revenue =
                EXCLUDED.predicted_revenue,
            model_name =
                EXCLUDED.model_name,
            history_start_month =
                EXCLUDED.history_start_month,
            history_end_month =
                EXCLUDED.history_end_month,
            history_months =
                EXCLUDED.history_months
        """
    )

    try:
        with engine.begin() as connection:

            create_forecast_schema_and_table(
                connection
            )

            connection.execute(
                insert_query,
                records,
            )

    finally:
        engine.dispose()

    return len(records)