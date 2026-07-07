WITH items AS (

    SELECT *
    FROM {{ ref('fct_order_items') }}

),

products AS (

    SELECT *
    FROM {{ ref('dim_products') }}

)

SELECT

    p.product_id,

    p.product_name,

    p.category,

    SUM(i.quantity) AS total_quantity,

    SUM(i.line_total) AS total_sales

FROM items i

JOIN products p
    ON i.product_id = p.product_id

GROUP BY

    p.product_id,
    p.product_name,
    p.category