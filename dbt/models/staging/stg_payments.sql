SELECT

    payment_id,

    order_id,

    LOWER(TRIM(payment_method)) AS payment_method,

    CASE
        WHEN LOWER(TRIM(payment_status)) = 'paid' THEN 'paid'
        WHEN LOWER(TRIM(payment_status)) = 'pending' THEN 'pending'
        WHEN LOWER(TRIM(payment_status)) = 'failed' THEN 'failed'
        WHEN LOWER(TRIM(payment_status)) = 'refunded' THEN 'refunded'
        ELSE 'unknown'
    END AS payment_status,

    payment_date,

    payment_amount::NUMERIC(12,2) AS payment_amount,

    source_system,

    ingested_at,

    pipeline_run_id

FROM {{ source('raw', 'payments') }}