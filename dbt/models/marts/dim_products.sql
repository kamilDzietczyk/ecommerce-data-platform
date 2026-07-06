WITH source AS (

    SELECT *
    FROM {{ ref('stg_products') }}

),

final AS (

    SELECT

        product_id,
        product_name,
        category,
        price,
        stock_quantity,
        created_at

    FROM source

)

SELECT *
FROM final