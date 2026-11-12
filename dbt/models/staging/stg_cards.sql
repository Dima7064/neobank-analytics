{{ config(materialized='view') }}

SELECT
    toUInt64(card_id) AS card_id,
    toUInt64(client_id) AS client_id,
    card_type,
    toDateTime(issued_at) AS issued_at,
    toDateTimeOrNull(activated_at) AS activated_at,
    status
FROM {{ source('raw', 'raw_cards') }}
