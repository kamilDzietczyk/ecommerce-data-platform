WITH source AS (

    SELECT *
    FROM {{ ref('stg_customers') }}

),

final AS (

    SELECT

        customer_id,

        first_name,

        last_name,

        email,

        country,

        city,

        created_at

    FROM source

)

SELECT *
FROM final