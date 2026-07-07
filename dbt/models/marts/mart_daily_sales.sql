WITH orders AS (

    SELECT *
    FROM {{ ref('fct_orders') }}

)

SELECT

    order_date::DATE AS sales_date,

    COUNT(order_id) AS total_orders,

    SUM(total_amount) AS total_revenue,

    AVG(total_amount) AS average_order_value

FROM orders

GROUP BY order_date::DATE