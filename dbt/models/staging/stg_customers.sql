SELECT

    customer_id,

    TRIM(first_name) AS first_name,

    TRIM(last_name) AS last_name,

    LOWER(TRIM(email)) AS email,

    TRIM(country) AS country,

    TRIM(city) AS city,

    created_at,

    source_system,

    ingested_at,

    pipeline_run_id

FROM {{ source('raw', 'customers') }}