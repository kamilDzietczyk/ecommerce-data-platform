CREATE SCHEMA IF NOT EXISTS raw;

-- CUSTOMERS

CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id         INTEGER,
    first_name          TEXT,
    last_name           TEXT,
    email               TEXT,
    country             TEXT,
    city                TEXT,
    created_at          TIMESTAMP,

    source_system       TEXT,
    ingested_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pipeline_run_id     TEXT
);

-- PRODUCTS

CREATE TABLE IF NOT EXISTS raw.products (
    product_id          INTEGER,
    product_name        TEXT,
    category            TEXT,
    price               NUMERIC(10,2),
    stock_quantity      INTEGER,
    created_at          TIMESTAMP,

    source_system       TEXT,
    ingested_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pipeline_run_id     TEXT
);

-- ORDERS

CREATE TABLE IF NOT EXISTS raw.orders (
    order_id            INTEGER,
    customer_id         INTEGER,
    order_date          TIMESTAMP,
    order_status        TEXT,
    total_amount        NUMERIC(10,2),

    source_system       TEXT,
    ingested_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pipeline_run_id     TEXT
);

-- ORDER ITEMS

CREATE TABLE IF NOT EXISTS raw.order_items (
    order_item_id       INTEGER,
    order_id            INTEGER,
    product_id          INTEGER,
    quantity            INTEGER,
    unit_price          NUMERIC(10,2),

    source_system       TEXT,
    ingested_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pipeline_run_id     TEXT
);

-- PAYMENTS

CREATE TABLE IF NOT EXISTS raw.payments (
    payment_id          INTEGER,
    order_id            INTEGER,
    payment_method      TEXT,
    payment_status      TEXT,
    payment_date        TIMESTAMP,
    payment_amount      NUMERIC(10,2),

    source_system       TEXT,
    ingested_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pipeline_run_id     TEXT
);

-- SHIPMENTS

CREATE TABLE IF NOT EXISTS raw.shipments (
    shipment_id         INTEGER,
    order_id            INTEGER,
    shipment_status     TEXT,
    shipment_provider   TEXT,
    shipped_date        TIMESTAMP,
    delivered_date      TIMESTAMP,

    source_system       TEXT,
    ingested_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    pipeline_run_id     TEXT
);