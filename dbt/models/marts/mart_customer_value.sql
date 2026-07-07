WITH orders AS (

    SELECT *
    FROM {{ ref('fct_orders') }}

),

customers AS (

    SELECT *
    FROM {{ ref('dim_customers') }}

)

SELECT

    c.customer_id,

    c.first_name,

    c.last_name,

    c.country,

    c.city,

    COUNT(o.order_id) AS total_orders,

    SUM(o.total_amount) AS lifetime_value,

    AVG(o.total_amount) AS average_order_value

FROM customers c

JOIN orders o
    ON c.customer_id = o.customer_id

GROUP BY

    c.customer_id,
    c.first_name,
    c.last_name,
    c.country,
    c.city