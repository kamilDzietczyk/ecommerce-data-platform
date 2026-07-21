from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import (
    ExponentialSmoothing,
    Holt,
)

from forecasting.data import load_monthly_sales


HOLDOUT_MONTHS = 12
FORECAST_HORIZON_MONTHS = 12
SEASONAL_PERIODS = 12
MINIMUM_HISTORY_MONTHS = 36

OUTPUT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    / "output"
)


ForecastFunction = Callable[
    [pd.Series, int],
    np.ndarray,
]


def prepare_revenue_series(
    dataframe: pd.DataFrame,
) -> pd.Series:
    series = (
        dataframe
        .set_index("sales_month")[
            "total_revenue"
        ]
        .astype(float)
        .sort_index()
    )

    series.index = pd.DatetimeIndex(
        series.index
    )

    expected_index = pd.date_range(
        start=series.index.min(),
        end=series.index.max(),
        freq="MS",
    )

    series = series.reindex(
        expected_index
    )

    if series.isna().any():
        missing_months = (
            series[
                series.isna()
            ]
            .index
            .strftime("%Y-%m")
            .tolist()
        )

        raise RuntimeError(
            "Revenue history contains missing months: "
            f"{missing_months}"
        )

    if len(series) < MINIMUM_HISTORY_MONTHS:
        raise RuntimeError(
            "At least 36 complete months are required. "
            f"Available months: {len(series)}."
        )

    if (series <= 0).any():
        invalid_months = (
            series[
                series <= 0
            ]
            .index
            .strftime("%Y-%m")
            .tolist()
        )

        raise RuntimeError(
            "Revenue must be positive for every month. "
            f"Invalid months: {invalid_months}"
        )

    series.index.name = "sales_month"
    series.name = "total_revenue"

    return series


def seasonal_naive_forecast(
    training_series: pd.Series,
    horizon: int,
) -> np.ndarray:
    if len(training_series) < SEASONAL_PERIODS:
        raise ValueError(
            "Seasonal naive forecast requires "
            "at least 12 months."
        )

    seasonal_pattern = (
        training_series
        .iloc[-SEASONAL_PERIODS:]
        .to_numpy(dtype=float)
    )

    return np.resize(
        seasonal_pattern,
        horizon,
    )


def holt_damped_forecast(
    training_series: pd.Series,
    horizon: int,
) -> np.ndarray:
    fitted_model = Holt(
        training_series,
        damped_trend=True,
        initialization_method="estimated",
    ).fit(
        optimized=True,
    )

    return np.asarray(
        fitted_model.forecast(horizon),
        dtype=float,
    )


def holt_winters_additive_forecast(
    training_series: pd.Series,
    horizon: int,
) -> np.ndarray:
    fitted_model = ExponentialSmoothing(
        training_series,
        trend="add",
        damped_trend=True,
        seasonal="add",
        seasonal_periods=SEASONAL_PERIODS,
        initialization_method="estimated",
    ).fit(
        optimized=True,
        remove_bias=False,
    )

    return np.asarray(
        fitted_model.forecast(horizon),
        dtype=float,
    )


MODEL_FUNCTIONS: dict[
    str,
    ForecastFunction,
] = {
    "seasonal_naive_12": (
        seasonal_naive_forecast
    ),
    "holt_damped_trend": (
        holt_damped_forecast
    ),
    "holt_winters_additive": (
        holt_winters_additive_forecast
    ),
}


def calculate_mae(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> float:
    return float(
        np.mean(
            np.abs(
                actual - predicted
            )
        )
    )


def calculate_mape_percent(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> float:
    if np.any(actual == 0):
        raise ValueError(
            "MAPE cannot be calculated when "
            "actual values contain zero."
        )

    return float(
        np.mean(
            np.abs(
                (
                    actual
                    - predicted
                )
                / actual
            )
        )
        * 100
    )


def evaluate_models(
    training_series: pd.Series,
    test_series: pd.Series,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    actual_values = test_series.to_numpy(
        dtype=float
    )

    metrics = []

    predictions_dataframe = pd.DataFrame(
        {
            "sales_month": test_series.index,
            "actual_revenue": actual_values,
        }
    )

    model_errors = []

    for (
        model_name,
        forecast_function,
    ) in MODEL_FUNCTIONS.items():

        try:
            predicted_values = (
                forecast_function(
                    training_series,
                    len(test_series),
                )
            )

        except Exception as error:
            model_errors.append(
                {
                    "model_name": model_name,
                    "error": str(error),
                }
            )

            print(
                f"WARNING: model {model_name} "
                f"could not be evaluated: {error}"
            )

            continue

        if len(predicted_values) != len(
            actual_values
        ):
            raise RuntimeError(
                f"Model {model_name} returned "
                "an invalid forecast length."
            )

        mae = calculate_mae(
            actual=actual_values,
            predicted=predicted_values,
        )

        mape_percent = (
            calculate_mape_percent(
                actual=actual_values,
                predicted=predicted_values,
            )
        )

        metrics.append(
            {
                "model_name": model_name,
                "mae": mae,
                "mape_percent": mape_percent,
                "training_months": len(
                    training_series
                ),
                "test_months": len(
                    test_series
                ),
            }
        )

        predictions_dataframe[
            model_name
        ] = predicted_values

    if not metrics:
        raise RuntimeError(
            "None of the forecasting models "
            f"could be evaluated: {model_errors}"
        )

    metrics_dataframe = (
        pd.DataFrame(metrics)
        .sort_values(
            by=[
                "mape_percent",
                "mae",
            ],
            ascending=True,
        )
        .reset_index(drop=True)
    )

    return (
        metrics_dataframe,
        predictions_dataframe,
    )


def train_selected_model(
    model_name: str,
    full_series: pd.Series,
    horizon: int,
) -> np.ndarray:
    forecast_function = MODEL_FUNCTIONS.get(
        model_name
    )

    if forecast_function is None:
        raise ValueError(
            f"Unsupported model: {model_name}"
        )

    forecast_values = forecast_function(
        full_series,
        horizon,
    )

    if len(forecast_values) != horizon:
        raise RuntimeError(
            "Selected model returned an invalid "
            "forecast length."
        )

    if np.any(
        ~np.isfinite(forecast_values)
    ):
        raise RuntimeError(
            "Selected model returned non-finite "
            "forecast values."
        )

    if np.any(forecast_values < 0):
        raise RuntimeError(
            "Selected model returned negative revenue."
        )

    return forecast_values


def build_forecast_dataframe(
    full_series: pd.Series,
    forecast_values: np.ndarray,
    model_name: str,
) -> pd.DataFrame:
    first_forecast_month = (
        full_series.index.max()
        + pd.offsets.MonthBegin(1)
    )

    forecast_months = pd.date_range(
        start=first_forecast_month,
        periods=len(forecast_values),
        freq="MS",
    )

    trained_at = datetime.now(
        timezone.utc
    ).isoformat()

    return pd.DataFrame(
        {
            "forecast_month": forecast_months,
            "predicted_revenue": np.round(
                forecast_values,
                2,
            ),
            "model_name": model_name,
            "trained_at_utc": trained_at,
            "history_start_month": (
                full_series.index.min()
            ),
            "history_end_month": (
                full_series.index.max()
            ),
            "history_months": len(
                full_series
            ),
        }
    )


def save_results(
    metrics_dataframe: pd.DataFrame,
    predictions_dataframe: pd.DataFrame,
    forecast_dataframe: pd.DataFrame,
) -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics_dataframe.to_csv(
        OUTPUT_DIR / "model_metrics.csv",
        index=False,
    )

    predictions_dataframe.to_csv(
        OUTPUT_DIR
        / "holdout_predictions.csv",
        index=False,
    )

    forecast_dataframe.to_csv(
        OUTPUT_DIR
        / "sales_forecast.csv",
        index=False,
    )


def print_report(
    full_series: pd.Series,
    training_series: pd.Series,
    test_series: pd.Series,
    metrics_dataframe: pd.DataFrame,
    forecast_dataframe: pd.DataFrame,
) -> None:
    print()
    print("Sales forecasting report")
    print("=" * 70)

    print(
        "Full history: "
        f"{full_series.index.min():%Y-%m} "
        f"to {full_series.index.max():%Y-%m}"
    )

    print(
        f"History months: {len(full_series)}"
    )

    print(
        "Training period: "
        f"{training_series.index.min():%Y-%m} "
        f"to {training_series.index.max():%Y-%m}"
    )

    print(
        "Holdout period: "
        f"{test_series.index.min():%Y-%m} "
        f"to {test_series.index.max():%Y-%m}"
    )

    print()
    print("Model comparison")
    print("-" * 70)

    printable_metrics = (
        metrics_dataframe.copy()
    )

    printable_metrics["mae"] = (
        printable_metrics["mae"]
        .map(
            lambda value: f"{value:,.2f}"
        )
    )

    printable_metrics[
        "mape_percent"
    ] = (
        printable_metrics[
            "mape_percent"
        ]
        .map(
            lambda value: f"{value:.2f}%"
        )
    )

    print(
        printable_metrics.to_string(
            index=False
        )
    )

    selected_model = metrics_dataframe.iloc[
        0
    ]["model_name"]

    print()
    print(
        f"Selected model: {selected_model}"
    )

    print()
    print("12-month revenue forecast")
    print("-" * 70)

    printable_forecast = (
        forecast_dataframe[
            [
                "forecast_month",
                "predicted_revenue",
            ]
        ]
        .copy()
    )

    printable_forecast[
        "forecast_month"
    ] = (
        printable_forecast[
            "forecast_month"
        ]
        .dt.strftime("%Y-%m")
    )

    printable_forecast[
        "predicted_revenue"
    ] = (
        printable_forecast[
            "predicted_revenue"
        ]
        .map(
            lambda value: f"{value:,.2f}"
        )
    )

    print(
        printable_forecast.to_string(
            index=False
        )
    )

    print()
    print("Files saved:")

    print(
        f"- {OUTPUT_DIR / 'model_metrics.csv'}"
    )

    print(
        f"- {OUTPUT_DIR / 'holdout_predictions.csv'}"
    )

    print(
        f"- {OUTPUT_DIR / 'sales_forecast.csv'}"
    )


def main() -> None:
    monthly_sales_dataframe = (
        load_monthly_sales()
    )

    full_series = prepare_revenue_series(
        monthly_sales_dataframe
    )

    training_series = full_series.iloc[
        :-HOLDOUT_MONTHS
    ]

    test_series = full_series.iloc[
        -HOLDOUT_MONTHS:
    ]

    (
        metrics_dataframe,
        predictions_dataframe,
    ) = evaluate_models(
        training_series=training_series,
        test_series=test_series,
    )

    selected_model = metrics_dataframe.iloc[
        0
    ]["model_name"]

    forecast_values = train_selected_model(
        model_name=selected_model,
        full_series=full_series,
        horizon=FORECAST_HORIZON_MONTHS,
    )

    forecast_dataframe = (
        build_forecast_dataframe(
            full_series=full_series,
            forecast_values=forecast_values,
            model_name=selected_model,
        )
    )

    save_results(
        metrics_dataframe=metrics_dataframe,
        predictions_dataframe=(
            predictions_dataframe
        ),
        forecast_dataframe=forecast_dataframe,
    )

    print_report(
        full_series=full_series,
        training_series=training_series,
        test_series=test_series,
        metrics_dataframe=metrics_dataframe,
        forecast_dataframe=forecast_dataframe,
    )


if __name__ == "__main__":
    main()