SELECT

    shipment_id,

    order_id,

    CASE
        WHEN LOWER(TRIM(shipment_status)) = 'processing' THEN 'processing'
        WHEN LOWER(TRIM(shipment_status)) = 'shipped' THEN 'shipped'
        WHEN LOWER(TRIM(shipment_status)) = 'delivered' THEN 'delivered'
        WHEN LOWER(TRIM(shipment_status)) = 'cancelled' THEN 'cancelled'
        ELSE 'unknown'
    END AS shipment_status,

    TRIM(shipment_provider) AS shipment_provider,

    shipped_date,

    delivered_date,

    source_system,

    ingested_at,

    pipeline_run_id

FROM {{ source('raw', 'shipments') }}