{{ config(materialized='table') }}

SELECT
    client_id,
    count(product_id) AS products_count,
    groupArray(product_type) AS product_types
FROM {{ ref('stg_products') }}
WHERE status = 'active'
GROUP BY client_id
