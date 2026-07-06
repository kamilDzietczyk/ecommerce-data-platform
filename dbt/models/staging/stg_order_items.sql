SELECT

    order_item_id,

    order_id,

    product_id,

    quantity::INTEGER AS quantity,

    unit_price::NUMERIC(10,2) AS unit_price,

    source_system,

    ingested_at,

    pipeline_run_id

FROM {{ source('raw', 'order_items') }}