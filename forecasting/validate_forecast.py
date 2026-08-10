from pathlib import Path

import numpy as np
import pandas as pd

from forecasting.data import load_monthly_sales
from forecasting.train_forecast import (
    MODEL_FUNCTIONS,
    calculate_mae,
    calculate_mape_percent,
    prepare_revenue_series,
)


INITIAL_TRAINING_MONTHS = 24
VALIDATION_HORIZON_MONTHS = 3

OUTPUT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    / "output"
)


def run_rolling_validation(
    full_series: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame]:

    predictions = []

    fold_number = 1

    training_end = INITIAL_TRAINING_MONTHS

    while training_end < len(full_series):

        test_end = min(
            training_end + VALIDATION_HORIZON_MONTHS,
            len(full_series),
        )

        training_series = full_series.iloc[
            :training_end
        ]

        test_series = full_series.iloc[
            training_end:test_end
        ]

        if test_series.empty:
            break

        print()
        print(
            f"Fold {fold_number}: "
            f"train {training_series.index.min():%Y-%m} "
            f"→ {training_series.index.max():%Y-%m}, "
            f"test {test_series.index.min():%Y-%m} "
            f"→ {test_series.index.max():%Y-%m}"
        )

        for model_name, forecast_function in MODEL_FUNCTIONS.items():

            try:
                predicted_values = forecast_function(
                    training_series,
                    len(test_series),
                )

            except Exception as error:
                print(
                    f"WARNING: {model_name} failed: "
                    f"{error}"
                )
                continue

            for month, actual, predicted in zip(
                test_series.index,
                test_series.to_numpy(dtype=float),
                predicted_values,
            ):
                predictions.append(
                    {
                        "fold": fold_number,
                        "model_name": model_name,
                        "sales_month": month,
                        "actual_revenue": actual,
                        "predicted_revenue": predicted,
                        "absolute_error": abs(
                            actual - predicted
                        ),
                        "percentage_error": (
                            abs(actual - predicted)
                            / actual
                            * 100
                        ),
                    }
                )

        training_end = test_end
        fold_number += 1

    predictions_dataframe = pd.DataFrame(
        predictions
    )

    if predictions_dataframe.empty:
        raise RuntimeError(
            "Rolling validation produced no results."
        )

    metrics = []

    for model_name in predictions_dataframe[
        "model_name"
    ].unique():

        model_results = predictions_dataframe[
            predictions_dataframe["model_name"]
            == model_name
        ]

        actual = model_results[
            "actual_revenue"
        ].to_numpy(dtype=float)

        predicted = model_results[
            "predicted_revenue"
        ].to_numpy(dtype=float)

        metrics.append(
            {
                "model_name": model_name,
                "mae": calculate_mae(
                    actual,
                    predicted,
                ),
                "mape_percent": calculate_mape_percent(
                    actual,
                    predicted,
                ),
                "validation_months": len(
                    model_results
                ),
                "folds": model_results[
                    "fold"
                ].nunique(),
            }
        )

    metrics_dataframe = (
        pd.DataFrame(metrics)
        .sort_values(
            by=[
                "mape_percent",
                "mae",
            ]
        )
        .reset_index(drop=True)
    )

    return (
        metrics_dataframe,
        predictions_dataframe,
    )


def save_results(
    metrics_dataframe: pd.DataFrame,
    predictions_dataframe: pd.DataFrame,
) -> None:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics_dataframe.to_csv(
        OUTPUT_DIR
        / "rolling_validation_metrics.csv",
        index=False,
    )

    predictions_dataframe.to_csv(
        OUTPUT_DIR
        / "rolling_validation_predictions.csv",
        index=False,
    )


def print_report(
    metrics_dataframe: pd.DataFrame,
) -> None:

    print()
    print("Rolling forecast validation")
    print("=" * 70)

    printable = metrics_dataframe.copy()

    printable["mae"] = printable[
        "mae"
    ].map(
        lambda value: f"{value:,.2f}"
    )

    printable["mape_percent"] = printable[
        "mape_percent"
    ].map(
        lambda value: f"{value:.2f}%"
    )

    print(
        printable.to_string(
            index=False
        )
    )

    best_model = metrics_dataframe.iloc[
        0
    ]["model_name"]

    print()
    print(
        f"Best rolling-validation model: "
        f"{best_model}"
    )


def main() -> None:

    monthly_sales = load_monthly_sales()

    full_series = prepare_revenue_series(
        monthly_sales
    )

    (
        metrics_dataframe,
        predictions_dataframe,
    ) = run_rolling_validation(
        full_series
    )

    save_results(
        metrics_dataframe,
        predictions_dataframe,
    )

    print_report(
        metrics_dataframe
    )


if __name__ == "__main__":
    main()