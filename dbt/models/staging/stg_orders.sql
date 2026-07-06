SELECT

    order_id,

    customer_id,

    order_date,

    LOWER(TRIM(order_status)) AS order_status,

    total_amount::NUMERIC(12,2) AS total_amount,

    source_system,

    ingested_at,

    pipeline_run_id

FROM {{ source('raw', 'orders') }}