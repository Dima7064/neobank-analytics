
{{ config(materialized='view') }}

SELECT
    toUInt64(tx_id) AS tx_id,
    toUInt64(client_id) AS client_id,
    toUInt64(tx_id) AS account_id,
    toFloat64OrZero(replaceAll(toString(amount), ' ', '')) AS amount,
    tx_type,
    category,
    status,
    -- Исправленная проверка: ловим и 'True', и 'true', и '1'
    if(lower(toString(is_fraud)) IN ('true', '1', 't'), 1, 0) AS is_fraud,
    toDateTime(tx_at) AS tx_at,
    toDate(toDateTime(tx_at)) AS tx_date
FROM {{ source('raw', 'raw_transactions') }}