{{ config(materialized='view') }}

SELECT
    toUInt64(event_id) AS event_id,
    toUInt64(client_id) AS client_id,
    event_type,
    toDateTime(event_at) AS event_at,
    toDate(event_at) AS event_date
FROM {{ source('raw', 'raw_events') }}
