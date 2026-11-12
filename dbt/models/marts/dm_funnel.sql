{{ config(materialized='table') }}

WITH client_events AS (
    SELECT
        client_id,
        groupUniqArray(event_type) AS event_types,
        minIf(event_at, event_type = 'registration') AS reg_at,
        minIf(event_at, event_type = 'verification') AS ver_at,
        minIf(event_at, event_type = 'transaction') AS tx_at,
        minIf(event_at, event_type = 'open_product') AS prod_at
    FROM {{ ref('stg_events') }}
    GROUP BY client_id
)
SELECT
    toDate(reg_at) AS reg_date,
    count(DISTINCT client_id) AS registered,
    countIf(ver_at IS NOT NULL) AS verified,
    countIf(tx_at IS NOT NULL) AS activated,
    countIf(prod_at IS NOT NULL) AS got_product
FROM client_events
GROUP BY reg_date
ORDER BY reg_date
