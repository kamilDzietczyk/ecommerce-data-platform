WITH dates AS (

    SELECT
        generate_series(
            DATE '2024-01-01',
            DATE '2028-12-31',
            INTERVAL '1 day'
        )::DATE AS date_day

),

final AS (

    SELECT

        date_day,

        EXTRACT(YEAR FROM date_day)::INTEGER AS year,

        EXTRACT(MONTH FROM date_day)::INTEGER AS month,

        TO_CHAR(date_day, 'Month') AS month_name,

        EXTRACT(DAY FROM date_day)::INTEGER AS day,

        EXTRACT(QUARTER FROM date_day)::INTEGER AS quarter,

        EXTRACT(WEEK FROM date_day)::INTEGER AS week,

        CASE
            WHEN EXTRACT(ISODOW FROM date_day) IN (6,7)
                THEN TRUE
            ELSE FALSE
        END AS is_weekend

    FROM dates

)

SELECT *
FROM final