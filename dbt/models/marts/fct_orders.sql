WITH source AS (

    SELECT *
    FROM {{ ref('stg_orders') }}

),

final AS (

    SELECT

        order_id,

        customer_id,

        order_date,

        order_status,

        total_amount

    FROM source

)

SELECT *
FROM final