WITH source AS (

    SELECT *
    FROM {{ ref('stg_order_items') }}

),

final AS (

    SELECT

        order_item_id,

        order_id,

        product_id,

        quantity,

        unit_price,

        quantity * unit_price AS line_total

    FROM source

)

SELECT *
FROM final