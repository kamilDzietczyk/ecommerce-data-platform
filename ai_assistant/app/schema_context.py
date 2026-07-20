MARTS_SCHEMA_CONTEXT = """
Available PostgreSQL analytical tables:

1. marts.mart_daily_sales
Purpose:
- Historical daily sales aggregated for the entire store.

Columns:
- sales_date: date of sales
- total_orders: number of orders
- total_revenue: total revenue
- average_order_value: average order value

2. marts.mart_product_sales
Purpose:
- Historical sales aggregated by product.

Columns:
- product_id
- product_name
- category
- total_quantity
- total_sales

3. marts.mart_customer_value
Purpose:
- Historical customer value aggregated by customer.

Columns:
- customer_id
- first_name
- last_name
- country
- city
- total_orders
- lifetime_value
- average_order_value

4. marts.dim_customers
Columns:
- customer_id
- first_name
- last_name
- email
- country
- city
- created_at

5. marts.dim_products
Columns:
- product_id
- product_name
- category
- price
- stock_quantity
- created_at

6. marts.dim_dates
Columns:
- date_day
- year
- month
- month_name
- day
- quarter
- week
- is_weekend

7. marts.fct_orders
Grain:
- One row represents one order.

Columns:
- order_id
- customer_id
- order_date
- order_status
- total_amount

8. marts.fct_order_items
Grain:
- One row represents one order item.

Columns:
- order_item_id
- order_id
- product_id
- quantity
- unit_price
- line_total

Relationships:
- marts.fct_orders.customer_id = marts.dim_customers.customer_id
- marts.fct_order_items.order_id = marts.fct_orders.order_id
- marts.fct_order_items.product_id = marts.dim_products.product_id

Important rules:
- order_date exists only in marts.fct_orders.
- sales_date exists only in marts.mart_daily_sales.
- marts.fct_order_items does not contain order_date.
- Use marts.mart_product_sales for aggregated product sales without a date filter.
- For product sales filtered by date, join:
  marts.fct_order_items
  → marts.fct_orders using order_id
  → marts.dim_products using product_id.
- Use marts.mart_daily_sales for historical total sales over time.
- Use only columns explicitly listed above.
- Forecasting data is not available yet.
- Current tables support historical analytics only.

Canonical pattern for product sales filtered by order date:

SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(oi.quantity) AS total_quantity,
    SUM(oi.line_total) AS total_sales
FROM marts.fct_order_items AS oi
JOIN marts.fct_orders AS o
    ON o.order_id = oi.order_id
JOIN marts.dim_products AS p
    ON p.product_id = oi.product_id
WHERE o.order_date >= DATE '2025-01-01'
  AND o.order_date < DATE '2025-02-01'
GROUP BY
    p.product_id,
    p.product_name,
    p.category
ORDER BY total_sales DESC
LIMIT 50

Adapt the date range to the user's question.
Never use oi.order_date because order_date belongs only to fct_orders.
"""