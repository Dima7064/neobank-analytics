{{ config(materialized='view') }}

SELECT
    toUInt64(tx_id) AS tx_id,
    toUInt64(client_id) AS client_id,
    toUInt64(tx_id) AS account_id, -- В raw не сохраняли account_id, используем tx_id для заглушки
    -- Очистка суммы от пробелов "1 500"
    toFloat64OrZero(replaceAll(toString(amount), ' ', '')) AS amount,
    tx_type,
    category,
    status,
    -- Конвертация флага
    if(toString(is_fraud) = 'True', 1, 0) AS is_fraud,
    -- Обработка часовых поясов (если нужно, оставляем как есть в UTC)
    toDateTime(tx_at) AS tx_at,
    toDate(toDateTime(tx_at)) AS tx_date
FROM {{ source('raw', 'raw_transactions') }}
WHERE toString(amount) NOT LIKE '%None%' OR amount IS NOT NULL
