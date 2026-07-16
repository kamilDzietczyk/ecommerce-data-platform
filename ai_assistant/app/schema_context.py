MARTS_SCHEMA_CONTEXT = """
Available analytical tables:

1. marts.mart_daily_sales
Columns:
- sales_date
- total_orders
- total_revenue
- average_order_value

2. marts.mart_product_sales
Columns:
- product_id
- product_name
- category
- total_quantity
- total_sales

3. marts.mart_customer_value
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

6. marts.fct_orders
Columns:
- order_id
- customer_id
- order_date
- order_status
- total_amount

7. marts.fct_order_items
Columns:
- order_item_id
- order_id
- product_id
- quantity
- unit_price
- line_total
"""