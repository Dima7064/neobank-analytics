
{{ config(materialized='view') }}

SELECT
    toUInt64(client_product_id) AS client_product_id,
    toUInt64(client_id) AS client_id,
    toUInt32(product_id) AS product_id,
    product_type,
    toDateTime(opened_at) AS opened_at,
    toDateTimeOrNull(closed_at) AS closed_at,
    toFloat64OrZero(amount) AS amount,
    status
FROM {{ source('raw', 'raw_products') }}