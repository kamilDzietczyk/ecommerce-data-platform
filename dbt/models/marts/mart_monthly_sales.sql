WITH daily_sales AS (

    SELECT
        sales_date,
        total_orders,
        total_revenue
    FROM {{ ref('mart_daily_sales') }}

),

monthly_sales AS (

    SELECT
        DATE_TRUNC('month', sales_date)::DATE AS sales_month,

        MIN(sales_date) AS first_sales_date,
        MAX(sales_date) AS last_sales_date,
        COUNT(DISTINCT sales_date) AS number_of_days,

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

),

final AS (

    SELECT
        sales_month,
        first_sales_date,
        last_sales_date,
        number_of_days,
        total_orders,
        total_revenue,
        average_order_value,

        (
            first_sales_date = sales_month
            AND last_sales_date = (
                sales_month
                + INTERVAL '1 month'
                - INTERVAL '1 day'
            )::DATE
        ) AS is_complete_month

    FROM monthly_sales

)

SELECT *
FROM final