
{{ config(materialized='view') }}

SELECT
    toUInt64(fraud_id) AS fraud_id,
    toUInt64(tx_id) AS tx_id,
    toUInt64(client_id) AS client_id,
    toDateTime(detected_at) AS detected_at,
    fraud_type,
    toFloat64OrZero(amount) AS amount,
    if(lower(toString(confirmed)) IN ('true', '1', 't'), 1, 0) AS is_confirmed
FROM {{ source('raw', 'raw_fraud') }}