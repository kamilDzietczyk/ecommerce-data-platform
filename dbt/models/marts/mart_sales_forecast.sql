WITH source_forecasts AS (

    SELECT
        forecast_month,
        predicted_revenue,
        model_name,
        trained_at_utc,
        history_start_month,
        history_end_month,
        history_months
    FROM {{ source('forecast', 'sales_forecast') }}

),

latest_run AS (

    SELECT
        MAX(trained_at_utc) AS trained_at_utc
    FROM source_forecasts

),

final AS (

    SELECT
        forecast.forecast_month,
        forecast.predicted_revenue,
        forecast.model_name,
        forecast.trained_at_utc,
        forecast.history_start_month,
        forecast.history_end_month,
        forecast.history_months

    FROM source_forecasts AS forecast

    INNER JOIN latest_run AS latest
        ON forecast.trained_at_utc =
           latest.trained_at_utc

)

SELECT *
FROM final