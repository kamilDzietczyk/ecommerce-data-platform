SELECT

    product_id,

    TRIM(product_name) AS product_name,

    TRIM(category) AS category,

    price::NUMERIC(10,2) AS price,

    stock_quantity::INTEGER AS stock_quantity,

    created_at,

    source_system,

    ingested_at,

    pipeline_run_id

FROM {{ source('raw', 'products') }}