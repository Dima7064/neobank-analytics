{{ config(materialized='view') }}

SELECT
    toUInt64(account_id) AS account_id,
    toUInt64(client_id) AS client_id,
    account_type,
    toDateTime(opened_at) AS opened_at,
    toDateTimeOrNull(closed_at) AS closed_at,
    toFloat64OrZero(balance) AS balance,
    status
FROM {{ source('raw', 'raw_accounts') }}
