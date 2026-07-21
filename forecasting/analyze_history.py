import pandas as pd

from forecasting.data import load_monthly_sales


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
            "History is too short for a reliable forecast."
        )

    if number_of_months < 24:
        return (
            "History supports a trend-based forecast, "
            "but yearly seasonality may be unreliable."
        )

    if number_of_months < 36:
        return (
            "Yearly seasonality can be tested, but there is "
            "limited history for a 12-month holdout."
        )

    return (
        "History is long enough to compare trend-based "
        "and 12-month seasonal forecasting models."
    )


def print_history_report(
    dataframe: pd.DataFrame,
) -> None:
    missing_months = find_missing_months(
        dataframe
    )

    first_month = dataframe[
        "sales_month"
    ].min()

    last_month = dataframe[
        "sales_month"
    ].max()

    number_of_months = len(dataframe)

    print()
    print("Monthly sales history report")
    print("=" * 40)

    print(
        "First month: "
        f"{first_month.strftime('%Y-%m')}"
    )

    print(
        "Last month: "
        f"{last_month.strftime('%Y-%m')}"
    )

    print(
        f"Number of months: {number_of_months}"
    )

    print(
        f"Missing months: {len(missing_months)}"
    )

    print(
        "Average monthly revenue: "
        f"{dataframe['total_revenue'].mean():,.2f}"
    )

    print(
        "Minimum monthly revenue: "
        f"{dataframe['total_revenue'].min():,.2f}"
    )

    print(
        "Maximum monthly revenue: "
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
            missing_months_count=len(
                missing_months
            ),
        )
    )


def main() -> None:
    dataframe = load_monthly_sales()

    print_history_report(dataframe)


if __name__ == "__main__":
    main()