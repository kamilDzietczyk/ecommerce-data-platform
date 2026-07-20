WITH daily_sales AS (

    SELECT
        sales_date,
        total_orders,
        total_revenue
    FROM {{ ref('mart_daily_sales') }}

),

final AS (

    SELECT
        DATE_TRUNC('month', sales_date)::DATE AS sales_month,

        SUM(total_orders)::BIGINT AS total_orders,

        SUM(total_revenue)::NUMERIC(14, 2) AS total_revenue,

        CASE
            WHEN SUM(total_orders) = 0 THEN 0
            ELSE (
                SUM(total_revenue) / SUM(total_orders)
            )::NUMERIC(14, 2)
        END AS average_order_value

    FROM daily_sales

    GROUP BY
        DATE_TRUNC('month', sales_date)::DATE

)

SELECT *
FROM final