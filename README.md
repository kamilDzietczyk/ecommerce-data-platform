# Ecommerce Data Platform

End-to-end Data Engineering project for ecommerce analytics.

The project demonstrates a complete local data platform using Docker, PostgreSQL, Python ingestion, dbt transformations, Airflow orchestration and Metabase dashboards.


## Tech Stack

- Python
- PostgreSQL
- Docker / Docker Compose
- dbt
- Apache Airflow
- Metabase
- pgAdmin

## Data Flow

### 1. Data generation

Synthetic ecommerce datasets are generated as CSV files:

- customers
- products
- orders
- order_items
- payments
- shipments

### 2. Ingestion

Python ingestion pipelines load CSV files into PostgreSQL RAW tables.

RAW tables keep source-like data and include technical metadata:

- source_system
- ingested_at
- pipeline_run_id

### 3. dbt transformations

dbt builds analytical layers:

```text
RAW → STAGING → MARTS
```

STAGING models clean and standardize raw data.

MARTS models contain business-ready tables:

- dim_customers
- dim_products
- dim_dates
- fct_orders
- fct_order_items
- mart_daily_sales
- mart_product_sales
- mart_customer_value

### 4. Orchestration

Airflow orchestrates the full pipeline:

```text
ingest_raw_data
→ dbt_run
→ dbt_test
→ dbt_docs_generate
```

### 5. Analytics

Metabase connects to PostgreSQL and visualizes MARTS tables.

Example dashboards:

- Daily revenue
- Revenue by category
- Top products
- Top customers by lifetime value


## How to Run

### 1. Start containers

```bash
docker compose up -d --build
```

### 2. Run database migration

Execute:

```sql
sql/migrations/001_create_raw_tables.sql
```

inside PostgreSQL / pgAdmin.

### 3. Run ingestion manually

```bash
docker exec -it ecommerce_ingestion python -m ingestion.pipelines.run_all_ingestion
```

### 4. Run dbt manually

```bash
docker exec -it ecommerce_dbt bash
```

Inside container:

```bash
dbt run --profiles-dir .
dbt test --profiles-dir .
dbt docs generate --profiles-dir .
```

To serve dbt documentation:

```bash
dbt docs serve --profiles-dir . --host 0.0.0.0 --port 8085
```

Open:

```text
http://localhost:8085
```

### 5. Run Airflow pipeline

Open Airflow:

```text
http://localhost:8086
```

Credentials:

```text
login: login_airflow
password: login_airflow
```

Trigger DAG:

```text
ecommerce_data_pipeline
```

### 6. Open Metabase

Open:

```text
http://localhost:3000
```

PostgreSQL connection from Metabase:

```text
Host: postgres
Port: 5432
Database: value from POSTGRES_DB
Username: value from POSTGRES_USER
Password: value from POSTGRES_PASSWORD
```

## Useful Ports

| Service | URL |
|---|---|
| PostgreSQL | localhost:5433 |
| pgAdmin | http://localhost:8084 |
| dbt docs | http://localhost:8085 |
| Airflow | http://localhost:8086 |
| Metabase | http://localhost:3000 |

## Example Analytics Queries

### Daily Sales

```sql
SELECT
    sales_date,
    total_revenue,
    total_orders,
    average_order_value
FROM marts.mart_daily_sales
ORDER BY sales_date;
```

### Revenue by Category

```sql
SELECT
    category,
    SUM(total_sales) AS total_sales
FROM marts.mart_product_sales
GROUP BY category
ORDER BY total_sales DESC;
```

### Top Products

```sql
SELECT
    product_name,
    category,
    total_quantity,
    total_sales
FROM marts.mart_product_sales
ORDER BY total_sales DESC
LIMIT 10;
```

### Top Customers

```sql
SELECT
    customer_id,
    first_name,
    last_name,
    country,
    city,
    total_orders,
    lifetime_value,
    average_order_value
FROM marts.mart_customer_value
ORDER BY lifetime_value DESC
LIMIT 10;
```

## Data Quality

The project includes dbt tests for:

- primary business keys
- not null checks
- relationships between facts and dimensions

Example:

```bash
dbt test --profiles-dir .
```

## Notes

Metabase dashboards are configured manually in the UI and stored in Docker volume.

This project is designed as a local portfolio Data Engineering platform.